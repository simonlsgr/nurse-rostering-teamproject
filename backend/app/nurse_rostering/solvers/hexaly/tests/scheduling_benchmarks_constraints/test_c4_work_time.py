
import datetime

from nurse_rostering.solvers.hexaly.model.modules import LimitWorkTimeModule
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVars
from nurse_rostering.data_schema import Shift, Nurse
from nurse_rostering.utils._generate import create_shifts, create_nurse
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.data_schema import NurseRosteringInstance
import hexaly.optimizer as hx

def test_limit_work_time_feasible():
    shifts = [
        Shift(demand=1, 
              start_time=datetime.datetime(2018, 1, 1, 8, 0), 
              end_time=datetime.datetime(2018, 1, 1, 16, 0),
              name="Morning Shift",
        ),
        Shift(demand=1,
                start_time=datetime.datetime(2018, 1, 2, 8, 0), 
                end_time=datetime.datetime(2018, 1, 2, 16, 0),
                name="Morning Shift",
            ),
    ]
    
    nurse1 = Nurse(
        name="n1",
        max_work_time=datetime.timedelta(hours=16),
        referred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )
    
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    with AssertModelFeasible() as model:
        nurse_vars1 = NurseDecisionVars(nurse1, shifts, model)
        LimitWorkTimeModule().build(instance, model, [nurse_vars1])
        nurse_vars1.fix(shifts[0].uid, True)
        nurse_vars1.fix(shifts[1].uid, True)
        
def test_limit_work_time_infeasible():
    shifts = [
        Shift(demand=1, 
              start_time=datetime.datetime(2018, 1, 1, 8, 0), 
              end_time=datetime.datetime(2018, 1, 1, 16, 0),
              name="Morning Shift",
        ),
        Shift(demand=1,
                start_time=datetime.datetime(2018, 1, 2, 8, 0), 
                end_time=datetime.datetime(2018, 1, 2, 16, 0),
                name="Morning Shift",
            ),
    ]
    
    nurse1 = Nurse(
        name="n1",
        max_work_time=datetime.timedelta(hours=8),
        referred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )
    
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    with AssertModelInfeasible() as model:
        nurse_vars1 = NurseDecisionVars(nurse1, shifts, model)
        LimitWorkTimeModule().build(instance, model, [nurse_vars1])
        nurse_vars1.fix(shifts[0].uid, True)
        nurse_vars1.fix(shifts[1].uid, True)

