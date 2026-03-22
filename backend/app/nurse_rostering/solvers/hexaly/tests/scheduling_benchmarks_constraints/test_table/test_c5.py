import datetime

from nurse_rostering.data_schema import Shift, Nurse, NurseRosteringInstance
from nurse_rostering.solvers.hexaly.model.modules_table import MaximumConsecutiveShiftsModuleTable
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVarsTable
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.utils.data_utils import group_shifts_by_date


def test_maximum_consecutive_shifts_feasible_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
            type="A",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
            type="B",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 2, 8, 0),
            end_time=datetime.datetime(2018, 1, 2, 16, 0),
            name="Morning Shift",
            type="A",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 2, 8, 0),
            end_time=datetime.datetime(2018, 1, 2, 16, 0),
            name="Morning Shift",
            type="B",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 3, 8, 0),
            end_time=datetime.datetime(2018, 1, 3, 16, 0),
            name="Morning Shift",
            type="A",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 3, 8, 0),
            end_time=datetime.datetime(2018, 1, 3, 16, 0),
            name="Morning Shift",
            type="B",
        ),
    ]

    nurse1 = Nurse(
        name="n1",
        maximum_consecutive_shifts=3,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )

    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)

    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(instance, model)

        MaximumConsecutiveShiftsModuleTable().build(instance, model, nv)

        nv.fix(nurse1.uid, shifts[0].uid, True)
        nv.fix(nurse1.uid, shifts[2].uid, True)
        nv.fix(nurse1.uid, shifts[4].uid, True)


def test_maximum_consecutive_shifts_infeasible_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
            type="A",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
            type="B",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 2, 8, 0),
            end_time=datetime.datetime(2018, 1, 2, 16, 0),
            name="Morning Shift",
            type="A",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 2, 8, 0),
            end_time=datetime.datetime(2018, 1, 2, 16, 0),
            name="Morning Shift",
            type="B",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 3, 8, 0),
            end_time=datetime.datetime(2018, 1, 3, 16, 0),
            name="Morning Shift",
            type="A",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 3, 8, 0),
            end_time=datetime.datetime(2018, 1, 3, 16, 0),
            name="Morning Shift",
            type="B",
        ),
    ]

    nurse1 = Nurse(
        name="n1",
        maximum_consecutive_shifts=2,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )

    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)

    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(instance, model)

        MaximumConsecutiveShiftsModuleTable().build(instance, model, nv)
        print(shifts[0])
        print(shifts[2])
        print(shifts[4])

        nv.fix(nurse1.uid, shifts[0].uid, True)
        nv.fix(nurse1.uid, shifts[2].uid, True)
        nv.fix(nurse1.uid, shifts[4].uid, True)
        
