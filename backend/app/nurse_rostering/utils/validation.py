"""
This module contains validation functions for nurse rostering solutions.
It is solver and algorithm agnostic, meaning it can be used to validate solutions
from any solver that produces a `NurseRosteringSolution` object. Just by providing
such functions, you have done a huge step towards computing a solution as now you
have a clean specification of what a valid and good solution looks like.
"""

from collections import defaultdict
from datetime import timedelta

from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution


def assert_consistent_uids(
    instance: NurseRosteringInstance, solution: NurseRosteringSolution
):
    """
    Assert that all UIDs in the solution are part of the instance.
    """
    nurse_uids = {n.uid for n in instance.nurses}
    shift_uids = {s.uid for s in instance.shifts}
    for shift_uid, nurse_list in solution.nurses_at_shifts.items():
        if shift_uid not in shift_uids:
            raise AssertionError(f"Shift {shift_uid} is not present in the instance.")
        for nurse_uid in nurse_list:
            if nurse_uid not in nurse_uids:
                raise AssertionError(
                    f"Nurse {nurse_uid} is not present in the instance."
                )


def assert_no_blocked_shifts(
    instance: NurseRosteringInstance, solution: NurseRosteringSolution
):
    """
    Assert that no nurse is assigned to a blocked shift in the solution.
    """
    for nurse in instance.nurses:
        for shift_uid in nurse.blocked_shifts:
            if (
                shift_uid in solution.nurses_at_shifts
                and nurse.uid in solution.nurses_at_shifts[shift_uid]
            ):
                raise AssertionError(
                    f"Nurse {nurse.uid} is assigned to blocked shift {shift_uid}."
                )


def assert_demand_satisfaction(
    instance: NurseRosteringInstance, solution: NurseRosteringSolution
):
    """
    Assert that each shift meets its nurse demand.
    """
    for shift in instance.shifts:
        assigned = solution.nurses_at_shifts.get(shift.uid, [])
        if len(assigned) < shift.demand:
            raise AssertionError(
                f"Shift {shift.uid} demand not met: {len(assigned)}/{shift.demand} assigned."
            )


def assert_min_time_between_shifts(
    instance: NurseRosteringInstance, solution: NurseRosteringSolution
):
    """
    Assert that nurses are not assigned to shifts too close together.
    """
    shifts_by_uid = {s.uid: s for s in instance.shifts}
    nurse_to_shifts = defaultdict(list)
    for shift_uid, nurse_uids in solution.nurses_at_shifts.items():
        for nurse_uid in nurse_uids:
            nurse_to_shifts[nurse_uid].append(shifts_by_uid[shift_uid])
    for nurse in instance.nurses:
        assigned = sorted(nurse_to_shifts[nurse.uid], key=lambda s: s.start_time)
        for a, b in zip(assigned, assigned[1:]):
            if b.start_time < a.end_time + nurse.min_time_between_shifts:
                raise AssertionError(
                    f"Nurse {nurse.uid} assigned to shifts {a.uid} and {b.uid} with insufficient rest."
                )


def assert_limit_worktime(
    instance: NurseRosteringInstance, solution: NurseRosteringSolution
):
    
    shifts_by_uid = {s.uid: s for s in instance.shifts}
    nurses_by_uid = {n.uid: n for n in instance.nurses}
    nurse_to_shifts = defaultdict(list)
    for shift_uid, nurse_uids in solution.nurses_at_shifts.items():
        for nurse_uid in nurse_uids:
            nurse_to_shifts[nurse_uid].append(shifts_by_uid[shift_uid])
    
    for nurse_uid, shifts in nurse_to_shifts.items():
        total = sum(int((s.end_time - s.start_time).total_seconds() // 60) for s in shifts)
        nurse = nurses_by_uid[nurse_uid]
        if nurse.maximum_work_time is None:
            continue
            raise Warning(f"No maximum work time was supplied for nurse {nurse_uid}.")
        if total > nurse.maximum_work_time:
            raise AssertionError(
                f"Nurse {nurse_uid} works: {total}, allowed: {nurse.maximum_work_time}"
            )


def assert_maximum_consecutive_shifts(
    instance: NurseRosteringInstance, solution: NurseRosteringSolution
):
    shifts_by_uid = {s.uid: s for s in instance.shifts}
    nurses_by_uid = {n.uid: n for n in instance.nurses}
    nurse_work_days = {}
    for shift_uid, nurse_uids in solution.nurses_at_shifts.items():
        for nurse_uid in nurse_uids:
            start = shifts_by_uid[shift_uid].start_time.date()
            end = shifts_by_uid[shift_uid].end_time.date()
            while start <= end:
                nurse_work_days.setdefault(nurse_uid, set()).add(start)
                start += timedelta(days=1)
    for nurse_uid, nurse in nurses_by_uid.items():
        max_cons = nurse.maximum_consecutive_shifts
        if max_cons is None:
            continue
        nurse_shifts = sorted(nurse_work_days.get(nurse_uid, set()))
        if not nurse_shifts:
            continue
        counter = 1
        for i in range(len(nurse_shifts)-1):
            if (nurse_shifts[i+1] - nurse_shifts[i]).days == 1:
                counter += 1
                if counter > max_cons:
                    raise AssertionError(
                        f"Nurse {nurse_uid} has to many consecutive shifts: {counter}, allowed: {max_cons}"
                    )
            else:
                counter = 1


def assert_minimum_consecutive_shifts(
    instance: NurseRosteringInstance, solution: NurseRosteringSolution
):
    shifts_by_uid = {s.uid: s for s in instance.shifts}
    nurses_by_uid = {n.uid: n for n in instance.nurses}
    nurse_work_days = {}
    for shift_uid, nurse_uids in solution.nurses_at_shifts.items():
        for nurse_uid in nurse_uids:
            start = shifts_by_uid[shift_uid].start_time.date()
            end = shifts_by_uid[shift_uid].end_time.date()
            while start <= end:
                nurse_work_days.setdefault(nurse_uid, set()).add(start)
                start += timedelta(days=1)
    for nurse_uid, nurse in nurses_by_uid.items():
        min_cons = nurse.minimum_consecutive_shifts
        if min_cons is None:
            continue
        nurse_shifts = sorted(nurse_work_days.get(nurse_uid, set()))
        if not nurse_shifts:
            continue
        counter = 1
        for i in range(len(nurse_shifts) - 1):
            if (nurse_shifts[i + 1] - nurse_shifts[i]).days == 1:
                counter += 1
            else:
                if counter < min_cons:
                    raise AssertionError(
                        f"Nurse {nurse_uid} has not enough consecutive shifts: {counter}, allowed: {min_cons}"
                    )
                counter = 1
        if counter < min_cons:
            raise AssertionError(
                f"Nurse {nurse_uid} has not enough consecutive shifts: {counter}, allowed: {min_cons}"
            )


def assert_minimum_consecutive_days_off(
    instance: NurseRosteringInstance, solution: NurseRosteringSolution
):
    shifts_by_uid = {s.uid: s for s in instance.shifts}
    nurses_by_uid = {n.uid: n for n in instance.nurses}
    nurse_work_days = {}
    for shift_uid, nurse_uids in solution.nurses_at_shifts.items():
        for nurse_uid in nurse_uids:
            start = shifts_by_uid[shift_uid].start_time.date()
            end = shifts_by_uid[shift_uid].end_time.date()
            while start <= end:
                nurse_work_days.setdefault(nurse_uid, set()).add(start)
                start += timedelta(days=1)
    for nurse_uid, nurse in nurses_by_uid.items():
        min_days_off = nurse.minimum_consecutive_days_off
        if min_days_off is None:
            continue
        nurse_shifts = sorted(nurse_work_days.get(nurse_uid, set()))
        if not nurse_shifts:
            continue
        for i in range(len(nurse_shifts) - 1):
            days_off = (nurse_shifts[i + 1] - nurse_shifts[i]).days - 1
            if 1 < days_off < min_days_off:
                    raise AssertionError(
                        f"Nurse {nurse_uid} has not enough days off: {days_off}, allowed: {min_days_off}"
                    )


def assert_maximum_number_of_weekends(
    instance: NurseRosteringInstance, solution: NurseRosteringSolution
):
    shifts_by_uid = {s.uid: s for s in instance.shifts}
    nurses_by_uid = {n.uid: n for n in instance.nurses}
    weekends = {}
    for shift_uid, nurse_uids in solution.nurses_at_shifts.items():
        for nurse_uid in nurse_uids:
            start = shifts_by_uid[shift_uid].start_time.date()
            end = shifts_by_uid[shift_uid].end_time.date()
            while start <= end:
                if start.weekday() >= 5:
                    saturday = start if start.weekday() == 5 else (start- timedelta(days=1))
                    weekends.setdefault(nurse_uid, set()).add(saturday)
                start += timedelta(days=1)
    for nurse_uid, nurse in nurses_by_uid.items():
        max_weekends = nurse.maximum_weekends
        if max_weekends is None:
            continue
        nurse_weekends = weekends.get(nurse_uid, set())
        if not nurse_weekends:
            continue
        worked_weekends = len(nurse_weekends)

        if worked_weekends > max_weekends:
            raise AssertionError(
                f"Nurse {nurse_uid} worked on too many weekends: {worked_weekends}, {max_weekends} allowed"
            )



def objective_value(
    instance: NurseRosteringInstance, solution: NurseRosteringSolution
) -> int:
    """
    Calculate the objective value of the solution based on the instance's preferences and staff assignments.
    This function is to be implemented with CP-SAT.
    """
    nurses_by_uid = {n.uid: n for n in instance.nurses}
    obj_val = 0
    for shift_uid, nurse_uids in solution.nurses_at_shifts.items():
        for nurse_uid in nurse_uids:
            nurse = nurses_by_uid[nurse_uid]
            if shift_uid in nurse.preferred_shifts:
                # This is a minimization problem, so we we subtract the weight for preferred shifts
                obj_val -= nurse.preferred_shift_weight
            if not nurse.staff:
                # Add the penalty for assigning a non-staff nurse (they are more expensive)
                obj_val += instance.staff_weight
    return obj_val


def assert_solution_is_feasible(
    instance: NurseRosteringInstance,
    solution: NurseRosteringSolution,
    check_objective: bool = True,
):
    """
    Run all standard feasibility checks.
    """
    assert_consistent_uids(instance, solution)
    assert_no_blocked_shifts(instance, solution)
    # assert_shift_limits(instance, solution)
    assert_demand_satisfaction(instance, solution)
    assert_min_time_between_shifts(instance, solution)
    assert_limit_worktime(instance, solution)
    assert_maximum_consecutive_shifts(instance, solution)
    assert_minimum_consecutive_shifts(instance, solution)
    assert_minimum_consecutive_days_off(instance, solution)
    assert_maximum_number_of_weekends(instance, solution)
    if check_objective:
        obj_val = objective_value(instance, solution)
        if obj_val != solution.objective_value:
            raise AssertionError(
                f"Objective value mismatch: expected {obj_val}, got {solution.objective_value}."
            )