import datetime

from nurse_rostering.data_schema import NurseRosteringInstance, Shift
from nurse_rostering.solvers.hexaly.model.modules_table import ShiftRotationModuleTable
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVarsTable
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.utils._generate import create_nurse
from nurse_rostering.utils.data_utils import group_shifts_by_date


def test_shift_rotation_infeasible_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
            type="A",
            not_followed_by_shift_types={"B"},
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 2, 8, 0),
            end_time=datetime.datetime(2018, 1, 2, 16, 0),
            name="Morning Shift",
            type="B",
        ),
    ]

    nurse1 = create_nurse("N1")
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    dates = group_shifts_by_date(instance)

    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(nurse1, shifts, model, dates)

        ShiftRotationModuleTable().build(instance, model, [nv], dates)

        # 2018-01-01: einzige Schicht -> Index 1
        nv.fix(datetime.date(2018, 1, 1), 1)

        # 2018-01-02: einzige Schicht -> Index 1
        nv.fix(datetime.date(2018, 1, 2), 1)


def test_shift_rotation_feasible_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
            type="A",
            not_followed_by_shift_types={"B"},
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 3, 8, 0),
            end_time=datetime.datetime(2018, 1, 3, 16, 0),
            name="Morning Shift",
            type="B",
        ),
    ]

    nurse1 = create_nurse("N1")
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    dates = group_shifts_by_date(instance)

    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(nurse1, shifts, model, dates)

        ShiftRotationModuleTable().build(instance, model, [nv], dates)

        # 2018-01-01: einzige Schicht -> Index 1
        nv.fix(datetime.date(2018, 1, 1), 1)

        # 2018-01-03: einzige Schicht -> Index 1
        nv.fix(datetime.date(2018, 1, 3), 1)