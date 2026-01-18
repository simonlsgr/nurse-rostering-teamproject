import abc
from datetime import timedelta
from typing import Any

from ortools.sat.python import cp_model
from nurse_rostering.data_schema import NurseRosteringInstance, Shift
from .nurse_vars import NurseDecisionVars, PreferredCoverDecisionVars, NurseWorksAtWeekendVars

from nurse_rostering.utils.data_utils import group_shifts_by_date, get_shift_type_dict
class ShiftAssignmentModule(abc.ABC):
    @abc.abstractmethod
    def build(
        self,
        instance: NurseRosteringInstance,
        model: cp_model.CpModel,
        nurse_shift_vars: list[NurseDecisionVars]
    ) -> cp_model.LinearExprT:
        """
        Add constraints and optionally return a sub-objective expression.
        Each subclass defines one constraint or objective aspect.
        """
        return 0

class NoBlockedShiftsModule(ShiftAssignmentModule):
    """
    Prohibit assignment to blocked shifts. 
    """

    def enforce_for_nurse(self, model: cp_model.CpModel, nurse_x: NurseDecisionVars):
        for shift_uid in nurse_x.nurse.blocked_shifts:
            # prohibit assignment to blocked shifts
            model.add(nurse_x.is_assigned_to(shift_uid) == 0)

    def build(
        self,
        instance: NurseRosteringInstance,
        model: cp_model.CpModel,
        nurse_shift_vars: list[NurseDecisionVars],
        preferred_shift_vars: PreferredCoverDecisionVars = None
    ) -> cp_model.LinearExprT:
        for nurse_x in nurse_shift_vars:
            self.enforce_for_nurse(model, nurse_x)
        return 0


# class DemandSatisfactionModule(ShiftAssignmentModule):
#     def build(self, instance, model, nurse_shift_vars, preferred_shift_vars: PreferredCoverDecisionVars = None):
#         """
#         Ensure each shift meets its demand. Similar to 10th constraint CoverRequirementsModule in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf
#         """
#         for shift in instance.shifts:
#             assigned = [
#                 nv.is_assigned_to(shift.uid)
#                 for nv in nurse_shift_vars
#                 if shift.uid in nv._x
#             ]
#             model.add(sum(assigned) >= shift.demand)
#         return 0

class OneShiftPerDayModule(ShiftAssignmentModule):
    """1st constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    
    def build(self, instance, model, nurse_shift_vars, preferred_shift_vars: PreferredCoverDecisionVars = None):
        """
        Enforce that each nurse works at most one shift per day.
        """
        shifts_by_date = group_shifts_by_date(instance)

        for nv in nurse_shift_vars:
            for date, shift_uids in shifts_by_date.items():
                vars_for_date = [nv.is_assigned_to(uid) for uid in shift_uids if uid in nv._x]
                if len(vars_for_date) > 1:
                    model.add(sum(vars_for_date) <= 1)
        return 0




class MinTimeBetweenShifts(ShiftAssignmentModule):
    
    """2nd constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    def build(self, instance, model, nurse_shift_vars):
        """
        Enforce minimum rest time between any two shifts for a nurse.
        """
        shift_by_uid = {shift.uid: shift for shift in instance.shifts}
        shift_type_dict = get_shift_type_dict(instance)
        shifts_by_date = group_shifts_by_date(instance)
        all_dates = sorted(shifts_by_date.keys())
        if not all_dates:
            return 0
        for nv in nurse_shift_vars:
            for i in range(len(all_dates)-1):
                day_shifts = shifts_by_date.get(all_dates[i], [])
                following_day_shifts = shifts_by_date.get(all_dates[i]+timedelta(days=1), [])
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
                            model.add(nv.is_assigned_to(day_shift) + nv.is_assigned_to(following_shift) <= 1)
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
                working_time += shift.length * var
            if min_time is not None:
                model.add(working_time >= min_time)
            if max_time is not None:
                model.add(working_time <= max_time)
        return 0


class MaximumConsecutiveShiftsModule(ShiftAssignmentModule):
    """5th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    def build(self, instance, model, nurse_shift_vars):

        shifts_by_date = group_shifts_by_date(instance)
        all_dates = sorted(shifts_by_date.keys())
        if not all_dates:
            return 0
        for nv in nurse_shift_vars:
            max_shifts = nv.nurse.maximum_consecutive_shifts
            if max_shifts is None:
                continue
            for d in range(len(all_dates) - max_shifts):
                shifts_in_range = []
                for i in range(max_shifts + 1):
                    shifts_in_range += shifts_by_date[all_dates[d + i]]
                model.add(sum(nv.is_assigned_to(shift) for shift in shifts_in_range) <= max_shifts)
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
                    model.add(sum(nv.is_assigned_to(shift) for shift in shifts_by_date[all_dates[d]]) + (s - sum(nv.is_assigned_to(shift) for shift in shifts_in_range)) + sum(nv.is_assigned_to(shift) for shift in shifts_by_date[all_dates[d+s+1]]) >= 1)
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
                    model.add((1 - sum(nv.is_assigned_to(shift) for shift in shifts_by_date[all_dates[d]])) + sum(nv.is_assigned_to(shift) for shift in shifts_in_range) + (1 - sum(
                        nv.is_assigned_to(shift) for shift in shifts_by_date[all_dates[d + s + 1]])) >= 1)
        return 0


def get_weekends(instance):
    shifts_by_date = group_shifts_by_date(instance)
    all_dates = sorted(shifts_by_date.keys())
    if not all_dates:
        return 0
    saturdays = []
    if all_dates[0].weekday() == 6:
        saturdays.append(all_dates[0]-timedelta(days=1))
    saturdays = [d for d in all_dates if d.weekday() == 5]
    return [(s, s+timedelta(days=1)) for s in saturdays]


class MaximumNumberOfWeekendsModule(ShiftAssignmentModule):
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
    """9th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
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
                model.add(sum(nv.is_assigned_to(shift) for shift in shifts_on_day) == 0)
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
                assigned_nurses = sum([nv.is_assigned_to(shift_uid) for nv in nurse_shift_vars if shift_uid in nv._x])
                model.add(
                    assigned_nurses + preferred_cover_vars.total_above_preferred[shift_uid] - preferred_cover_vars.total_below_preferred[shift_uid]
                    == 
                    shift_by_uid[shift_uid].demand
                )
                
                expr += shift_by_uid[shift_uid].weight_below_demand * preferred_cover_vars.total_below_preferred[shift_uid]
                expr += shift_by_uid[shift_uid].weight_above_demand * preferred_cover_vars.total_above_preferred[shift_uid]
        
        return expr

