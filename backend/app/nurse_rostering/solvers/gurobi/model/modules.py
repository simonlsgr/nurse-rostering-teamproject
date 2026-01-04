import abc
from datetime import timedelta

import gurobipy as gp
from gurobipy import GRB
from ...data_schema import NurseRosteringInstance, Shift
from .nurse_vars import NurseDecisionVars


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
        Each subclass defines one constraint or objective aspect.
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
        return 0
    

class MinimumConsecutiveDaysOffModule(ShiftAssignmentModule):
    """7th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    def build(self, instance, model, nurse_shift_vars):
        return 0

class MaxmimumNumberOfWeekendsModule(ShiftAssignmentModule):
    """8th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    def build(self, instance, model, nurse_shift_vars):
        return 0
    
class DaysOffModule(ShiftAssignmentModule):
    """9th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf
        Possibly already enforced by NoBlockedShiftsModule"""
    def build(self, instance, model, nurse_shift_vars):
        return 0
    
    
class CoverRequirementsModule(ShiftAssignmentModule):
    """10th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    def build(self, instance, model, nurse_shift_vars):
        return 0


