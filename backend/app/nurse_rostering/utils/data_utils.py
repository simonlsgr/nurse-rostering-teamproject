from nurse_rostering.data_schema import NurseRosteringInstance, ShiftUid
from datetime import date
from typing import Any
from datetime import timedelta


def group_shifts_by_date(instance: NurseRosteringInstance) -> dict[date, list[ShiftUid]]:
    shifts_by_date = {}
    for shift in instance.shifts:
        current_date = shift.start_time.date()
        shifts_by_date.setdefault(current_date, []).append(shift.uid)
    return shifts_by_date


def get_shift_type_dict(instance: NurseRosteringInstance) -> dict[ShiftUid, list[str]]:
    shift_type_dict = {}
    for shift in instance.shifts:
        shift_type_dict[shift.uid] = shift.not_followed_by_shift_types
    return shift_type_dict


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