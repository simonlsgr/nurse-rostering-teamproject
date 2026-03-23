import abc
from datetime import timedelta, date
from typing import Any

from hexaly.optimizer import HxModel, HxExpression

from nurse_rostering.data_schema import NurseRosteringInstance, Shift, ShiftUid
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVarsTable, PreferredCoverDecisionVarsIP
from nurse_rostering.utils.data_utils import get_types_and_length_in_instance, group_shifts_by_date, get_weekends, \
    get_shift_type_dict


class ShiftAssignmentModuleTable(abc.ABC):
    @abc.abstractmethod
    def build(
            self,
            instance: NurseRosteringInstance,
            model: HxModel,
            nurse_shift_vars: NurseDecisionVarsTable,
    ) -> HxExpression:
        """
        Add constraints and optionally return a sub-objective expression.
        Each subclass defines one constraint or objective aspect.
        """
        return 0


class OneShiftPerDayModuleTable(ShiftAssignmentModuleTable):
    """1st constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars):
        """
        Enforce that each nurse works at most one shift per day.
        """
        # Implicit
        return 0


class ShiftRotationModuleTable(ShiftAssignmentModuleTable):
    """2nd constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars):
        """
        Enforce minimum rest time between any two shifts for a nurse.
        """

        for nurse in instance.nurses:
            nurse_index = nurse_shift_vars.get_nurse_index(nurse.uid)
            for _date, shift_uids in nurse_shift_vars.dates.items():
                date_index = nurse_shift_vars.get_date_index(_date)
                if date_index is None:
                    continue
                following_date = _date + timedelta(days=1)
                if following_date not in nurse_shift_vars.dates:
                    continue
                following_date_index = nurse_shift_vars.get_date_index(following_date)
                for stype, stype_int in nurse_shift_vars.type_to_int.items():
                    stype_not_followed_by_types = nurse_shift_vars.type_not_followed_by_types[stype]
                    if stype_not_followed_by_types is not None:
                        for not_followed_type in stype_not_followed_by_types:
                            model.add_constraint(
                                model.not_(
                                    model.and_(
                                        nurse_shift_vars[nurse_index][date_index] == stype_int,
                                        nurse_shift_vars[nurse_index][following_date_index] ==
                                        nurse_shift_vars.type_to_int[not_followed_type]
                                    )

                                )
                            )
        return 0  # no objective contribution


class MaximumShiftTypesModuleTable(ShiftAssignmentModuleTable):

    def build(self, instance, model, nurse_shift_vars):

        for nurse in instance.nurses:
            nurse_index = nurse_shift_vars.get_nurse_index(nurse.uid)
            for stype, max_shifts_of_type in nurse.maximum_number_of_shifts_per_type.items():
                if max_shifts_of_type is not None:
                    of_type_t = model.lambda_function(lambda t: nurse_shift_vars.type_to_int[stype] == t)
                    model.constraint(
                        model.sum(
                            nurse_shift_vars[nurse_index],
                            of_type_t
                        ) <= max_shifts_of_type
                    )

        return 0


class MaximizePreferencesTable(ShiftAssignmentModuleTable):
    def build(self, instance, model, nurse_shift_vars):
        """
        Encourage assigning nurses to their preferred shifts.

        Minimization objective:
        For each preferred shift that is not assigned, its weight is paid.
        """
        expr = 0

        for nurse in instance.nurses:
            nurse_index = nurse_shift_vars.get_nurse_index(nurse.uid)
            for _date, shift_uids in nurse_shift_vars.dates.items():
                date_index = nurse_shift_vars.get_date_index(_date)
                if date_index is None:
                    continue
                for shift_uid in shift_uids:
                    if shift_uid in nurse.preferred_shifts:
                        _, type_int = nurse_shift_vars.get_shift_date_and_index(shift_uid)
                        expr += nurse.preferred_shift_weight[shift_uid] * (
                                    1 - (nurse_shift_vars[nurse_index][date_index] == type_int))
                    elif shift_uid in nurse.preferred_off_shifts:
                        _, type_int = nurse_shift_vars.get_shift_date_and_index(shift_uid)
                        expr += nurse.preferred_off_shift_weight[shift_uid] * (
                                    nurse_shift_vars[nurse_index][date_index] == type_int)
        return expr


# class PreferStaffModuleTable(ShiftAssignmentModuleTable):
#     def build(self, instance, model, nurse_shift_vars):
#         """
#         Penalize use of non-staff (contract) nurses in the objective.
#         """
#         expr = 0
#         _dict = {}
#         for _date, shift_uids in nurse_shift_vars.dates.items():
#             _dict[_date] = model.array([0] + len(shift_uids) * [1])

#         for nv in nurse_shift_vars:
#             if not nv.nurse.staff:
#                 for _date in nurse_shift_vars.dates:
#                     expr += instance.staff_weight * model.at(_dict[_date], nv.is_assigned_to(_date))
#         return expr


class LimitWorkTimeModuleTable(ShiftAssignmentModuleTable):
    """4th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars):
        durations_by_type = get_types_and_length_in_instance(instance)

        for nurse in instance.nurses:
            nurse_index = nurse_shift_vars.get_nurse_index(nurse.uid)
            min_time = nurse.minimum_work_time
            max_time = nurse.maximum_work_time
            if min_time is None and max_time is None:
                continue
            working_time = 0

            for stype, type_int in nurse_shift_vars.type_to_int.items():
                of_type_t = model.lambda_function(lambda t: t == type_int)
                working_time += model.sum(
                    nurse_shift_vars[nurse_index],
                    of_type_t
                ) * durations_by_type[stype]

            if min_time is not None:
                model.add_constraint(working_time >= min_time)
            if max_time is not None:
                model.add_constraint(working_time <= max_time)
        return 0


class MaximumConsecutiveShiftsModuleTable(ShiftAssignmentModuleTable):
    """5th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars):

        for nurse in instance.nurses:
            nurse_index = nurse_shift_vars.get_nurse_index(nurse.uid)
            for d in range(instance.planning_horizon_in_days - nurse.maximum_consecutive_shifts):
                model.constraint(
                    model.sum(
                        nurse_shift_vars[nurse_index][j] > 0
                        for j in range(d, d + nurse.maximum_consecutive_shifts + 1)
                    ) <= nurse.maximum_consecutive_shifts
                )
        return 0


class MinimumConsecutiveShiftsModuleTable(ShiftAssignmentModuleTable):
    """6th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars):

        for nurse in instance.nurses:
            nurse_index = nurse_shift_vars.get_nurse_index(nurse.uid)
            for s in range(1, nurse.minimum_consecutive_shifts):
                for d in range(instance.planning_horizon_in_days - (s + 1)):
                    model.constraint(
                        (nurse_shift_vars[nurse_index][d] >= 1) +
                        (
                                s - model.sum(
                            nurse_shift_vars[nurse_index][j] >= 1
                            for j in range(d + 1, d + s + 1)
                        )
                        ) +
                        (nurse_shift_vars[nurse_index][d + s + 1] >= 1)
                        >= 1
                    )
        return 0


class MinimumConsecutiveDaysOffModuleTable(ShiftAssignmentModuleTable):
    """7th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars):

        for nurse in instance.nurses:
            nurse_index = nurse_shift_vars.get_nurse_index(nurse.uid)
            for s in range(1, nurse.minimum_consecutive_days_off):
                for d in range(instance.planning_horizon_in_days - (s + 1)):
                    model.constraint(
                        1 - (nurse_shift_vars[nurse_index][d] >= 1) +
                        (
                            model.sum(
                                nurse_shift_vars[nurse_index][j] >= 1
                                for j in range(d + 1, d + s + 1)
                            )
                        ) +
                        1 - (nurse_shift_vars[nurse_index][d + s + 1] >= 1)
                        >= 1
                    )
        return 0


class MaximumNumberOfWeekendsModuleTable(ShiftAssignmentModuleTable):
    """8th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars):
        weekends = get_weekends(instance)
        if not weekends:
            return 0

        for nurse in instance.nurses:
            max_weekends = nurse.maximum_weekends
            if max_weekends is None:
                continue
            nurse_index = nurse_shift_vars.get_nurse_index(nurse.uid)

            max_weekends = nurse.maximum_weekends
            if max_weekends is None:
                continue
            expr = 0

            model.add_constraint(
                model.sum(
                    (
                            nurse_shift_vars[nurse_index][i * 7 + 5] +
                            nurse_shift_vars[nurse_index][i * 7 + 6]
                    ) >= 1
                    for i in range(0, instance.planning_horizon_in_days // 7)
                ) <= max_weekends
            )
        return 0


class DaysOffModuleTable(ShiftAssignmentModuleTable):
    """9th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars):
        for nurse in instance.nurses:
            nurse_index = nurse_shift_vars.get_nurse_index(nurse.uid)
            for off_day in nurse.days_off:
                d = nurse_shift_vars.get_date_index(off_day)
                model.add_constraint(nurse_shift_vars[nurse_index][d] == 0)
        return 0


class CoverRequirementsModuleTable(ShiftAssignmentModuleTable):
    """10th constraint in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf"""

    def build(self, instance, model, nurse_shift_vars):
        preferred_cover_vars = PreferredCoverDecisionVarsIP(instance, model=model)

        expr = 0
        for shift in instance.shifts:
            shift_index = nurse_shift_vars.get_date_index(shift.start_time.date())
            model.add_constraint(
                model.sum(
                    nurse_shift_vars[nurse_shift_vars.get_nurse_index(nurse.uid)][shift_index] ==
                    nurse_shift_vars.type_to_int[shift.type]
                    for nurse in instance.nurses
                )
                - preferred_cover_vars.total_above_preferred[shift.uid]
                + preferred_cover_vars.total_below_preferred[shift.uid] == shift.demand
            )
            expr += shift.weight_below_demand * preferred_cover_vars.total_below_preferred[shift.uid]
            expr += shift.weight_above_demand * preferred_cover_vars.total_above_preferred[shift.uid]

        return expr