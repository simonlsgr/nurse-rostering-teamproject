from nurse_rostering.utils.output import print_instance_and_solution
from nurse_rostering.utils.generate_random_instance import generate_random_instance
from nurse_rostering.solvers.gurobi.model.solver import NurseRosteringModel
from nurse_rostering.utils.validation import (
    assert_solution_is_feasible,
)
from datetime import datetime, timedelta
from nurse_rostering.data_schema import Nurse, Shift, NurseRosteringInstance


def test_random_instances():
    """
    Test the generation of random nurse rostering instances.
    This function creates a random instance and checks if it can be solved.
    """

    instance = generate_random_instance(num_nurses=12, num_days=14, staff_ratio=0.5)

    model = NurseRosteringModel(instance)
    solution = model.solve()
    assert_solution_is_feasible(instance, solution)
    assert solution is not None, "The solution should not be None"
    assert len(solution.nurses_at_shifts) > 0, (
        "There should be at least one nurse assigned to a shift"
    )


def test_fixed_instance():
    """
    Detailed comments can be found in solvers/cp_sat/tests/test_full_instances.py
    """

    base_date = datetime(2025, 1, 1)
    shift_length = 8
    shifts = []

    # 7 days, 3 shifts/day = 21 shifts
    for day in range(7):
        for idx, hour in enumerate([0, 8, 16]):  # Morning, Day, Night
            start = base_date + timedelta(days=day, hours=hour)
            end = start + timedelta(hours=shift_length)
            shifts.append(
                Shift(
                    name=f"Day {day + 1} Shift {idx + 1}",
                    start_time=start,
                    end_time=end,
                    demand=2 if hour == 8 else 1,  # Higher demand for day shifts
                )
            )

    # Total demand: 7*2 (day) + 7*1 (morning) + 7*1 (night) = 28 + 7 + 7 = 42 shifts needed

    # 8 nurses * 6 shifts max = 48 shifts possible ⇒ feasible

    nurses = [
        Nurse(
            name="Alice (prefers mornings, no Sundays)",
            preferred_shifts={s.uid for s in shifts if s.start_time.hour == 0},
            blocked_shifts={s.uid for s in shifts if s.start_time.weekday() == 6},
            staff=True,
            min_time_between_shifts=timedelta(hours=10),
            preferred_shift_weight=3,
        ),
        Nurse(
            name="Bob (prefers nights)",
            preferred_shifts={s.uid for s in shifts if s.start_time.hour == 16},
            blocked_shifts=set(),
            staff=True,
            min_time_between_shifts=timedelta(hours=10),
            preferred_shift_weight=3,
        ),
        Nurse(
            name="Clara (prefers weekends, blocks weekdays)",
            preferred_shifts={
                s.uid for s in shifts if s.start_time.weekday() in {5, 6}
            },
            blocked_shifts={s.uid for s in shifts if s.start_time.weekday() < 5},
            staff=True,
            min_time_between_shifts=timedelta(hours=10),
            preferred_shift_weight=2,
        ),
        Nurse(
            name="Dan (no preferences)",
            preferred_shifts=set(),
            blocked_shifts=set(),
            staff=True,
            min_time_between_shifts=timedelta(hours=8),
            preferred_shift_weight=1,
        ),
        Nurse(
            name="Eve (contractor, prefers day shifts)",
            preferred_shifts={s.uid for s in shifts if s.start_time.hour == 8},
            blocked_shifts=set(),
            staff=False,
            min_time_between_shifts=timedelta(hours=10),
            preferred_shift_weight=2,
        ),
        Nurse(
            name="Frank (prefers day shifts)",
            preferred_shifts={s.uid for s in shifts if s.start_time.hour == 8},
            blocked_shifts=set(),
            staff=True,
            min_time_between_shifts=timedelta(hours=10),
            preferred_shift_weight=2,
        ),
        Nurse(
            name="Grace (prefers mornings)",
            preferred_shifts={s.uid for s in shifts if s.start_time.hour == 0},
            blocked_shifts=set(),
            staff=True,
            min_time_between_shifts=timedelta(hours=10),
            preferred_shift_weight=3,
        ),
        Nurse(
            name="Heidi (contractor, no preferences)",
            preferred_shifts=set(),
            blocked_shifts=set(),
            staff=False,
            min_time_between_shifts=timedelta(hours=8),
            preferred_shift_weight=1,
        ),
    ]

    instance = NurseRosteringInstance(
        nurses=nurses, shifts=sorted(shifts, key=lambda s: s.start_time), staff_weight=2
    )

    model = NurseRosteringModel(instance)
    solution = model.solve()
    assert solution is not None, "The solution should not be None"
    assert_solution_is_feasible(instance, solution)
    print_instance_and_solution(instance, solution)
