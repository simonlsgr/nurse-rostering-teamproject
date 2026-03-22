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
    """2nd constraint in the benchmark paper."""

    def build(self, instance, model, nurse_var, dates):

        shift_by_uid = {shift.uid: shift for shift in instance.shifts}
        date_to_index = {d: i for i, d in enumerate(sorted(dates))}

        for _date, shift_uids in dates.items():
            following_date = _date + timedelta(days=1)
            if following_date not in dates:
                continue

            current_date_index = date_to_index[_date]
            following_date_index = date_to_index[following_date]

            shift_mapping = {}

            for i, current_shift_uid in enumerate(shift_uids, start=1):
                forbidden_types = shift_by_uid[current_shift_uid].not_followed_by_shift_types

                mapping = [0]
                for next_shift_uid in dates[following_date]:
                    if shift_by_uid[next_shift_uid].type in forbidden_types:
                        mapping.append(1)
                    else:
                        mapping.append(0)
                shift_mapping[i] = model.array(mapping)

            for shift_index in shift_mapping:
                current_shift_indicator = [0] * (len(shift_uids) + 1)
                current_shift_indicator[shift_index] = 1
                current_shift_indicator = model.array(current_shift_indicator)

                for nurse_index in range(len(instance.nurses)):
                    model.add_constraint(
                        model.at(current_shift_indicator, nurse_var[nurse_index][current_date_index]) +
                        model.at(shift_mapping[shift_index], nurse_var[nurse_index][following_date_index])
                        <= 1
                    )

        return 0


class MaximumShiftTypesModuleTable(ShiftAssignmentModuleTable):

    def build(self, instance, model, nurse_vars, dates):
        shift_by_uid = {shift.uid: shift for shift in instance.shifts}
        sorted_dates = sorted(dates)
        date_to_index = {d: i for i, d in enumerate(sorted_dates)}

        day_type_mapping = {}
        zero_mapping = {}

        for _date, shift_uids in dates.items():
            day_type_mapping[_date] = {}
            zero_mapping[_date] = model.array([0] * (len(shift_uids) + 1))

            types_on_day = {shift_by_uid[uid].type for uid in shift_uids}

            for _type in types_on_day:
                mapping = [0]
                for shift_uid in shift_uids:
                    mapping.append(1 if shift_by_uid[shift_uid].type == _type else 0)
                day_type_mapping[_date][_type] = model.array(mapping)

        for nurse_index, nurse in enumerate(instance.nurses):
            for _type, max_count in nurse.maximum_number_of_shifts_per_type.items():
                count_expr = model.sum(
                    model.at(
                        day_type_mapping[_date].get(_type, zero_mapping[_date]),
                        nurse_vars[nurse_index][date_to_index[_date]]
                    )
                    for _date in dates
                )
                model.add_constraint(count_expr <= max_count)

        return 0


class MaximizePreferencesTable(ShiftAssignmentModuleTable):
    def build(self, instance, model, nurse_vars, dates):
        expr = 0
        sorted_dates = sorted(dates)
        date_to_index = {d: i for i, d in enumerate(sorted_dates)}

        for nurse_index, nurse in enumerate(instance.nurses):
            mapping = {}
            preferred_shifts = set(nurse.preferred_shifts)

            for _date, shift_uids in dates.items():
                day_penalty = sum(
                    nurse.preferred_shift_weight[shift_uid]
                    for shift_uid in shift_uids
                    if shift_uid in preferred_shifts
                )
                current = [day_penalty]

                for shift_uid in shift_uids:
                    if shift_uid in preferred_shifts:
                        current.append(day_penalty - nurse.preferred_shift_weight[shift_uid])
                    else:
                        current.append(day_penalty)

                mapping[_date] = model.array(current)

            expr += model.sum(
                model.at(mapping[_date], nurse_vars[nurse_index][date_to_index[_date]])
                for _date in dates
            )

        return expr


class OffPreferencesTable(ShiftAssignmentModuleTable):
    def build(self, instance, model, nurse_vars, dates):
        expr = 0
        sorted_dates = sorted(dates)
        date_to_index = {d: i for i, d in enumerate(sorted_dates)}

        for nurse_index, nurse in enumerate(instance.nurses):
            off_shifts = set(nurse.preferred_off_shifts)
            if not off_shifts:
                continue
            mapping = {}

            for _date, shift_uids in dates.items():
                current = [0]
                for shift_uid in shift_uids:
                    if shift_uid in off_shifts:
                        current.append(nurse.preferred_off_shift_weight[shift_uid])
                    else:
                        current.append(0)

                mapping[_date] = model.array(current)

            expr += model.sum(
                model.at(mapping[_date], nurse_vars[nurse_index][date_to_index[_date]])
                for _date in dates
            )

        return expr


class PreferStaffModuleTable(ShiftAssignmentModuleTable):
    def build(self, instance, model, nurse_vars, dates):
        """
        Penalize use of non-staff (contract) nurses in the objective.
        """
        expr = 0
        sorted_dates = sorted(dates)
        date_to_index = {d: i for i, d in enumerate(sorted_dates)}

        works_mapping = {
            _date: model.array([0] + [1] * len(shift_uids))
            for _date, shift_uids in dates.items()
        }

        for nurse_index, nurse in enumerate(instance.nurses):
            if not nurse.staff:
                for _date in dates:
                    expr += instance.staff_weight * model.at(
                        works_mapping[_date],
                        nurse_vars[nurse_index][date_to_index[_date]]
                    )
        return expr


class LimitWorkTimeModuleTable(ShiftAssignmentModuleTable):
    """4th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_vars, dates):
        shift_by_uid = {shift.uid: shift for shift in instance.shifts}
        sorted_dates = sorted(dates)
        date_to_index = {d: i for i, d in enumerate(sorted_dates)}
        durations_by_day = {}

        for _date, shift_uids in dates.items():
            durations = [0]
            for shift_uid in shift_uids:
                shift = shift_by_uid[shift_uid]
                durations.append(int((shift.end_time - shift.start_time).total_seconds() / 60))
            durations_by_day[_date] = model.array(durations)

        for nurse_index, nurse in enumerate(instance.nurses):
            min_time = nurse.minimum_work_time
            max_time = nurse.maximum_work_time
            if min_time is None and max_time is None:
                continue

            working_time = model.sum(
                model.at(durations_by_day[_date], nurse_vars[nurse_index][date_to_index[_date]])
                for _date in dates
            )

            if min_time is not None:
                model.add_constraint(working_time >= min_time)
            if max_time is not None:
                model.add_constraint(working_time <= max_time)

        return 0


class MaximumConsecutiveShiftsModuleTable(ShiftAssignmentModuleTable):
    """5th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_vars, dates):
        dates_in_order = sorted(dates.keys())
        date_to_index = {d: i for i, d in enumerate(dates_in_order)}
        works_mapping = {
            _date: model.array([0] + [1] * len(shift_uids))
            for _date, shift_uids in dates.items()
        }

        for nurse_index, nurse in enumerate(instance.nurses):
            max_consecutive = nurse.maximum_consecutive_shifts
            if max_consecutive is None:
                continue

            window_len = max_consecutive + 1
            if len(dates_in_order) < window_len:
                continue

            for start in range(len(dates_in_order) - window_len + 1):
                window_dates = dates_in_order[start:start + window_len]

                worked_days_in_window = model.sum(
                    model.at(works_mapping[_date], nurse_vars[nurse_index][date_to_index[_date]])
                    for _date in window_dates
                )

                model.add_constraint(worked_days_in_window <= max_consecutive)

        return 0

class MinimumConsecutiveShiftsModuleTable(ShiftAssignmentModuleTable):
    """6th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_vars, dates):
        dates_in_order = sorted(dates.keys())
        date_to_index = {d: i for i, d in enumerate(dates_in_order)}
        works_mapping = {
            _date: model.array([0] + [1] * len(shift_uids))
            for _date, shift_uids in dates.items()
        }

        for nurse_index, nurse in enumerate(instance.nurses):
            min_consecutive = nurse.minimum_consecutive_shifts
            if min_consecutive is None:
                continue

            for s in range(1, min_consecutive):
                for d in range(len(dates_in_order) - (s + 1)):
                    expr = model.at(
                        works_mapping[dates_in_order[d]],
                        nurse_vars[nurse_index][date_to_index[dates_in_order[d]]]
                    )
                    expr += s - model.sum(
                        model.at(
                            works_mapping[_date],
                            nurse_vars[nurse_index][date_to_index[_date]]
                        )
                        for _date in dates_in_order[d + 1:d + s + 1]
                    )
                    expr += model.at(
                        works_mapping[dates_in_order[d + s + 1]],
                        nurse_vars[nurse_index][date_to_index[dates_in_order[d + s + 1]]]
                    )
                    model.add_constraint(expr > 0)

        return 0

class MinimumConsecutiveDaysOffModuleTable(ShiftAssignmentModuleTable):
    """7th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_vars, dates):
        dates_in_order = sorted(dates.keys())
        date_to_index = {d: i for i, d in enumerate(dates_in_order)}
        works_mapping = {
            _date: model.array([0] + [1] * len(shift_uids))
            for _date, shift_uids in dates.items()
        }

        for nurse_index, nurse in enumerate(instance.nurses):
            min_consecutive = nurse.minimum_consecutive_days_off
            if min_consecutive is None:
                continue

            for s in range(1, min_consecutive):
                for d in range(len(dates_in_order) - (s + 1)):
                    expr = 1 - model.at(
                        works_mapping[dates_in_order[d]],
                        nurse_vars[nurse_index][date_to_index[dates_in_order[d]]]
                    )
                    expr += model.sum(
                        model.at(
                            works_mapping[_date],
                            nurse_vars[nurse_index][date_to_index[_date]]
                        )
                        for _date in dates_in_order[d + 1:d + s + 1]
                    )
                    expr += 1 - model.at(
                        works_mapping[dates_in_order[d + s + 1]],
                        nurse_vars[nurse_index][date_to_index[dates_in_order[d + s + 1]]]
                    )
                    model.add_constraint(expr > 0)

        return 0

class MaximumNumberOfWeekendsModuleTable(ShiftAssignmentModuleTable):
    """8th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_vars, dates):
        weekends = get_weekends(instance)
        if not weekends:
            return 0

        sorted_dates = sorted(dates)
        date_to_index = {d: i for i, d in enumerate(sorted_dates)}
        works_on_day = {
            _date: model.array([0] + [1] * len(shift_uids))
            for _date, shift_uids in dates.items()
        }
        weekend_or = model.array([0, 1, 1])

        for nurse_index, nurse in enumerate(instance.nurses):
            max_weekends = nurse.maximum_weekends
            if max_weekends is None:
                continue

            expr = model.sum(
                model.at(
                    weekend_or,
                    (model.at(works_on_day[sat],
                              nurse_vars[nurse_index][date_to_index[sat]]) if sat in dates else 0) +
                    (model.at(works_on_day[sun],
                              nurse_vars[nurse_index][date_to_index[sun]]) if sun in dates else 0)
                )
                for sat, sun in weekends
                if sat in dates or sun in dates
            )

            model.add_constraint(expr <= max_weekends)

        return 0

class DaysOffModuleTable(ShiftAssignmentModuleTable):
    """9th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_vars, dates):
        sorted_dates = sorted(dates)
        date_to_index = {d: i for i, d in enumerate(sorted_dates)}

        for nurse_index, nurse in enumerate(instance.nurses):
            days_off = nurse.days_off
            if days_off is None:
                continue

            for _date in days_off:
                if _date in date_to_index:
                    model.add_constraint(nurse_vars[nurse_index][date_to_index[_date]] == 0)

        return 0

class CoverRequirementsModuleTable(ShiftAssignmentModuleTable):
    """10th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_vars, dates):
        shift_by_uid = {shift.uid: shift for shift in instance.shifts}
        sorted_dates = sorted(dates)
        date_to_index = {d: i for i, d in enumerate(sorted_dates)}
        shift_uid_table = {}

        for _date, shift_uids in dates.items():
            for i, shift_uid in enumerate(shift_uids, start=1):
                shift_uid_table[shift_uid] = (_date, i)

        preferred_cover_vars = PreferredCoverDecisionVarsIP(shifts=instance.shifts, model=model)
        expr = 0

        for shift_uid, (_date, shift_index) in shift_uid_table.items():
            mapping = [0] * (len(dates[_date]) + 1)
            mapping[shift_index] = 1
            mapping = model.array(mapping)

            assigned_nurses = model.sum(
                model.at(mapping, nurse_vars[nurse_index][date_to_index[_date]])
                for nurse_index in range(len(instance.nurses))
            )

            model.add_constraint(
                assigned_nurses
                - preferred_cover_vars.total_above_preferred[shift_uid]
                + preferred_cover_vars.total_below_preferred[shift_uid]
                == shift_by_uid[shift_uid].demand
            )

            expr += (
                    shift_by_uid[shift_uid].weight_below_demand
                    * preferred_cover_vars.total_below_preferred[shift_uid]
            )
            expr += (
                    shift_by_uid[shift_uid].weight_above_demand
                    * preferred_cover_vars.total_above_preferred[shift_uid]
            )

        return expr


