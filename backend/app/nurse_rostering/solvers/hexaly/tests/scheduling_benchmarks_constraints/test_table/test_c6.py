import datetime

from nurse_rostering.data_schema import Shift, Nurse, NurseRosteringInstance
from nurse_rostering.solvers.hexaly.model.modules_table import MinimumConsecutiveShiftsModuleTable
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVarsTable
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.utils.data_utils import group_shifts_by_date


def test_minimum_consecutive_shifts_feasible_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 2, 8, 0),
            end_time=datetime.datetime(2018, 1, 2, 16, 0),
            name="Morning Shift",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 3, 8, 0),
            end_time=datetime.datetime(2018, 1, 3, 16, 0),
            name="Morning Shift",
        ),
    ]

    nurse1 = Nurse(
        name="n1",
        minimum_consecutive_shifts=3,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )

    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    dates = group_shifts_by_date(instance)

    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(nurse1, shifts, model, dates)

        MinimumConsecutiveShiftsModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 1), 1)
        nv.fix(datetime.date(2018, 1, 2), 1)
        nv.fix(datetime.date(2018, 1, 3), 1)


def test_minimum_consecutive_shifts_infeasible_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 2, 8, 0),
            end_time=datetime.datetime(2018, 1, 2, 16, 0),
            name="Morning Shift",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 3, 8, 0),
            end_time=datetime.datetime(2018, 1, 3, 16, 0),
            name="Morning Shift",
        ),
    ]

    nurse1 = Nurse(
        name="n1",
        minimum_consecutive_shifts=2,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )

    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    dates = group_shifts_by_date(instance)

    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(nurse1, shifts, model, dates)

        MinimumConsecutiveShiftsModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 1), 0)
        nv.fix(datetime.date(2018, 1, 2), 1)
        nv.fix(datetime.date(2018, 1, 3), 0)