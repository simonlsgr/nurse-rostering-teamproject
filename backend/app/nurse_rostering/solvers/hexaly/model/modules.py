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
            for nurse_index in range(len(instance.nurses)):
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
                    
        return 0
            
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
            
                
            
class MinimumConsecutiveShiftsModule(ShiftAssignmentModule):
    """6th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    
    def is_consecutive(self, all_dates, start_index, length):
        if length <= 1:
            return True
        for i in range(start_index, start_index + length - 1):
            if (all_dates[i+1] - all_dates[i]).days != 1:
                return False
        return True
    
    def build(self, instance, model, shift_vars):
        shifts_by_date = {}
        for sv in shift_vars:
            date = sv.shift.start_time.date()
            shifts_by_date.setdefault(date, []).append(sv)
        
        shifts_by_date_union = {date: model.union([sv.nurses_assigned for sv in svs]) for date, svs in shifts_by_date.items()}
        all_dates = sorted(shifts_by_date.keys())
        for n_idx, nurse in enumerate(instance.nurses):
            min_shifts = nurse.minimum_consecutive_shifts
            if min_shifts is None or min_shifts <= 1:
                continue
            for s in range(1, min_shifts):
                for d in range(0, len(all_dates)-(s+1)):
                    if not self.is_consecutive(all_dates, d, s+1):
                        continue
                    
                    date_start = all_dates[d]
                    date_end = all_dates[d+s+1]
                    
                    model.add_constraint(
                        model.contains(shifts_by_date_union[date_start], n_idx) + 
                        model.contains(shifts_by_date_union[date_end], n_idx) + 
                        (s - sum([model.contains(shifts_by_date_union[all_dates[d+inc]], n_idx) for inc in range(1, s+1)])) 
                        >= 1
                    )
            
            self.enforce_for_first_day(model, shifts_by_date_union, all_dates, n_idx, min_shifts)
            self.enforce_for_last_day(model, shifts_by_date_union, all_dates, n_idx, min_shifts)
            
        return 0 

    def enforce_for_last_day(self, model, shifts_by_date_union, all_dates, n_idx, min_shifts):
        model.add_constraint(
                model.contains(shifts_by_date_union[all_dates[-1]], n_idx)
                <= 
                sum(
                    [
                        model.contains(shifts_by_date_union[all_dates[len(all_dates)-1 - inc]], n_idx) 
                        for inc in range(1, min_shifts)
                    ]
                )
            )

    def enforce_for_first_day(self, model, shifts_by_date_union, all_dates, n_idx, min_shifts):
        model.add_constraint(
                model.contains(shifts_by_date_union[all_dates[0]], n_idx)
                <= 
                sum(
                    [
                        model.contains(shifts_by_date_union[all_dates[inc]], n_idx) 
                        for inc in range(1, min_shifts)
                    ]
                )
            )   
            
class MinimumConsecutiveDaysOffModule(ShiftAssignmentModule):
    """7th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    
    def build(self, instance, model, shift_vars):
        shifts_by_date = {}
        for sv in shift_vars:
            date = sv.shift.start_time.date()
            shifts_by_date.setdefault(date, []).append(sv)
        
        shifts_by_date_union = {date: model.union([sv.nurses_assigned for sv in svs]) for date, svs in shifts_by_date.items()}
        all_dates = sorted(shifts_by_date.keys())
        for n_idx, nurse in enumerate(instance.nurses):
            min_days_off = nurse.minimum_consecutive_days_off
            if min_days_off is None or min_days_off <= 1:
                continue
            for s in range(1, min_days_off):
                for d in range(0, len(all_dates)-(s+1)):
                    date_start = all_dates[d]
                    date_end = all_dates[d+s+1]
                    
                    model.add_constraint(
                        (1 - model.contains(shifts_by_date_union[date_start], n_idx)) + 
                        (1 - model.contains(shifts_by_date_union[date_end], n_idx)) + 
                        sum([model.contains(shifts_by_date_union[all_dates[d+inc]], n_idx) for inc in range(1, s+1)]) 
                        >= 1
                    )
        
        self.enfore_for_first_day(model, shifts_by_date_union, all_dates, n_idx, min_days_off)
        self.enfore_for_last_day(model, shifts_by_date_union, all_dates, n_idx, min_days_off)
        
        return 0
    
    def enfore_for_first_day(self, model, shifts_by_date_union, all_dates, n_idx, min_days_off):
        model.add_constraint(
            (1 - model.contains(shifts_by_date_union[all_dates[0]], n_idx))
            <= 
            sum(
                [
                    (1 - model.contains(shifts_by_date_union[all_dates[inc]], n_idx)) 
                    for inc in range(1, min_days_off)
                ]
            )
        )
        
    
    def enfore_for_last_day(self, model, shifts_by_date_union, all_dates, n_idx, min_days_off):
        model.add_constraint(
            (1 - model.contains(shifts_by_date_union[all_dates[-1]], n_idx))
            <= 
            sum(
                [
                    (1 - model.contains(shifts_by_date_union[all_dates[len(all_dates)-1 - inc]], n_idx)) 
                    for inc in range(1, min_days_off)
                ]
            )
        )


# should work but tests dont terminate
# class MaximumNumberOfWeekendsModule(ShiftAssignmentModule):
#     """8th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
#     def build(self, instance, model, shift_vars):
#         shifts_by_date = {}
#         for sv in shift_vars:
#             date = sv.shift.start_time.date()
#             shifts_by_date.setdefault(date, []).append(sv)
        
#         all_weekends = [date for date in shifts_by_date.keys() if date.weekday() in (5,6)]
#         weekend_shifts_union = {date: [sv.nurses_assigned for sv in shifts_by_date[date]] for date in all_weekends}
#         # union over two days of the weekend saturday and sunday
        
#         weekend_as_one_shift = {}
#         for date in all_weekends:
#             if date.weekday() == 5:
#                 if date + timedelta(days=1) in all_weekends:
#                     weekend_as_one_shift[date] = weekend_shifts_union[date] + weekend_shifts_union[date + timedelta(days=1)]
#                 else:
#                     weekend_as_one_shift[date] = weekend_shifts_union[date]
#         for date in all_weekends:
#             if date.weekday() == 6:
#                 if (date - timedelta(days=1)) not in all_weekends:
#                     weekend_as_one_shift[date-timedelta(days=1)] = weekend_shifts_union[date]
                    
        
        
        
#         for n_idx, nurse in enumerate(instance.nurses):
#             max_weekends = nurse.maximum_weekends
#             if max_weekends is None:
#                 continue
#             model.add_constraint(
#                 sum([model.contains(model.union(weekend_as_one_shift[date]), n_idx) for date in weekend_as_one_shift]) <= max_weekends
#             )

#         return 0
        



class MaximumNumberOfWeekendsModule(ShiftAssignmentModule):
    """8th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf
    It is assumed that if a sunday or a saturday is in the model, the corresponding other weekend day is also part of the scheduling horizn.
    """

    def get_weekend_info(self, shifts_by_date_weekend):
        nb_weekends = 0
        skip_dates = []
        saturdays_dates = []
        for date in sorted(shifts_by_date_weekend.keys()):
            if date.weekday() == 5:
                saturdays_dates.append(date)
                skip_dates.append(date + timedelta(days=1))
                nb_weekends += 1
            if date.weekday() == 6 and date not in skip_dates:
                saturdays_dates.append(date - timedelta(days=1))
                nb_weekends += 1
        
        return nb_weekends, saturdays_dates
    
    def build(self, instance, model, shift_vars):
        
        shifts_by_date = {}
        for sv in shift_vars:
            date = sv.shift.start_time.date()
            shifts_by_date.setdefault(date, []).append(sv)
        
        shifts_by_date_weekend = {date: shifts for date, shifts in shifts_by_date.items() if date.weekday() in (5,6)}
        nb_weekends, saturdays = self.get_weekend_info(shifts_by_date_weekend)
        
        weekend_vars = {nurse.uid: [model.bool() for _ in range(nb_weekends)] for nurse in instance.nurses}
        for n_idx, nurse in enumerate(instance.nurses):
            max_weekends = nurse.maximum_weekends
            if max_weekends is None:
                continue
            for w_idx, saturday in enumerate(saturdays):
                sum_saturday = model.contains(model.union([sv.nurses_assigned for sv in shifts_by_date_weekend[saturday]]), n_idx)
                sum_sunday = model.contains(model.union([sv.nurses_assigned for sv in shifts_by_date_weekend[saturday + timedelta(days=1)]]), n_idx)
                model.add_constraint(
                    weekend_vars[nurse.uid][w_idx] <= sum_saturday + sum_sunday
                )
                model.add_constraint(
                    sum_saturday + sum_sunday <= weekend_vars[nurse.uid][w_idx] * 2
                )
            model.add_constraint(
                sum(weekend_vars[nurse.uid]) <= max_weekends
            )
        
        return 0
                

class DaysOffModule(ShiftAssignmentModule):
    """9th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    
    def build(self, instance, model, shift_vars):
        shifts_by_date = {}
        for sv in shift_vars:
            date = sv.shift.start_time.date()
            shifts_by_date.setdefault(date, []).append(sv)
        
        for n_idx, nurse in enumerate(instance.nurses):
            if nurse.days_off is None:
                continue
            for day_off in nurse.days_off:
                if day_off in shifts_by_date:
                    svs = shifts_by_date[day_off]
                    for sv in svs:
                        model.add_constraint(
                            model.contains(sv.nurses_assigned, n_idx) == 0
                        )
        return 0


class CoverRequirementsModule(ShiftAssignmentModule):
    """10th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    
    def build(self, instance, model, shift_vars):
        
        expr = 0
        for sv in shift_vars:
            preferred_demand = sv.shift.demand
            
            expr += model.iif(
                model.count(sv.nurses_assigned) - preferred_demand < 0, # if
                    sv.shift.weight_below_demand * (preferred_demand - model.count(sv.nurses_assigned)),  #then
                    sv.shift.weight_above_demand * (model.count(sv.nurses_assigned) - preferred_demand)  # else
                )
        
        return expr
        

class PreferStaffModule(ShiftAssignmentModule):
    def build(self, instance, model, shift_vars):
        """
        Penalize use of non-staff (contract) nurses in the objective.
        """
        expr = 0
        for sv in shift_vars:
            for n_idx, nurse in enumerate(sv.nurses):
                if not nurse.staff:
                    expr += instance.staff_weight * model.contains(sv.nurses_assigned, n_idx)
        return expr                   

class PreferredShiftsModule(ShiftAssignmentModule):
    """Part of objective in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""
    
    def build(self, instance, model, shift_vars):
        
        expr = 0
        for sv in shift_vars:
            for n_idx, nurse in enumerate(sv.nurses):
                if sv.shift.uid in nurse.preferred_shifts:
                    expr += nurse.preferred_shift_weight * (1- model.contains(sv.nurses_assigned, n_idx))
                if sv.shift.uid in nurse.preferred_off_shifts:
                    expr += nurse.preferred_off_shift_weight * model.contains(sv.nurses_assigned, n_idx)
        
        return expr
                
        

        
            
            
        
