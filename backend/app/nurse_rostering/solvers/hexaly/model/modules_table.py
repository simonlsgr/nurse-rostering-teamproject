import abc
from datetime import timedelta, date
from typing import Any

from hexaly.optimizer import HxModel, HxExpression

from nurse_rostering.data_schema import NurseRosteringInstance, Shift, ShiftUid
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVarsTable, PreferredCoverDecisionVarsIP
from nurse_rostering.utils.data_utils import group_shifts_by_date, get_weekends, get_shift_type_dict


class ShiftAssignmentModuleTable(abc.ABC):
    @abc.abstractmethod
    def build(
            self,
            instance: NurseRosteringInstance,
            model: HxModel,
            nurse_shift_vars: list[NurseDecisionVarsTable],
            dates: dict[date, list[ShiftUid]]
    ) -> HxExpression:
        """
        Add constraints and optionally return a sub-objective expression.
        Each subclass defines one constraint or objective aspect.
        """
        return 0


class OneShiftPerDayModuleTable(ShiftAssignmentModuleTable):
    """1st constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars, dates):
        """
        Enforce that each nurse works at most one shift per day.
        """
        # Implicit
        return 0


class ShiftRotationModuleTable(ShiftAssignmentModuleTable):
    """2nd constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars, dates):
        """
        Enforce minimum rest time between any two shifts for a nurse.
        """
        shift_by_uid = {shift.uid: shift for shift in instance.shifts}
        for _date, shift_uids in dates.items():
            following_date = _date+timedelta(days=1)
            if following_date not in dates:
                continue
            shift_mapping = {}
            for i in range(len(shift_uids)):
                current_shift_uid = shift_uids[i]
                current_shift_types = shift_by_uid[current_shift_uid].not_followed_by_shift_types
                for j in range(len(dates[following_date])):
                    shift_uid = dates[following_date][j]
                    if shift_by_uid[shift_uid].type in current_shift_types:
                        shift_mapping.setdefault(i+1, []).append(j+1)
            for shift, types in shift_mapping.items():
                for nv in nurse_shift_vars:
                    for _type in types:
                        model.add_constraint(
                            model.iif(nv.is_assigned_to(_date) == shift, 1, 0) +
                            model.iif(nv.is_assigned_to(following_date) == _type, 1, 0)
                            <= 1
                        )

        return 0  # no objective contribution


class MaximumShiftTypesModuleTable(ShiftAssignmentModuleTable):

    def build(self, instance, model, nurse_shift_vars, dates):
        shift_by_uid = {shift.uid: shift for shift in instance.shifts}

        day_index_to_type = {}
        for _date, shift_uids in dates.items():
            day_index_to_type[_date] = {}
            for i, shift_uid in enumerate(shift_uids):
                day_index_to_type[_date].setdefault(shift_by_uid[shift_uid].type, []).append(i+1)
        for nv in nurse_shift_vars:
            for _type, max_count in nv.nurse.maximum_number_of_shifts_per_type.items():
                count_expr = model.sum(
                    model.iif(nv.is_assigned_to(_date) == index, 1, 0)
                    for _date in dates.keys()
                    for index in day_index_to_type[_date].get(_type, [])
                )
                model.add_constraint(count_expr <= max_count)

        return 0


class MaximizePreferencesTable(ShiftAssignmentModuleTable):
    def build(self, instance, model, nurse_shift_vars, dates):
        """
        Encourage assigning nurses to their preferred shifts.
        Each preference counts negatively toward the minimization objective.
        """
        shift_uid_table = {}
        for _date, shift_uids in dates.items():
            for i in range(len(shift_uids)):
                shift_uid_table[shift_uids[i]] = (_date, i+1)
        expr = 0
        for nv in nurse_shift_vars:
            for shift_uid in nv.nurse.preferred_shifts:
                expr += nv.nurse.preferred_shift_weight[shift_uid] * model.iif(nv.is_assigned_to(shift_uid_table[shift_uid][0]) == shift_uid_table[shift_uid][1], 0, 1)
        return expr


class OffPreferencesTable(ShiftAssignmentModuleTable):
    def build(self, instance, model, nurse_shift_vars, dates):
        shift_uid_table = {}
        for _date, shift_uids in dates.items():
            for i in range(len(shift_uids)):
                shift_uid_table[shift_uids[i]] = (_date, i + 1)
        expr = 0
        for nv in nurse_shift_vars:
            shift_off_uids = nv.nurse.preferred_off_shifts
            if not shift_off_uids:
                continue
            for shift_uid in shift_off_uids:
                    expr += nv.nurse.preferred_off_shift_weight[shift_uid] * model.iif(nv.is_assigned_to(shift_uid_table[shift_uid][0]) == shift_uid_table[shift_uid][1], 1, 0)
        return expr


class PreferStaffModuleTable(ShiftAssignmentModuleTable):
    def build(self, instance, model, nurse_shift_vars, dates):
        """
        Penalize use of non-staff (contract) nurses in the objective.
        """
        expr = 0
        for nv in nurse_shift_vars:
            if not nv.nurse.staff:
                for _date in dates:
                    expr += instance.staff_weight * model.iif(nv.is_assigned_to(_date) >= 1, 1, 0)
        return expr


class LimitWorkTimeModuleTable(ShiftAssignmentModuleTable):
    """4th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars, dates):
        shift_by_uid = {shift.uid: shift for shift in instance.shifts}
        durations_by_day = {}
        for _date, shift_uids in dates.items():
            durations = [0]
            for shift_uid in shift_uids:
                shift = shift_by_uid[shift_uid]
                durations.append(int((shift.end_time - shift.start_time).total_seconds() / 60))
            durations_by_day[_date] = model.array(durations)
        for nv in nurse_shift_vars:
            min_time = nv.nurse.minimum_work_time
            max_time = nv.nurse.maximum_work_time
            if min_time is None and max_time is None:
                continue
            working_time = model.sum(
                model.at(durations_by_day[_date], nv.is_assigned_to(_date))
                for _date in dates
            )
            if min_time is not None:
                model.add_constraint(working_time >= min_time)
            if max_time is not None:
                model.add_constraint(working_time <= max_time)
        return 0


class MaximumConsecutiveShiftsModuleTable(ShiftAssignmentModuleTable):
    """5th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars, dates):
        dates_in_order = sorted(dates.keys())
        for nv in nurse_shift_vars:
            max_consecutive = nv.nurse.maximum_consecutive_shifts
            if max_consecutive is None:
                continue
            window_len = max_consecutive + 1
            if len(dates_in_order) < window_len:
                continue

            for start in range(len(dates_in_order) - window_len + 1):
                window_dates = dates_in_order[start:start + window_len]

                worked_days_in_window = model.sum(
                    model.iif(nv.is_assigned_to(_date) >= 1, 1, 0)
                    for _date in window_dates
                )

                model.add_constraint(worked_days_in_window <= max_consecutive)
        return 0


class MinimumConsecutiveShiftsModuleTable(ShiftAssignmentModuleTable):
    """6th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars, dates):
        dates_in_order = sorted(dates.keys())
        for nv in nurse_shift_vars:
            min_consecutive = nv.nurse.minimum_consecutive_shifts
            if min_consecutive is None:
                continue
            for s in range(1, min_consecutive):
                for d in range(instance.planning_horizon_in_days - (s+1)):
                    expr = model.iif(nv.is_assigned_to(dates_in_order[d]) >= 1, 1, 0)
                    expr += s - model.sum(
                        model.iif(nv.is_assigned_to(_date) >= 1, 1, 0)
                        for _date in dates_in_order[d+1:d+s+1]
                    )
                    expr += model.iif(nv.is_assigned_to(dates_in_order[d+s+1]) >= 1, 1, 0)
                    model.add_constraint(expr > 0)

        return 0


class MinimumConsecutiveDaysOffModuleTable(ShiftAssignmentModuleTable):
    """7th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars, dates):
        dates_in_order = sorted(dates.keys())
        for nv in nurse_shift_vars:
            min_consecutive = nv.nurse.minimum_consecutive_days_off
            if min_consecutive is None:
                continue
            for s in range(1, min_consecutive):
                for d in range(instance.planning_horizon_in_days - (s + 1)):
                    expr = model.iif(nv.is_assigned_to(dates_in_order[d]) >= 1, 0, 1)
                    expr += model.sum(
                        model.iif(nv.is_assigned_to(_date) >= 1, 1, 0)
                        for _date in dates_in_order[d + 1:d + s + 1]
                    )
                    expr += model.iif(nv.is_assigned_to(dates_in_order[d + s + 1]) >= 1, 0, 1)
                    model.add_constraint(expr > 0)

        return 0


class MaximumNumberOfWeekendsModuleTable(ShiftAssignmentModuleTable):
    """8th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars, dates):
        weekends = get_weekends(instance)
        if not weekends:
            return 0
        for nv in nurse_shift_vars:
            nurse = nv.nurse
            max_weekends = nurse.maximum_weekends
            if max_weekends is None:
                continue
            first = weekends[0]
            sat = first[0]
            sun = first[1]
            expr = 0
            if sat in dates:
                expr += model.iif(nv.is_assigned_to(sat) + nv.is_assigned_to(sun) >= 1, 1, 0)
            else:
                expr += model.iif(nv.is_assigned_to(sun) >= 1, 1, 0)
            if len(weekends) > 1:
                expr += model.sum(
                    model.iif(nv.is_assigned_to(weekends[i][0]) + nv.is_assigned_to(weekends[i][1]) >= 1, 1, 0)
                    for i in range(1, len(weekends)-1)
                )
                last = weekends[-1]
                sat = last[0]
                sun = last[1]
                if sun in dates:
                    expr += model.iif(nv.is_assigned_to(sat) + nv.is_assigned_to(sun) >= 1, 1, 0)
                else:
                    expr += model.iif(nv.is_assigned_to(sat) >= 1, 1, 0)
            model.add_constraint(expr <= max_weekends)
        return 0


class DaysOffModuleTable(ShiftAssignmentModuleTable):
    """9th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars, dates):
        for nv in nurse_shift_vars:
            days_off = nv.nurse.days_off
            if days_off is None:
                continue
            for _date in days_off:
                model.add_constraint(nv.is_assigned_to(_date) == 0)

        return 0


class CoverRequirementsModuleTable(ShiftAssignmentModuleTable):
    """10th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars, dates):
        shift_by_uid = {shift.uid: shift for shift in instance.shifts}
        shift_uid_table = {}
        for _date, shift_uids in dates.items():
            for i in range(len(shift_uids)):
                shift_uid_table[shift_uids[i]] = (_date, i + 1)
        preferred_cover_vars = PreferredCoverDecisionVarsIP(shifts=instance.shifts, model=model)
        expr = 0
        for shift_uid, field in shift_uid_table.items():
            assigned_nurses = model.sum(
                model.iif(nv.is_assigned_to(field[0]) == field[1], 1, 0)
                for nv in nurse_shift_vars
            )
            model.add_constraint(
                assigned_nurses - preferred_cover_vars.total_above_preferred[shift_uid] +
                preferred_cover_vars.total_below_preferred[shift_uid]
                ==
                shift_by_uid[shift_uid].demand
            )

            expr += shift_by_uid[shift_uid].weight_below_demand * preferred_cover_vars.total_below_preferred[
                shift_uid]
            expr += shift_by_uid[shift_uid].weight_above_demand * preferred_cover_vars.total_above_preferred[
                shift_uid]

        return expr