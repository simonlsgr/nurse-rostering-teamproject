import datetime

from nurse_rostering.data_schema import Shift, Nurse, NurseRosteringInstance
from nurse_rostering.solvers.hexaly.model.modules_table import MaximumShiftTypesModuleTable
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVarsTable
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.utils.data_utils import group_shifts_by_date


def test_maximum_shift_types_feasible_table():
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
            start_time=datetime.datetime(2018, 1, 2, 8, 0),
            end_time=datetime.datetime(2018, 1, 2, 16, 0),
            name="Morning Shift",
            type="B",
        ),
    ]

    nurse1 = Nurse(
        name="n1",
        maximum_number_of_shifts_per_type={"A": 1, "B": 1},
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )

    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    dates = group_shifts_by_date(instance)

    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(nurse1, shifts, model, dates)

        MaximumShiftTypesModuleTable().build(instance, model, [nv], dates)

        # an beiden Tagen jeweils die einzige Schicht -> Index 1
        nv.fix(datetime.date(2018, 1, 1), 1)
        nv.fix(datetime.date(2018, 1, 2), 1)


def test_maximum_shift_types_infeasible_table():
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
            start_time=datetime.datetime(2018, 1, 2, 8, 0),
            end_time=datetime.datetime(2018, 1, 2, 16, 0),
            name="Morning Shift",
            type="B",
        ),
    ]

    nurse1 = Nurse(
        name="n1",
        maximum_number_of_shifts_per_type={"A": 1, "B": 0},
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )

    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    dates = group_shifts_by_date(instance)

    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(nurse1, shifts, model, dates)

        MaximumShiftTypesModuleTable().build(instance, model, [nv], dates)

        # Tag 1: Typ A
        nv.fix(datetime.date(2018, 1, 1), 1)

        # Tag 2: Typ B, aber B max = 0
        nv.fix(datetime.date(2018, 1, 2), 1)