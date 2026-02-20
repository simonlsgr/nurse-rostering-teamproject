from __future__ import annotations

from datetime import datetime, timedelta, date
from typing import Dict, List

from nurse_rostering.data_schema import Nurse, Shift, NurseRosteringInstance
from nurse_rostering.solvers.cp_sat.model.solver import NurseRosteringModel
from nurse_rostering.utils.validation import (
    assert_solution_is_feasible,
)


def dt(y: int, m: int, d: int, hh: int, mm: int = 0) -> datetime:
    return datetime(y, m, d, hh, mm)


def build_instance() -> NurseRosteringInstance:
    # 7 Tage, 3 Schichten pro Tag (early/late/night) => 21 shifts
    start_day = date(2026, 3, 2)  # Montag

    shifts: List[Shift] = []
    for i in range(7):
        day = start_day + timedelta(days=i)

        # early 07-15
        shifts.append(
            Shift(
                name=f"{day.isoformat()} early",
                start_time=dt(day.year, day.month, day.day, 7),
                end_time=dt(day.year, day.month, day.day, 15),
                demand=3,
                type="early",
                not_followed_by_shift_types=None,
                weight_below_demand=2,
                weight_above_demand=1,
            )
        )

        # late 15-23
        shifts.append(
            Shift(
                name=f"{day.isoformat()} late",
                start_time=dt(day.year, day.month, day.day, 15),
                end_time=dt(day.year, day.month, day.day, 23),
                demand=3,
                type="late",
                not_followed_by_shift_types={"early"},  # Beispielregel (kannst du weglassen)
                weight_below_demand=2,
                weight_above_demand=1,
            )
        )

        # night 23-07 next day
        next_day = day + timedelta(days=1)
        shifts.append(
            Shift(
                name=f"{day.isoformat()} night",
                start_time=dt(day.year, day.month, day.day, 23),
                end_time=dt(next_day.year, next_day.month, next_day.day, 7),
                demand=2,
                type="night",
                not_followed_by_shift_types={"early", "late"},
                weight_below_demand=5,
                weight_above_demand=1,
            )
        )


    shifts.sort(key=lambda s: s.start_time)

    all_uids = [s.uid for s in shifts]

    nurses: List[Nurse] = []

    # 10 Nurses
    for idx in range(10):

        preferred = set(all_uids[idx: idx + 6])
        preferred_off = set(all_uids[3 * idx: 3 * idx + 2])

        days_off = None
        if idx % 3 == 0:
            days_off = {start_day + timedelta(days=idx % 7)}

        nurses.append(
            Nurse(
                name=f"Nurse_{idx+1}",
                preferred_shifts=preferred,
                preferred_off_shifts=preferred_off,
                blocked_shifts=set(),
                days_off=days_off,
                staff=(idx < 7),
                min_time_between_shifts=timedelta(hours=11),
                preferred_shift_weight={uid: 3 for uid in preferred},
                preferred_off_shift_weight={uid: 2 for uid in preferred_off},
                minimum_work_time=60 * 0,
                maximum_work_time=60 * 40,
                minimum_consecutive_shifts=1,
                maximum_consecutive_shifts=5,
                minimum_consecutive_days_off=1,
                maximum_weekends=1,
                maximum_number_of_shifts_per_type={"night": 2},
            )
        )

    return NurseRosteringInstance(nurses=nurses, shifts=shifts, staff_weight=1)


def build_hints(instance: NurseRosteringInstance) -> Dict[int, List[Shift]]:
    shifts = instance.shifts

    def shifts_of_type(t: str) -> List[int]:
        return [s.uid for s in shifts if s.type == t]

    early = shifts_of_type("early")
    late = shifts_of_type("late")
    night = shifts_of_type("night")

    hints: Dict[int, List[int]] = {}

    n0 = instance.nurses[0].uid
    hints[n0] = [early[0], early[2]]

    # Nurse 1: late Tag 2
    n1 = instance.nurses[1].uid
    hints[n1] = [late[1]]

    # Nurse 2: night Tag 1 & 2
    n2 = instance.nurses[2].uid
    hints[n2] = [night[0], night[1]]
    n3 = instance.nurses[3].uid
    hints[n3] = [early[3], late[3]]

    return hints


def test_hints():
    instance = build_instance()
    hints = build_hints(instance)

    # print("Hints summary (nurse_uid -> [shift.name,...]):")
    # for nurse_uid, shs in hints.items():
    #     print(f"  {nurse_uid}: {[s.name for s in shs]}")

    model = NurseRosteringModel(instance=instance, hints=hints)

    sol = model.solve(
        log_search_progress=True,
        max_time_in_seconds=10.0,
        num_search_workers=8,
    )

    print("\nSolved!")
    print("Return status:", sol.return_status)
    print("Objective:", sol.objective_value)
    print("Lower bound:", sol.lower_bound)
    if sol is not None:
        assert_solution_is_feasible(instance, sol)

    model = NurseRosteringModel(instance=instance)

    sol2 = model.solve(
        log_search_progress=True,
        max_time_in_seconds=10.0,
        num_search_workers=8,
    )

    if sol2 is not None:
        assert_solution_is_feasible(instance, sol2)

    # kleine Ausgabe: erste 5 Schichten, wer zugeordnet wurde
    print("\nAssignments (first 5 shifts):")
    for sh in instance.shifts[:5]:
        assigned = sol.nurses_at_shifts.get(sh.uid, [])
        print(f"  {sh.name}: {assigned}")

    print("+"*20)
    print("\nAssignments (first 5 shifts):")
    for sh in instance.shifts[:5]:
        assigned = sol2.nurses_at_shifts.get(sh.uid, [])
        print(f"  {sh.name}: {assigned}")


if __name__ == "__main__":
    test_hints()
