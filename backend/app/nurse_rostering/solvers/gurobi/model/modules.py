import abc
from datetime import timedelta

import gurobipy as gp
from gurobipy import GRB
from nurse_rostering.data_schema import NurseRosteringInstance, Shift
from .nurse_vars import NurseDecisionVars, PreferredCoverDecisionVars, NurseWorksAtWeekendVars
from nurse_rostering.utils.data_utils import group_shifts_by_date, get_weekends

class ShiftAssignmentModule(abc.ABC):
    @abc.abstractmethod
    def build(
        self,
        instance: NurseRosteringInstance,
        model: gp.Model,
        nurse_shift_vars: list[NurseDecisionVars],
    ) -> gp.LinExpr:
        """
        Add constraints and optionally return a sub-objective expression.
        Eac1h subclass defines one constraint or objective aspect.
        """
        return 0


class NoBlockedShiftsModule(ShiftAssignmentModule):
    """
    Prohibit assignment to blocked shifts. 
    """

    def enforce_for_nurse(self, model: gp.Model, nurse_x: NurseDecisionVars):
        for shift_uid in nurse_x.nurse.blocked_shifts:
            # prohibit assignment to blocked shifts
            model.addConstr(nurse_x.is_assigned_to(shift_uid) == 0)

    def build(
        self,
        instance: NurseRosteringInstance,
        model: gp.Model,
        nurse_shift_vars: list[NurseDecisionVars],
    ) -> gp.LinExpr:
        for nurse_x in nurse_shift_vars:
            self.enforce_for_nurse(model, nurse_x)
        return 0


class DemandSatisfactionModule(ShiftAssignmentModule):
    def build(self, instance, model, nurse_shift_vars):
        """
        Ensure each shift meets its demand. Similar to 10th constraint CoverRequirementsModule in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf
        """
        for shift in instance.shifts:
            assigned = [
                nv.is_assigned_to(shift.uid)
                for nv in nurse_shift_vars
                if shift.uid in nv._x
            ]
            model.addConstr(gp.quicksum(assigned) >= shift.demand)
        return 0


class MinTimeBetweenShifts(ShiftAssignmentModule):
    
    """2nd constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    
    def enforce_for_nurse(self, model: gp.Model, nurse_x: NurseDecisionVars):
        min_time_between_shifts = nurse_x.nurse.min_time_between_shifts
        for i in range(len(nurse_x.shifts) - 1):
            shift_i = nurse_x.shifts[i]
            colliding: list[Shift] = []  # shifts that are too close to shift_i
            for j in range(i + 1, len(nurse_x.shifts)):
                shift_j = nurse_x.shifts[j]
                if shift_i.end_time + min_time_between_shifts <= shift_j.start_time:
                    # Since shifts are sorted by start time, if the current shift_j starts
                    # after the required rest period, all subsequent shifts will also be valid.
                    # Therefore, we can safely break here to avoid unnecessary checks.
                    break
                colliding.append(shift_j)
            if colliding:
                # if there are shifts that are too close to shift_i,
                # prevent their assignment if shift_i is assigned
                shift_i_selected = nurse_x.is_assigned_to(shift_i.uid)
                model.addConstr(gp.quicksum(nurse_x.is_assigned_to(s.uid) for s in colliding) <= ((1 - shift_i_selected) * len(colliding))) # use big M constraint to only enforce when shift i is selected

    def build(self, instance, model, nurse_shift_vars):
        """
        Enforce minimum rest time between any two shifts for a nurse.
        """
        for nv in nurse_shift_vars:
            self.enforce_for_nurse(model, nv)
        return 0  # no objective contribution


class MaximizePreferences(ShiftAssignmentModule):
    def build(self, instance, model, nurse_shift_vars):
        """
        Encourage assigning nurses to their preferred shifts.
        Each preference counts negatively toward the minimization objective.
        """
        expr = 0
        for nv in nurse_shift_vars:
            for uid in nv.nurse.preferred_shifts:
                expr += -nv.nurse.preferred_shift_weight * nv.is_assigned_to(uid)
        return expr


class PreferStaffModule(ShiftAssignmentModule):
    def build(self, instance, model, nurse_shift_vars):
        """
        Penalize use of non-staff (contract) nurses in the objective.
        """
        expr = 0
        for nv in nurse_shift_vars:
            if not nv.nurse.staff:
                for uid in nv._x:
                    expr += instance.staff_weight * nv.is_assigned_to(uid)
        return expr


class LimitWorkTimeModule(ShiftAssignmentModule):
    """4th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    def build(self, instance, model, nurse_shift_vars):
        for nv in nurse_shift_vars:
            min_time = nv.nurse.minimum_work_time
            max_time = nv.nurse.maximum_work_time
            if min_time is None and max_time is None:
                continue
            working_time = 0
            for shift, var in nv.iter_shifts():
                working_time += (shift.end_time - shift.start_time) * var
            if min_time is not None:
                model.addConstr(working_time >= min_time)
            if max_time is not None:
                model.addConstr(working_time <= max_time)
        return 0

class MaximumConsecutiveShiftsModule(ShiftAssignmentModule):
    """5th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    def build(self, instance, model, nurse_shift_vars):
        # shifts grouped by date
        shifts_by_date = {}
        for shift in instance.shifts:
            current_date = shift.start_time.date()
            end_date = shift.end_time.date()
            while current_date <= end_date:
                shifts_by_date.setdefault(current_date, []).append(shift.uid)
                current_date += timedelta(days=1)

        min_date = instance.shifts[0].start_time.date()
        max_date = instance.shifts[-1].end_time.date()

        all_dates = []
        current_date = min_date
        while current_date <= max_date:
            all_dates.append(current_date)
            current_date += timedelta(days=1)
        if not all_dates:
            return 0
        for nv in nurse_shift_vars:
            # decision variable if nurse works at date x
            max_shifts = nv.nurse.maximum_consecutive_shifts
            if max_shifts is None:
                continue
            work_day = []
            for date in all_dates:
                w = model.addVar(vtype=GRB.BINARY, name=f"work_{nv.nurse.uid}_{date.isoformat()}")
                work_day.append(w)
                uids = shifts_by_date.get(date, [])
                vars_for_date = [nv.is_assigned_to(uid) for uid in uids]
                if not vars_for_date:
                    model.addConstr(w == 0)
                else:
                    model.addConstr(w <= gp.quicksum(vars_for_date))

            for i in range(len(work_day)-max_shifts):
                model.addConstr(gp.quicksum(work_day[i:i+max_shifts+1]) <= max_shifts)

        return 0


class MinimumConsecutiveShiftsModule(ShiftAssignmentModule):
    """6th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    def build(self, instance, model, nurse_shift_vars):
        shifts_by_date = group_shifts_by_date(instance)
        all_dates = sorted(shifts_by_date.keys())
        if not all_dates:
            return 0
        for nv in nurse_shift_vars:
            min_shifts = nv.nurse.minimum_consecutive_shifts
            if min_shifts is None:
                continue
            for s in range(1, min_shifts):
                for d in range(0, len(all_dates)-(s+1)):
                    shifts_in_range = []
                    for i in range(d+1, d+s+1):
                        shifts_in_range += shifts_by_date[all_dates[i]]
                    model.addConstr(gp.quicksum(nv.is_assigned_to(shift) for shift in shifts_by_date[all_dates[d]]) + (s - gp.quicksum(nv.is_assigned_to(shift) for shift in shifts_in_range)) + gp.quicksum(nv.is_assigned_to(shift) for shift in shifts_by_date[all_dates[d+s+1]]) >= 1)
        return 0    

class MinimumConsecutiveDaysOffModule(ShiftAssignmentModule):
    """7th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    def build(self, instance, model, nurse_shift_vars):
        shifts_by_date = group_shifts_by_date(instance)
        all_dates = sorted(shifts_by_date.keys())
        if not all_dates:
            return 0
        for nv in nurse_shift_vars:
            min_days_off = nv.nurse.minimum_consecutive_days_off
            if min_days_off is None:
                continue
            for s in range(1, min_days_off):
                for d in range(0, len(all_dates) - (s + 1)):
                    shifts_in_range = []
                    for i in range(d + 1, d + s + 1):
                        shifts_in_range += shifts_by_date[all_dates[i]]
                    model.addConstr((1 - gp.quicksum(nv.is_assigned_to(shift) for shift in shifts_by_date[all_dates[d]])) + gp.quicksum(nv.is_assigned_to(shift) for shift in shifts_in_range) + (1 - gp.quicksum(
                        nv.is_assigned_to(shift) for shift in shifts_by_date[all_dates[d + s + 1]])) >= 1)
        return 0

class MaxmimumNumberOfWeekendsModule(ShiftAssignmentModule):
    """8th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    def build(self, instance, model, nurse_shift_vars):
        shifts_by_date = group_shifts_by_date(instance)
        all_weekend_vars = []
        weekends = get_weekends(instance)
        for nv in nurse_shift_vars:
            nurse = nv.nurse
            max_weekends = nurse.maximum_weekends
            if max_weekends is None:
                continue
            weekend_vars = NurseWorksAtWeekendVars(nv, weekends, shifts_by_date, model)
            all_weekend_vars.append(weekend_vars)
            model.add(sum(weekend_vars.is_assigned_to(weekend) for weekend in weekends) <= max_weekends)

        return 0
    
class DaysOffModule(ShiftAssignmentModule):
    """9th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf
        Possibly already enforced by NoBlockedShiftsModule"""
    def build(self, instance, model, nurse_shift_vars):
        shifts_by_date = group_shifts_by_date(instance)
        for nv in nurse_shift_vars:
            days_off = nv.nurse.days_off
            if days_off is None:
                continue
            for day in days_off:
                shifts_on_day = shifts_by_date.get(day, [])
                if not shifts_on_day:
                    continue
                model.addConstr(gp.quicksum(nv.is_assigned_to(shift) for shift in shifts_on_day) == 0)
        return 0
    
    
class CoverRequirementsModule(ShiftAssignmentModule):
    """10th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    def build(self, instance, model, nurse_shift_vars):
        shift_by_uid = {shift.uid: shift for shift in instance.shifts}
        shifts_by_date = group_shifts_by_date(instance)
        preferred_cover_vars = PreferredCoverDecisionVars(shifts=instance.shifts, model=model)
        expr = 0
        for date, shifts in shifts_by_date.items():
            for shift_uid in shifts:
                assigned_nurses = gp.quicksum([nv.is_assigned_to(shift_uid) for nv in nurse_shift_vars if shift_uid in nv._x])
                model.addConstr(
                    assigned_nurses + preferred_cover_vars.total_above_preferred[shift_uid] - preferred_cover_vars.total_below_preferred[shift_uid]
                    == 
                    shift_by_uid[shift_uid].demand
                )
                
                expr += shift_by_uid[shift_uid].weight_below_demand * preferred_cover_vars.total_below_preferred[shift_uid]
                expr += shift_by_uid[shift_uid].weight_above_demand * preferred_cover_vars.total_above_preferred[shift_uid]
        
        return expr


import abc
from datetime import timedelta

import gurobipy as gp
from gurobipy import GRB

from nurse_rostering.data_schema import NurseRosteringInstance
from nurse_rostering.utils.data_utils import group_shifts_by_date, get_shift_type_dict

from .nurse_vars import NurseDecisionVars, PreferredCoverDecisionVars, NurseWorksAtWeekendVars


class ShiftAssignmentModule(abc.ABC):
    @abc.abstractmethod
    def build(
        self,
        instance: NurseRosteringInstance,
        model: gp.Model,
        nurse_shift_vars: list[NurseDecisionVars],
    ):
        """
        Add constraints and optionally return a (linear) objective term.
        """
        return gp.LinExpr()


class NoBlockedShiftsModule(ShiftAssignmentModule):
    """
    Prohibit assignment to blocked shifts.
    """
    def enforce_for_nurse(self, model: gp.Model, nurse_x: NurseDecisionVars):
        for shift_uid in nurse_x.nurse.blocked_shifts:
            model.addConstr(nurse_x.is_assigned_to(shift_uid) == 0, name=f"blocked_{nurse_x.nurse.uid}_{shift_uid}")

    def build(self, instance, model, nurse_shift_vars):
        for nurse_x in nurse_shift_vars:
            self.enforce_for_nurse(model, nurse_x)
        return gp.LinExpr()


class OneShiftPerDayModule(ShiftAssignmentModule):
    """1st constraint from paper"""
    def build(self, instance, model, nurse_shift_vars):
        """
        Enforce that each nurse works at most one shift per day.
        """
        shifts_by_date = group_shifts_by_date(instance)
        for nv in nurse_shift_vars:
            for date, shift_uids in shifts_by_date.items():
                vars_for_date = [nv.is_assigned_to(uid) for uid in shift_uids if uid in nv._x]
                if len(vars_for_date) > 1:
                    model.addConstr(gp.quicksum(vars_for_date) <= 1, name=f"one_shift_per_day_{nv.nurse.uid}_{date.isoformat()}")
        return gp.LinExpr()


class MinTimeBetweenShifts(ShiftAssignmentModule):
    """2nd constraint from paper"""
    def build(self, instance, model, nurse_shift_vars):
        """
        Enforce minimum rest time between any two shifts for a nurse.
        """
        shift_by_uid = {shift.uid: shift for shift in instance.shifts}
        shift_type_dict = get_shift_type_dict(instance)
        shifts_by_date = group_shifts_by_date(instance)
        all_dates = sorted(shifts_by_date.keys())
        if not all_dates:
            return gp.LinExpr()

        for nv in nurse_shift_vars:
            for i in range(len(all_dates) - 1):
                day_shifts = shifts_by_date.get(all_dates[i], [])
                following_day_shifts = shifts_by_date.get(all_dates[i] + timedelta(days=1), [])
                if not day_shifts or not following_day_shifts:
                    continue
                for day_shift in day_shifts:
                    types = shift_type_dict.get(day_shift, [])
                    if not types:
                        continue
                    for following_shift in following_day_shifts:
                        _type = shift_by_uid[following_shift].type
                        if _type is None:
                            continue
                        if _type in types:
                            model.addConstr(
                                nv.is_assigned_to(day_shift) + nv.is_assigned_to(following_shift) <= 1,
                                name=f"min_rest_{nv.nurse.uid}_{day_shift}_{following_shift}",
                            )
        return gp.LinExpr()


class MaximizePreferences(ShiftAssignmentModule):
    def build(self, instance, model, nurse_shift_vars):
        """
        Encourage assigning nurses to their preferred shifts.
        Each preference counts negatively toward the minimization objective.
        """
        expr = gp.LinExpr()
        for nv in nurse_shift_vars:
            for uid in nv.nurse.preferred_shifts:
                # negative weight -> encourages assignment in minimization
                expr += -int(nv.nurse.preferred_shift_weight) * nv.is_assigned_to(uid)
        return expr


class PreferStaffModule(ShiftAssignmentModule):
    def build(self, instance, model, nurse_shift_vars):
        """
        Penalize use of non-staff (contract) nurses in the objective.
        """
        expr = gp.LinExpr()
        for nv in nurse_shift_vars:
            if not nv.nurse.staff:
                for uid in nv._x:
                    expr += int(instance.staff_weight) * nv.is_assigned_to(uid)
        return expr


class LimitWorkTimeModule(ShiftAssignmentModule):
    """4th constraint of paper"""
    def build(self, instance, model, nurse_shift_vars):
        for nv in nurse_shift_vars:
            min_time = nv.nurse.minimum_work_time
            max_time = nv.nurse.maximum_work_time
            if min_time is None and max_time is None:
                continue

            working_time = gp.LinExpr()
            for shift, var in nv.iter_shifts():
                working_time += int(shift.length) * var

            if min_time is not None:
                model.addConstr(working_time >= int(min_time), name=f"min_work_{nv.nurse.uid}")
            if max_time is not None:
                model.addConstr(working_time <= int(max_time), name=f"max_work_{nv.nurse.uid}")

        return gp.LinExpr()


class MaximumConsecutiveShiftsModule(ShiftAssignmentModule):
    """5th constraint of paper"""
    def build(self, instance, model, nurse_shift_vars):
        shifts_by_date = group_shifts_by_date(instance)
        all_dates = sorted(shifts_by_date.keys())
        if not all_dates:
            return gp.LinExpr()

        for nv in nurse_shift_vars:
            max_shifts = nv.nurse.maximum_consecutive_shifts
            if max_shifts is None:
                continue
            max_shifts = int(max_shifts)
            for d in range(len(all_dates) - max_shifts):
                shifts_in_range = []
                for i in range(max_shifts + 1):
                    shifts_in_range += shifts_by_date[all_dates[d + i]]
                model.addConstr(
                    gp.quicksum(nv.is_assigned_to(shift_uid) for shift_uid in shifts_in_range) <= max_shifts,
                    name=f"max_consec_{nv.nurse.uid}_{d}",
                )

        return gp.LinExpr()


class MinimumConsecutiveShiftsModule(ShiftAssignmentModule):
    """6th constraint of paper"""
    def build(self, instance, model, nurse_shift_vars):
        shifts_by_date = group_shifts_by_date(instance)
        all_dates = sorted(shifts_by_date.keys())
        if not all_dates:
            return gp.LinExpr()

        for nv in nurse_shift_vars:
            min_shifts = nv.nurse.minimum_consecutive_shifts
            if min_shifts is None:
                continue
            min_shifts = int(min_shifts)
            for s in range(1, min_shifts):
                for d in range(0, len(all_dates) - (s + 1)):
                    shifts_in_range = []
                    for i in range(d + 1, d + s + 1):
                        shifts_in_range += shifts_by_date[all_dates[i]]

                    lhs = (
                        gp.quicksum(nv.is_assigned_to(shift_uid) for shift_uid in shifts_by_date[all_dates[d]])
                        + (s - gp.quicksum(nv.is_assigned_to(shift_uid) for shift_uid in shifts_in_range))
                        + gp.quicksum(nv.is_assigned_to(shift_uid) for shift_uid in shifts_by_date[all_dates[d + s + 1]])
                    )
                    model.addConstr(lhs >= 1, name=f"min_consec_shifts_{nv.nurse.uid}_{d}_{s}")

        return gp.LinExpr()


class MinimumConsecutiveDaysOffModule(ShiftAssignmentModule):
    """7th constraint of paper"""
    def build(self, instance, model, nurse_shift_vars):
        shifts_by_date = group_shifts_by_date(instance)
        all_dates = sorted(shifts_by_date.keys())
        if not all_dates:
            return gp.LinExpr()

        for nv in nurse_shift_vars:
            min_days_off = nv.nurse.minimum_consecutive_days_off
            if min_days_off is None:
                continue
            min_days_off = int(min_days_off)

            for s in range(1, min_days_off):
                for d in range(0, len(all_dates) - (s + 1)):
                    shifts_in_range = []
                    for i in range(d + 1, d + s + 1):
                        shifts_in_range += shifts_by_date[all_dates[i]]

                    lhs = (
                        (1 - gp.quicksum(nv.is_assigned_to(shift_uid) for shift_uid in shifts_by_date[all_dates[d]]))
                        + gp.quicksum(nv.is_assigned_to(shift_uid) for shift_uid in shifts_in_range)
                        + (1 - gp.quicksum(nv.is_assigned_to(shift_uid) for shift_uid in shifts_by_date[all_dates[d + s + 1]]))
                    )
                    model.addConstr(lhs >= 1, name=f"min_consec_days_off_{nv.nurse.uid}_{d}_{s}")

        return gp.LinExpr()


def get_weekends(instance):
    shifts_by_date = group_shifts_by_date(instance)
    all_dates = sorted(shifts_by_date.keys())
    if not all_dates:
        return []
    saturdays = [d for d in all_dates if d.weekday() == 5]
    return [(s, s + timedelta(days=1)) for s in saturdays]


class MaximumNumberOfWeekendsModule(ShiftAssignmentModule):
    """8th constraint of paper"""
    def build(self, instance, model, nurse_shift_vars):
        shifts_by_date = group_shifts_by_date(instance)
        weekends = get_weekends(instance)

        for nv in nurse_shift_vars:
            nurse = nv.nurse
            max_weekends = nurse.maximum_weekends
            if max_weekends is None:
                continue
            max_weekends = int(max_weekends)

            weekend_vars = NurseWorksAtWeekendVars(nv, weekends, shifts_by_date, model)
            model.addConstr(
                gp.quicksum(weekend_vars.is_assigned_to(weekend) for weekend in weekends) <= max_weekends,
                name=f"max_weekends_{nv.nurse.uid}",
            )

        return gp.LinExpr()

class DaysOffModule(ShiftAssignmentModule):
    """9th constraint of paper"""
    def build(self, instance, model, nurse_shift_vars):
        shifts_by_date = group_shifts_by_date(instance)

        for nv in nurse_shift_vars:
            days_off = nv.nurse.days_off
            if days_off is None:
                continue

            for day in days_off:
                shifts_on_day = shifts_by_date.get(day, [])
                if not shifts_on_day:
                    continue

                model.addConstr(
                    gp.quicksum(nv.is_assigned_to(shift_uid) for shift_uid in shifts_on_day) == 0,
                    name=f"day_off_{nv.nurse.uid}_{day.isoformat()}",
                )

        return gp.LinExpr()


class CoverRequirementsModule(ShiftAssignmentModule):
    """10th constraint of paper"""
    def build(self, instance, model, nurse_shift_vars):
        shift_by_uid = {shift.uid: shift for shift in instance.shifts}
        shifts_by_date = group_shifts_by_date(instance)

        preferred_cover_vars = PreferredCoverDecisionVars(shifts=instance.shifts, model=model)
        expr = gp.LinExpr()

        for date, shift_uids in shifts_by_date.items():
            for shift_uid in shift_uids:
                assigned_nurses = gp.quicksum(
                    nv.is_assigned_to(shift_uid) for nv in nurse_shift_vars if shift_uid in nv._x
                )

                model.addConstr(
                    assigned_nurses
                    + preferred_cover_vars.total_above_preferred[shift_uid]
                    - preferred_cover_vars.total_below_preferred[shift_uid]
                    == int(shift_by_uid[shift_uid].demand),
                    name=f"cover_{shift_uid}",
                )

                expr += int(shift_by_uid[shift_uid].weight_below_demand) * preferred_cover_vars.total_below_preferred[shift_uid]
                expr += int(shift_by_uid[shift_uid].weight_above_demand) * preferred_cover_vars.total_above_preferred[shift_uid]

        return expr
