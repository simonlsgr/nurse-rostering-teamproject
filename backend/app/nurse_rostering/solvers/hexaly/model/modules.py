import abc
from datetime import timedelta
from typing import Any

from hexaly.optimizer import HxModel, HxExpression

from nurse_rostering.data_schema import NurseRosteringInstance, Shift
from nurse_rostering.solvers.hexaly.model.nurse_vars import ShiftDecisionVars


class ShiftAssignmentModule(abc.ABC):
    @abc.abstractmethod
    def build(
        self,
        instance: NurseRosteringInstance,
        model: HxModel,
        shift_vars: list[ShiftDecisionVars],
    ) -> HxExpression:
        """
        Add constraints and optionally return a sub-objective expression.
        Each subclass defines one constraint or objective aspect.
        """
        return 0

class OneShiftPerDayModule(ShiftAssignmentModule):
    """1st constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    
    def build(self, instance, model, shift_vars):
        """
        Ensure each nurse is assigned to at most one shift per day.
        """
        shifts_by_day = {}
        for sv in shift_vars:
            day = sv.shift.start_time.date()
            shifts_by_day.setdefault(day, []).append(sv) 

        for day, svs in shifts_by_day.items():
            for nurse_index in range(len(sv.nurses)):
                model.add_constraint(
                    sum([model.contains(sv.nurses_assigned, nurse_index) for sv in svs]) <= 1
                )

        return 0

class ShiftRotationModule(ShiftAssignmentModule):
    """2nd constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    
    def build(self, instance, model, shift_vars):
        """
        Enforce minimum rest time between any two shifts for a nurse.
        """

        for sv in shift_vars:
            shift = sv.shift
            not_followed_by_types = getattr(shift, "not_followed_by_shift_types", set())
            if not not_followed_by_types:
                continue
            for other_sv in shift_vars:
                other_shift = other_sv.shift
                # if other shift is on the next day of shift do something
                if (
                    shift.start_time.date() + timedelta(days=1) == other_shift.start_time.date()
                    and
                    other_shift.type in not_followed_by_types
                    ):
                
                    model.add_constraint(
                        model.count(model.intersection(sv.nurses_assigned, other_sv.nurses_assigned)) == 0
                    )
                    
            
            
class MaximumShiftTypesModule(ShiftAssignmentModule):
    """3rd constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    
    def build(self, instance, model, shift_vars):
        """
        Ensure each nurse does not exceed maximum allowed shift types.
        """
        
        shift_vars_by_type = {}
        for sv in shift_vars:
            shift_type = sv.shift.type
            shift_vars_by_type.setdefault(shift_type, []).append(sv)
        
        for n_idx, nurse in enumerate(instance.nurses):
            for shift_type, svs in shift_vars_by_type.items():
                
                max_shifts = nurse.maximum_number_of_shifts_per_type.get(shift_type) if nurse.maximum_number_of_shifts_per_type else None
                print(max_shifts)
                if max_shifts is not None:
                    model.add_constraint(
                        sum([model.contains(sv.nurses_assigned, n_idx) for sv in svs]) <= max_shifts
                    )
                    
        return 0


class LimitWorkTimeModule(ShiftAssignmentModule):
    """4th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    def build(self, instance, model, shift_vars):
        for n_idx, nurse in enumerate(instance.nurses):
            min_time = nurse.minimum_work_time
            max_time = nurse.maximum_work_time
            if min_time is None and max_time is None:
                continue
            working_time = 0
            for sv in shift_vars:
                shift = sv.shift
                working_time += (shift.end_time - shift.start_time).total_seconds() / 60 * model.contains(sv.nurses_assigned, n_idx)
            if min_time is not None:
                model.add_constraint(working_time >= min_time)
            if max_time is not None:
                model.add_constraint(working_time <= max_time)
        return 0

class MaximumConsecutiveShiftsModule(ShiftAssignmentModule):
    """5th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    
        
    
    def build(self, instance, model, shift_vars):
        self.model = model
        intersections_by_length = {}
        shifts_by_date = {}
        for sv in shift_vars:
            date = sv.shift.start_time.date()
            shifts_by_date.setdefault(date, []).append(sv)
        
        
        shifts_by_date_union = {date: model.union([sv.nurses_assigned for sv in svs]) for date, svs in shifts_by_date.items()}
        
        all_dates = sorted(shifts_by_date.keys())
        for n_idx, nurse in enumerate(instance.nurses):
            max_shifts = nurse.maximum_consecutive_shifts
            if max_shifts is None:
                continue
            
            for i in range(len(all_dates)-max_shifts):
                date_block = all_dates[i:i+max_shifts+1]
                nurse_working_vars = [model.contains(shifts_by_date_union[date], n_idx) for date in date_block]
                self.model.add_constraint(sum(nurse_working_vars) <= max_shifts)
        return 0
            
                
            
                
            
                
            
            
            
            
        
        
# class NoBlockedShiftsModule(ShiftAssignmentModule):
#     """
#     Prohibit assignment to blocked shifts. 
#     """

#     def enforce_for_nurse(self, model: HxModel, nurse_x: NurseDecisionVars):
#         for shift_uid in nurse_x.nurse.blocked_shifts:
#             # prohibit assignment to blocked shifts
#             model.add_constraint(nurse_x.is_assigned_to(shift_uid) == 0)

#     def build(
#         self,
#         instance: NurseRosteringInstance,
#         model: HxModel,
#         nurse_shift_vars: list[NurseDecisionVars],
#     ) -> HxExpression:
#         for nurse_x in nurse_shift_vars:
#             self.enforce_for_nurse(model, nurse_x)
#         return 0


# # class DemandSatisfactionModule(ShiftAssignmentModule):
# #     def build(self, instance, model, nurse_shift_vars):
# #         """
# #         Ensure each shift meets its demand. Similar to 10th constraint CoverRequirementsModule in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf
# #         """
# #         for shift in instance.shifts:
# #             assigned = [
# #                 nv.is_assigned_to(shift.uid)
# #                 for nv in nurse_shift_vars
# #                 if shift.uid in nv._x
# #             ]
# #             model.add_constraint(sum(assigned) >= shift.demand)
# #         return 0


# class OneShiftPerDayModule(ShiftAssignmentModule):
#     """1st constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

#     def build(self, instance, model, nurse_shift_vars):
#         """
#         Ensure each nurse is assigned to at most one shift per day.
#         """
#         for nv in nurse_shift_vars:
#             shift_vars_by_date = {}
#             for shift in nv.shifts:
#                 day = shift.start_time.date()
#                 shift_vars_by_date.setdefault(day, []).append(
#                     nv.is_assigned_to(shift.uid)
#                 )

#             print(shift_vars_by_date)
#             day_blocks = model.array(a[0] for a in list(shift_vars_by_date.values()))
#             print(day_blocks)

#             model.constraint(model.partition(day_blocks))

#         return 0


# class MinTimeBetweenShifts(ShiftAssignmentModule):
#     """2nd constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

#     def enforce_for_nurse(self, model: HxModel, nurse_x: NurseDecisionVars):
#         min_time_between_shifts = nurse_x.nurse.min_time_between_shifts
#         for i in range(len(nurse_x.shifts) - 1):
#             shift_i = nurse_x.shifts[i]
#             colliding: list[Shift] = []  # shifts that are too close to shift_i
#             for j in range(i + 1, len(nurse_x.shifts)):
#                 shift_j = nurse_x.shifts[j]
#                 if shift_i.end_time + min_time_between_shifts <= shift_j.start_time:
#                     # Since shifts are sorted by start time, if the current shift_j starts
#                     # after the required rest period, all subsequent shifts will also be valid.
#                     # Therefore, we can safely break here to avoid unnecessary checks.
#                     break
#                 colliding.append(shift_j)
#             if colliding:
#                 # Ensure that if shift_i is assigned, none of the colliding shifts are assigned
#                 shift_i_selected = nurse_x.is_assigned_to(shift_i.uid)
#                 for shift_j in colliding:
#                     shift_j_selected = nurse_x.is_assigned_to(shift_j.uid)
#                     model.add_constraint(shift_i_selected + shift_j_selected <= 1)

#     def build(self, instance, model, nurse_shift_vars):
#         """
#         Enforce minimum rest time between any two shifts for a nurse.
#         """
#         for nv in nurse_shift_vars:
#             self.enforce_for_nurse(model, nv)
#         return 0  # no objective contribution


# class MaximizePreferences(ShiftAssignmentModule):
#     def build(self, instance, model, nurse_shift_vars):
#         """
#         Encourage assigning nurses to their preferred shifts.
#         Each preference counts negatively toward the minimization objective.
#         """
#         expr = 0
#         for nv in nurse_shift_vars:
#             for uid in nv.nurse.preferred_shifts:
#                 expr += -nv.nurse.preferred_shift_weight * nv.is_assigned_to(uid)
#         return expr


# class PreferStaffModule(ShiftAssignmentModule):
#     def build(self, instance, model, nurse_shift_vars):
#         """
#         Penalize use of non-staff (contract) nurses in the objective.
#         """
#         expr = 0
#         for nv in nurse_shift_vars:
#             if not nv.nurse.staff:
#                 for uid in nv._x:
#                     expr += instance.staff_weight * nv.is_assigned_to(uid)
#         return expr


# class LimitWorkTimeModule(ShiftAssignmentModule):
#     """4th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
#     def build(self, instance, model, nurse_shift_vars):
#         for nv in nurse_shift_vars:
#             min_time = nv.nurse.minimum_work_time
#             max_time = nv.nurse.maximum_work_time
#             if min_time is None and max_time is None:
#                 continue
#             working_time = 0
#             for shift, var in nv.iter_shifts():
#                 working_time += (shift.end_time - shift.start_time) * var
#             if min_time is not None:
#                 model.add_constraint(working_time >= min_time)
#             if max_time is not None:
#                 model.add_constraint(working_time <= max_time)
#         return 0


# def group_shifts_by_date(instance: NurseRosteringInstance) -> tuple[list[Any], dict[Any, Any]]:
#     shifts_by_date = {}
#     for shift in instance.shifts:
#         current_date = shift.start_time.date()
#         end_date = shift.end_time.date()
#         while current_date <= end_date:
#             shifts_by_date.setdefault(current_date, []).append(shift.uid)
#             current_date += timedelta(days=1)

#     min_date = instance.shifts[0].start_time.date()
#     max_date = instance.shifts[-1].end_time.date()

#     all_dates = []
#     current_date = min_date
#     while current_date <= max_date:
#         all_dates.append(current_date)
#         current_date += timedelta(days=1)
#     return all_dates, shifts_by_date


# def get_work_day_vars(instance, model, nv, all_dates, shifts_by_date):
#     if not hasattr(instance, "_work_day_vars"):
#         instance._work_day_vars = {}  # nurse_uid -> list[w]

#     nurse_uid = nv.nurse.uid
#     if nurse_uid in instance._work_day_vars:
#         return instance._work_day_vars[nurse_uid]
#     all_dates.sort(key=lambda s: s.start_time)
#     work_days = []
#     for date in all_dates:
#         w = model.new_bool_var(f"work_{nv.nurse.uid}_{date.isoformat()}")
#         work_days.append(w)
#         uids = shifts_by_date.get(date, [])
#         vars_for_date = [nv.is_assigned_to(uid) for uid in uids]
#         if not vars_for_date:
#             model.add_constraint(w == 0)
#         else:
#             model.add_constraint_max_equality(w, vars_for_date)

#     instance._work_day_vars[nurse_uid] = work_days
#     return work_days


# class MaximumConsecutiveShiftsModule(ShiftAssignmentModule):
#     """5th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
#     def build(self, instance, model, nurse_shift_vars):
#         all_dates, shifts_by_date = group_shifts_by_date(instance)
#         if not all_dates:
#             return 0
#         for nv in nurse_shift_vars:
#             max_shifts = nv.nurse.maximum_consecutive_shifts
#             if max_shifts is None:
#                 continue
#             work_day = get_work_day_vars(instance, model, nv, all_dates, shifts_by_date)

#             for i in range(len(work_day)-max_shifts):
#                 model.add_constraint(sum(work_day[i:i+max_shifts+1]) <= max_shifts)

#         return 0


# class MinimumConsecutiveShiftsModule(ShiftAssignmentModule):
#     """6th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
#     def build(self, instance, model, nurse_shift_vars):

#         all_dates, shifts_by_date = group_shifts_by_date(instance)
#         if not all_dates:
#             return 0
#         for nv in nurse_shift_vars:
#             min_shifts = nv.nurse.minimum_consecutive_shifts
#             if min_shifts is None:
#                 continue
#             work_days = get_work_day_vars(instance, model, nv, all_dates, shifts_by_date)
#             for s in range(1, min_shifts):
#                 for d in range(len(work_days) - (s+1)):
#                     model.add_constraint(work_days[d] + work_days[d+s+1] + (s - sum(work_days[d+1:d+s+1])) >= 1)
#         return 0
    

# class MinimumConsecutiveDaysOffModule(ShiftAssignmentModule):
#     """7th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
#     def build(self, instance, model, nurse_shift_vars):
#         all_dates, shifts_by_date = group_shifts_by_date(instance)
#         if not all_dates:
#             return 0
#         for nv in nurse_shift_vars:
#             min_days_off = nv.nurse.minimum_consecutive_days_off
#             if min_days_off is None:
#                 continue
#             work_days = get_work_day_vars(instance, model, nv, all_dates, shifts_by_date)
#             for s in range(1, min_days_off):
#                 for d in range(len(work_days) - (s + 1)):
#                     model.add_constraint(1 - work_days[d] + 1 - work_days[d + s + 1] + sum(work_days[d + 1:d + s + 1]) >= 1)
#         return 0

# class MaximumNumberOfWeekendsModule(ShiftAssignmentModule):
#     """8th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
#     def build(self, instance, model, nurse_shift_vars):
#         all_dates, shifts_by_date = group_shifts_by_date(instance)
#         if not all_dates:
#             return 0
#         dates_to_index = {date: i for i, date in enumerate(all_dates)}
#         saturdays = [d for d in all_dates if d.weekday() == 5]
#         for nv in nurse_shift_vars:
#             max_weekends = nv.nurse.maximum_weekends
#             if max_weekends is None:
#                 continue
#             weekend = []
#             work_days = get_work_day_vars(instance, model, nv, all_dates, shifts_by_date)
#             for saturday in saturdays:
#                 w = model.new_bool_var(f"nurse_{nv.nurse.uid}_works_on_weekend_{saturday.isoformat()}")
#                 weekend.append(w)
#                 sunday = saturday + timedelta(days=1)
#                 index = dates_to_index[saturday]
#                 if sunday not in dates_to_index:
#                     model.add_constraint(w == work_days[index])
#                 else:
#                     model.add_constraint(w <= work_days[index] + work_days[index+1])
#                     model.add_constraint(work_days[index] + work_days[index + 1] <= 2 * w)
#             model.add_constraint(sum(weekend) <= max_weekends)

#         return 0


# # class DaysOffModule(ShiftAssignmentModule):
# #     """9th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf
# #         Possibly already enforced by NoBlockedShiftsModule"""
# #     def build(self, instance, model, nurse_shift_vars):
# #
# #         return 0
# # Indeed already enforced by NoBlockedShiftsModule


# # class CoverRequirementsModule(ShiftAssignmentModule):
# #     """10th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
# #     def build(self, instance, model, nurse_shift_vars):
# #
# #         return 0
# # conflicts with demand satisfaction

