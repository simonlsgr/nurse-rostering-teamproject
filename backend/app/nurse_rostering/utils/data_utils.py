from nurse_rostering.data_schema import NurseRosteringInstance
from typing import Any


def group_shifts_by_date(instance: NurseRosteringInstance) -> dict[Any, list[Any]]:
    shifts_by_date = {}
    for shift in instance.shifts:
        current_date = shift.start_time.date()
        shifts_by_date.setdefault(current_date, []).append(shift.uid)
    return shifts_by_date