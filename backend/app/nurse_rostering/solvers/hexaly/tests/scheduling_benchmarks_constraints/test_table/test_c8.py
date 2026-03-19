import datetime

from nurse_rostering.data_schema import Shift, Nurse, NurseRosteringInstance
from nurse_rostering.solvers.hexaly.model.modules_table import MaximumNumberOfWeekendsModuleTable
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVarsTable
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.utils.data_utils import group_shifts_by_date


def _make_instance(max_weekends=1):
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 6, 8, 0),   # Samstag
            end_time=datetime.datetime(2018, 1, 6, 16, 0),
            name="Saturday Shift 1",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 7, 8, 0),   # Sonntag
            end_time=datetime.datetime(2018, 1, 7, 16, 0),
            name="Sunday Shift 1",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 13, 8, 0),  # Samstag
            end_time=datetime.datetime(2018, 1, 13, 16, 0),
            name="Saturday Shift 2",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 14, 8, 0),  # Sonntag
            end_time=datetime.datetime(2018, 1, 14, 16, 0),
            name="Sunday Shift 2",
        ),
    ]

    nurse = Nurse(
        name="n1",
        maximum_weekends=max_weekends,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )

    instance = NurseRosteringInstance(nurses=[nurse], shifts=shifts)
    dates = group_shifts_by_date(instance)
    return instance, nurse, shifts, dates


def test_maximum_number_of_weekends_feasible_table():
    instance, nurse, shifts, dates = _make_instance(max_weekends=1)

    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 6), 1)
        nv.fix(datetime.date(2018, 1, 7), 1)
        nv.fix(datetime.date(2018, 1, 13), 0)
        nv.fix(datetime.date(2018, 1, 14), 0)


def test_maximum_number_of_weekends_infeasible_table():
    instance, nurse, shifts, dates = _make_instance(max_weekends=1)

    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 6), 1)
        nv.fix(datetime.date(2018, 1, 7), 1)
        nv.fix(datetime.date(2018, 1, 13), 1)
        nv.fix(datetime.date(2018, 1, 14), 1)


def test_maximum_number_of_weekends_counts_weekend_only_once_table():
    instance, nurse, shifts, dates = _make_instance(max_weekends=1)

    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 6), 1)
        nv.fix(datetime.date(2018, 1, 7), 1)
        nv.fix(datetime.date(2018, 1, 13), 0)
        nv.fix(datetime.date(2018, 1, 14), 0)


def test_maximum_number_of_weekends_single_day_on_weekend_still_counts_table():
    instance, nurse, shifts, dates = _make_instance(max_weekends=1)

    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 6), 1)
        nv.fix(datetime.date(2018, 1, 7), 0)
        nv.fix(datetime.date(2018, 1, 13), 0)
        nv.fix(datetime.date(2018, 1, 14), 1)


def test_maximum_number_of_weekends_zero_allowed_feasible_if_no_weekend_work_table():
    instance, nurse, shifts, dates = _make_instance(max_weekends=0)

    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 6), 0)
        nv.fix(datetime.date(2018, 1, 7), 0)
        nv.fix(datetime.date(2018, 1, 13), 0)
        nv.fix(datetime.date(2018, 1, 14), 0)


def test_maximum_number_of_weekends_zero_allowed_infeasible_if_any_weekend_work_table():
    instance, nurse, shifts, dates = _make_instance(max_weekends=0)

    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 6), 1)
        nv.fix(datetime.date(2018, 1, 7), 0)
        nv.fix(datetime.date(2018, 1, 13), 0)
        nv.fix(datetime.date(2018, 1, 14), 0)


def test_maximum_number_of_weekends_exactly_at_limit_table():
    instance, nurse, shifts, dates = _make_instance(max_weekends=2)

    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 6), 1)
        nv.fix(datetime.date(2018, 1, 7), 0)
        nv.fix(datetime.date(2018, 1, 13), 1)
        nv.fix(datetime.date(2018, 1, 14), 0)


def test_maximum_number_of_weekends_single_weekend_horizon_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 6, 8, 0),
            end_time=datetime.datetime(2018, 1, 6, 16, 0),
            name="Saturday Shift",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 7, 8, 0),
            end_time=datetime.datetime(2018, 1, 7, 16, 0),
            name="Sunday Shift",
        ),
    ]

    nurse = Nurse(
        name="n1",
        maximum_weekends=1,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )

    instance = NurseRosteringInstance(nurses=[nurse], shifts=shifts)
    dates = group_shifts_by_date(instance)

    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(nurse, shifts, model, dates)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 6), 1)
        nv.fix(datetime.date(2018, 1, 7), 1)