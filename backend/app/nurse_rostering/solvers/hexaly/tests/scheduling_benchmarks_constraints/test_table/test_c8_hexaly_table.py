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
            start_time=datetime.datetime(2018, 1, i, 8, 0),
            end_time=datetime.datetime(2018, 1, i, 16, 0),
            name="Morning Shift",
            type="A",
        )
        for i in range(1,15)
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
    return instance


def test_maximum_number_of_weekends_feasible_table():
    instance = _make_instance(max_weekends=1)
    
    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(instance, model)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, nv)
        nuid = instance.nurses[0].uid

        nv.fix(nuid, instance.shifts[5].uid, True) # Saturday
        nv.fix(nuid, instance.shifts[6].uid, True) # Sunday
        nv.fix(nuid, instance.shifts[12].uid, False) # Saturday
        nv.fix(nuid, instance.shifts[13].uid, False) # Sunday
        


def test_maximum_number_of_weekends_infeasible_table():
    instance = _make_instance(max_weekends=1)

    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(instance, model)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, nv)
        nuid = instance.nurses[0].uid
        
        nv.fix(nuid, instance.shifts[5].uid, True) # Saturday
        nv.fix(nuid, instance.shifts[6].uid, True) # Sunday
        nv.fix(nuid, instance.shifts[12].uid, True) # Saturday
        nv.fix(nuid, instance.shifts[13].uid, True) # Sunday


def test_maximum_number_of_weekends_counts_weekend_only_once_table():
    instance = _make_instance(max_weekends=1)
    
    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(instance, model)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, nv)
        nuid = instance.nurses[0].uid

        nv.fix(nuid, instance.shifts[5].uid, True) # Saturday
        nv.fix(nuid, instance.shifts[6].uid, False) # Sunday
        nv.fix(nuid, instance.shifts[12].uid, False) # Saturday
        nv.fix(nuid, instance.shifts[13].uid, False) # Sunday


def test_maximum_number_of_weekends_single_day_on_weekend_still_counts_table():
    instance = _make_instance(max_weekends=1)
    
    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(instance, model)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, nv)
        nuid = instance.nurses[0].uid

        nv.fix(nuid, instance.shifts[5].uid, True) # Saturday
        nv.fix(nuid, instance.shifts[6].uid, False) # Sunday
        nv.fix(nuid, instance.shifts[12].uid, False) # Saturday
        nv.fix(nuid, instance.shifts[13].uid, True) # Sunday


def test_maximum_number_of_weekends_zero_allowed_feasible_if_no_weekend_work_table():
    instance = _make_instance(max_weekends=0)
    
    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(instance, model)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, nv)
        nuid = instance.nurses[0].uid

        nv.fix(nuid, instance.shifts[5].uid, False) # Saturday
        nv.fix(nuid, instance.shifts[6].uid, False) # Sunday
        nv.fix(nuid, instance.shifts[12].uid, False) # Saturday
        nv.fix(nuid, instance.shifts[13].uid, False) # Sunday


def test_maximum_number_of_weekends_zero_allowed_infeasible_if_any_weekend_work_table():
    instance = _make_instance(max_weekends=0)
    
    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(instance, model)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, nv)
        nuid = instance.nurses[0].uid

        nv.fix(nuid, instance.shifts[5].uid, True) # Saturday
        nv.fix(nuid, instance.shifts[6].uid, False) # Sunday
        nv.fix(nuid, instance.shifts[12].uid, False) # Saturday
        nv.fix(nuid, instance.shifts[13].uid, False) # Sunday


def test_maximum_number_of_weekends_exactly_at_limit_table():
    instance = _make_instance(max_weekends=2)
    
    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(instance, model)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, nv)
        nuid = instance.nurses[0].uid

        nv.fix(nuid, instance.shifts[5].uid, True) # Saturday
        nv.fix(nuid, instance.shifts[6].uid, False) # Sunday
        nv.fix(nuid, instance.shifts[12].uid, True) # Saturday
        nv.fix(nuid, instance.shifts[13].uid, False) # Sunday


def test_maximum_number_of_weekends_single_weekend_horizon_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, i, 8, 0),
            end_time=datetime.datetime(2018, 1, i, 16, 0),
            name="Morning Shift",
            type="A",
        )
        for i in range(1,8)
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

    with AssertModelFeasible() as model:
        nv = NurseDecisionVarsTable(instance, model)
        MaximumNumberOfWeekendsModuleTable().build(instance, model, nv)
        nuid = nurse.uid

        nv.fix(nuid, instance.shifts[5].uid, True) # Saturday
        nv.fix(nuid, instance.shifts[6].uid, True) # Sunday