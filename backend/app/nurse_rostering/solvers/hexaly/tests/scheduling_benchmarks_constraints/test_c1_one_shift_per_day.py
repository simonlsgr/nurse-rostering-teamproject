import datetime

from nurse_rostering.solvers.hexaly.model.modules_set import OneShiftPerDayModuleSet
from nurse_rostering.solvers.hexaly.model.nurse_vars import ShiftDecisionVars
from nurse_rostering.data_schema import Shift
from nurse_rostering.utils._generate import create_shifts, create_nurse
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.data_schema import NurseRosteringInstance
import hexaly.optimizer as hx


def test_one_shift_per_day_infeasible():
    shifts = [
        Shift(demand=1, 
              start_time=datetime.datetime(2018, 1, 1, 8, 0), 
              end_time=datetime.datetime(2018, 1, 1, 16, 0),
              name="Morning Shift",
        ),
        Shift(demand=1,
                start_time=datetime.datetime(2018, 1, 1, 16, 0), 
                end_time=datetime.datetime(2018, 1, 2, 0, 0),
                name="Evening Shift",
            ),
    ]
    nurse1 = create_nurse("N1", min_time_between_shifts=datetime.timedelta(hours=0))
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    
    with AssertModelInfeasible() as model:
        shift_vars1 = ShiftDecisionVars(shifts[0], [nurse1], model)
        shift_vars2 = ShiftDecisionVars(shifts[1], [nurse1], model)
        OneShiftPerDayModuleSet().build(instance, model, [shift_vars1, shift_vars2])
        shift_vars1.fix(nurse1.uid, True)
        shift_vars2.fix(nurse1.uid, True)
    
        
        
        

def test_one_shift_per_day_feasible():
    shifts = [
        Shift(demand=1, 
              start_time=datetime.datetime(2018, 1, 1, 8, 0), 
              end_time=datetime.datetime(2018, 1, 1, 16, 0),
              name="Morning Shift 1",
        ),
        Shift(demand=1,
                start_time=datetime.datetime(2018, 1, 2, 8, 0), 
                end_time=datetime.datetime(2018, 1, 2, 16, 0),
                name="Morning Shift 1",
            ),
    ]
    nurse1 = create_nurse("N1", min_time_between_shifts=datetime.timedelta(hours=0))
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    
    with AssertModelFeasible() as model:
        shift_vars1 = ShiftDecisionVars(shifts[0], [nurse1], model)
        shift_vars2 = ShiftDecisionVars(shifts[1], [nurse1], model)
        OneShiftPerDayModuleSet().build(instance, model, [shift_vars1, shift_vars2])
        shift_vars1.fix(nurse1.uid, True)
        shift_vars2.fix(nurse1.uid, False)
        
        

    