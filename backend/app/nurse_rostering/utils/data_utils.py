from nurse_rostering.data_schema import NurseRosteringInstance
from typing import Any


def group_shifts_by_date(instance: NurseRosteringInstance) -> dict[Any, list[Any]]:
    shifts_by_date = {}
    for shift in instance.shifts:
        current_date = shift.start_time.date()
        shifts_by_date.setdefault(current_date, []).append(shift.uid)
    return shifts_by_date


def get_shift_type_dict(instance: NurseRosteringInstance) -> dict[Any, list[Any]]:
    shift_type_dict = {}
    for shift in instance.shifts:
        shift_type_dict[shift.uid] = shift.not_followed_by_shift_types
    return shift_type_dict