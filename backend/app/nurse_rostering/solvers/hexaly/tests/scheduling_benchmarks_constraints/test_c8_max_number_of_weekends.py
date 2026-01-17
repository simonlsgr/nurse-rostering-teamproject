import datetime

from nurse_rostering.solvers.hexaly.model.modules import MinimumConsecutiveDaysOffModule
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVars
from nurse_rostering.data_schema import Shift, Nurse
from nurse_rostering.utils._generate import create_shifts, create_nurse
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.data_schema import NurseRosteringInstance
import hexaly.optimizer as hx


def test_maximum_number_of_weekends_feasible():
    
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
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 13, 8, 0), 
            end_time=datetime.datetime(2018, 1, 13, 16, 0),
            name="Saturday Shift",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 14, 8, 0), 
            end_time=datetime.datetime(2018, 1, 14, 16, 0),
            name="Sunday Shift",
        )
    ]
    
    nurse1 = Nurse(
        name="n1",
        maximum_number_of_weekends=1,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )
    
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    with AssertModelFeasible() as model:
        nurse_vars1 = NurseDecisionVars(nurse1, shifts, model)
        MinimumConsecutiveDaysOffModule().build(instance, model, [nurse_vars1])
        nurse_vars1.fix(shifts[0].uid, True)
        nurse_vars1.fix(shifts[1].uid, True)
        nurse_vars1.fix(shifts[2].uid, False)
        nurse_vars1.fix(shifts[3].uid, False)

def test_maximum_number_of_weekends_infeasible():
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
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 13, 8, 0), 
            end_time=datetime.datetime(2018, 1, 13, 16, 0),
            name="Saturday Shift",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 14, 8, 0), 
            end_time=datetime.datetime(2018, 1, 14, 16, 0),
            name="Sunday Shift",
        )
    ]
    
    nurse1 = Nurse(
        name="n1",
        maximum_number_of_weekends=1,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )
    
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    with AssertModelInfeasible() as model:
        nurse_vars1 = NurseDecisionVars(nurse1, shifts, model)
        MinimumConsecutiveDaysOffModule().build(instance, model, [nurse_vars1])
        nurse_vars1.fix(shifts[0].uid, True)
        nurse_vars1.fix(shifts[1].uid, True)
        nurse_vars1.fix(shifts[2].uid, True)
        nurse_vars1.fix(shifts[3].uid, True)
