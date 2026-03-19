import datetime

from nurse_rostering.data_schema import Shift, Nurse, NurseRosteringInstance
from nurse_rostering.solvers.hexaly.model.modules_table import DaysOffModuleTable
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVarsTable
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.utils.data_utils import group_shifts_by_date


def _make_days_off_instance(days_off):
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift 1",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 2, 8, 0),
            end_time=datetime.datetime(2018, 1, 2, 16, 0),
            name="Morning Shift 2",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 3, 8, 0),
            end_time=datetime.datetime(2018, 1, 3, 16, 0),
            name="Morning Shift 3",
        ),
    ]

    nurse = Nurse(
        name="n1",
        days_off=days_off,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )

    instance = NurseRosteringInstance(nurses=[nurse], shifts=shifts)
    dates = group_shifts_by_date(instance)
    return instance, nurse, shifts, dates


def test_days_off_feasible_table():
    instance, nurse, shifts, dates = _make_days_off_instance(
        days_off={datetime.date(2018, 1, 2)}
    )

    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        DaysOffModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 1), 1)
        nv.fix(datetime.date(2018, 1, 2), 0)
        nv.fix(datetime.date(2018, 1, 3), 1)


def test_days_off_infeasible_table():
    instance, nurse, shifts, dates = _make_days_off_instance(
        days_off={datetime.date(2018, 1, 2)}
    )

    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        DaysOffModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 1), 1)
        nv.fix(datetime.date(2018, 1, 2), 1)
        nv.fix(datetime.date(2018, 1, 3), 0)


def test_days_off_multiple_days_feasible_table():
    instance, nurse, shifts, dates = _make_days_off_instance(
        days_off={datetime.date(2018, 1, 1), datetime.date(2018, 1, 3)}
    )

    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        DaysOffModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 1), 0)
        nv.fix(datetime.date(2018, 1, 2), 1)
        nv.fix(datetime.date(2018, 1, 3), 0)


def test_days_off_multiple_days_infeasible_table():
    instance, nurse, shifts, dates = _make_days_off_instance(
        days_off={datetime.date(2018, 1, 1), datetime.date(2018, 1, 3)}
    )

    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        DaysOffModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 1), 1)
        nv.fix(datetime.date(2018, 1, 2), 0)
        nv.fix(datetime.date(2018, 1, 3), 0)


def test_days_off_no_days_off_feasible_table():
    instance, nurse, shifts, dates = _make_days_off_instance(days_off=set())

    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        DaysOffModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 1), 1)
        nv.fix(datetime.date(2018, 1, 2), 1)
        nv.fix(datetime.date(2018, 1, 3), 1)


def test_days_off_all_days_off_feasible_table():
    instance, nurse, shifts, dates = _make_days_off_instance(
        days_off={
            datetime.date(2018, 1, 1),
            datetime.date(2018, 1, 2),
            datetime.date(2018, 1, 3),
        }
    )

    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        DaysOffModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 1), 0)
        nv.fix(datetime.date(2018, 1, 2), 0)
        nv.fix(datetime.date(2018, 1, 3), 0)


def test_days_off_all_days_off_infeasible_table():
    instance, nurse, shifts, dates = _make_days_off_instance(
        days_off={
            datetime.date(2018, 1, 1),
            datetime.date(2018, 1, 2),
            datetime.date(2018, 1, 3),
        }
    )

    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        DaysOffModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 1), 0)
        nv.fix(datetime.date(2018, 1, 2), 1)
        nv.fix(datetime.date(2018, 1, 3), 0)


def test_days_off_with_multiple_shifts_same_day_infeasible_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift 1",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 16, 0),
            end_time=datetime.datetime(2018, 1, 2, 0, 0),
            name="Evening Shift 1",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 2, 8, 0),
            end_time=datetime.datetime(2018, 1, 2, 16, 0),
            name="Morning Shift 2",
        ),
    ]

    nurse = Nurse(
        name="n1",
        days_off={datetime.date(2018, 1, 1)},
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )

    instance = NurseRosteringInstance(nurses=[nurse], shifts=shifts)
    dates = group_shifts_by_date(instance)

    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        DaysOffModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 1), 2)
        nv.fix(datetime.date(2018, 1, 2), 0)