import datetime

import hexaly.optimizer as hx

from nurse_rostering.data_schema import Shift, Nurse, NurseRosteringInstance
from nurse_rostering.solvers.hexaly.model.modules_table import CoverRequirementsModuleTable
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVarsTable
from nurse_rostering.utils.data_utils import group_shifts_by_date


def _solve_cover(instance, fixed_assignments):
    """
    fixed_assignments: dict[nurse_name, dict[date, index]]
    """
    dates = group_shifts_by_date(instance)

    with hx.HexalyOptimizer() as optimizer:
        model = optimizer.model

        nurse_vars = {}
        nurse_vars_list = []
        for nurse in instance.nurses:
            nv = NurseDecisionVarsTable(nurse, instance.shifts, model, dates)
            nurse_vars[nurse.name] = nv
            nurse_vars_list.append(nv)

        goal = CoverRequirementsModuleTable().build(instance, model, nurse_vars_list, dates)

        for nurse_name, assignments in fixed_assignments.items():
            for _date, value in assignments.items():
                nurse_vars[nurse_name].fix(_date, value)

        model.minimize(goal)
        model.close()
        optimizer.solve()

        return optimizer.solution.status, goal.value


def test_cover_requirements_exact_cover_table():
    shifts = [
        Shift(
            demand=2,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
            weight_below_demand=10,
            weight_above_demand=5,
        ),
    ]

    nurse1 = Nurse(name="n1", preferred_shifts=set(), blocked_shifts=set(), staff=True,
                   min_time_between_shifts=datetime.timedelta(hours=0))
    nurse2 = Nurse(name="n2", preferred_shifts=set(), blocked_shifts=set(), staff=True,
                   min_time_between_shifts=datetime.timedelta(hours=0))

    instance = NurseRosteringInstance(nurses=[nurse1, nurse2], shifts=shifts)

    status, obj = _solve_cover(
        instance,
        {
            "n1": {datetime.date(2018, 1, 1): 1},
            "n2": {datetime.date(2018, 1, 1): 1},
        },
    )

    assert status == hx.HxSolutionStatus.OPTIMAL
    assert obj == 0


def test_cover_requirements_under_cover_table():
    shifts = [
        Shift(
            demand=2,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
            weight_below_demand=10,
            weight_above_demand=5,
        ),
    ]

    nurse1 = Nurse(name="n1", preferred_shifts=set(), blocked_shifts=set(), staff=True,
                   min_time_between_shifts=datetime.timedelta(hours=0))
    nurse2 = Nurse(name="n2", preferred_shifts=set(), blocked_shifts=set(), staff=True,
                   min_time_between_shifts=datetime.timedelta(hours=0))

    instance = NurseRosteringInstance(nurses=[nurse1, nurse2], shifts=shifts)

    status, obj = _solve_cover(
        instance,
        {
            "n1": {datetime.date(2018, 1, 1): 1},
            "n2": {datetime.date(2018, 1, 1): 0},
        },
    )

    assert status == hx.HxSolutionStatus.OPTIMAL
    assert obj == 10


def test_cover_requirements_over_cover_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
            weight_below_demand=10,
            weight_above_demand=5,
        ),
    ]

    nurse1 = Nurse(name="n1", preferred_shifts=set(), blocked_shifts=set(), staff=True,
                   min_time_between_shifts=datetime.timedelta(hours=0))
    nurse2 = Nurse(name="n2", preferred_shifts=set(), blocked_shifts=set(), staff=True,
                   min_time_between_shifts=datetime.timedelta(hours=0))

    instance = NurseRosteringInstance(nurses=[nurse1, nurse2], shifts=shifts)

    status, obj = _solve_cover(
        instance,
        {
            "n1": {datetime.date(2018, 1, 1): 1},
            "n2": {datetime.date(2018, 1, 1): 1},
        },
    )

    assert status == hx.HxSolutionStatus.OPTIMAL
    assert obj == 5

def test_cover_requirements_multiple_days_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Day1 Shift",
            weight_below_demand=7,
            weight_above_demand=3,
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 2, 8, 0),
            end_time=datetime.datetime(2018, 1, 2, 16, 0),
            name="Day2 Shift",
            weight_below_demand=11,
            weight_above_demand=4,
        ),
    ]

    nurse1 = Nurse(name="n1", preferred_shifts=set(), blocked_shifts=set(), staff=True,
                   min_time_between_shifts=datetime.timedelta(hours=0))

    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)

    status, obj = _solve_cover(
        instance,
        {
            "n1": {
                datetime.date(2018, 1, 1): 1,
                datetime.date(2018, 1, 2): 0,
            },
        },
    )

    assert status == hx.HxSolutionStatus.OPTIMAL
    assert obj == 11


def test_cover_requirements_same_day_two_shifts_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
            weight_below_demand=10,
            weight_above_demand=5,
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 16, 0),
            end_time=datetime.datetime(2018, 1, 2, 0, 0),
            name="Evening Shift",
            weight_below_demand=10,
            weight_above_demand=5,
        ),
    ]

    nurse1 = Nurse(name="n1", preferred_shifts=set(), blocked_shifts=set(), staff=True,
                   min_time_between_shifts=datetime.timedelta(hours=0))
    nurse2 = Nurse(name="n2", preferred_shifts=set(), blocked_shifts=set(), staff=True,
                   min_time_between_shifts=datetime.timedelta(hours=0))

    instance = NurseRosteringInstance(nurses=[nurse1, nurse2], shifts=shifts)

    status, obj = _solve_cover(
        instance,
        {
            "n1": {datetime.date(2018, 1, 1): 1},  # erste Schicht des Tages
            "n2": {datetime.date(2018, 1, 1): 2},  # zweite Schicht des Tages
        },
    )

    assert status == hx.HxSolutionStatus.OPTIMAL
    assert obj == 0


def test_cover_requirements_same_day_two_shifts_one_nurse_only_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
            weight_below_demand=10,
            weight_above_demand=5,
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 16, 0),
            end_time=datetime.datetime(2018, 1, 2, 0, 0),
            name="Evening Shift",
            weight_below_demand=10,
            weight_above_demand=5,
        ),
    ]

    nurse1 = Nurse(name="n1", preferred_shifts=set(), blocked_shifts=set(), staff=True,
                   min_time_between_shifts=datetime.timedelta(hours=0))

    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)

    status, obj = _solve_cover(
        instance,
        {
            "n1": {datetime.date(2018, 1, 1): 1},
        },
    )

    assert status == hx.HxSolutionStatus.OPTIMAL
    assert obj == 10


def test_cover_requirements_prefers_lower_penalty_choice_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Low penalty undercoverage",
            weight_below_demand=1,
            weight_above_demand=5,
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 16, 0),
            end_time=datetime.datetime(2018, 1, 2, 0, 0),
            name="High penalty undercoverage",
            weight_below_demand=100,
            weight_above_demand=5,
        ),
    ]

    nurse1 = Nurse(name="n1", preferred_shifts=set(), blocked_shifts=set(), staff=True,
                   min_time_between_shifts=datetime.timedelta(hours=0))

    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    dates = group_shifts_by_date(instance)

    with hx.HexalyOptimizer() as optimizer:
        model = optimizer.model

        nv = NurseDecisionVarsTable(instance, model)
        goal = CoverRequirementsModuleTable().build(instance, model, [nv])

        model.minimize(goal)
        model.close()
        optimizer.solve()

        assert optimizer.solution.status == hx.HxSolutionStatus.OPTIMAL
        assert goal.value == 1
        assert nv.(datetime.date(2018, 1, 1)).value == 2