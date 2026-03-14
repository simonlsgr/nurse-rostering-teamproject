import datetime

from nurse_rostering.solvers.hexaly.model.modules_set import MaximumConsecutiveShiftsModuleSet
from nurse_rostering.solvers.hexaly.model.nurse_vars import ShiftDecisionVars
from nurse_rostering.data_schema import Shift, Nurse
from nurse_rostering.utils._generate import create_shifts, create_nurse
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.data_schema import NurseRosteringInstance
import hexaly.optimizer as hx


def test_maximum_consecutive_shifts_feasible():
    
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
        )
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
        shift_vars_1 = ShiftDecisionVars(shifts[0], [nurse1], model)
        shift_vars_2 = ShiftDecisionVars(shifts[1], [nurse1], model)
        shift_vars_3 = ShiftDecisionVars(shifts[2], [nurse1], model)
        MaximumConsecutiveShiftsModuleSet().build(instance, model, [shift_vars_1, shift_vars_2, shift_vars_3])
        shift_vars_1.fix(nurse1.uid, True)
        shift_vars_2.fix(nurse1.uid, True)
        shift_vars_3.fix(nurse1.uid, True)
        

def test_maximum_consecutive_shifts_infeasible():
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
        )
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
        shift_vars_1 = ShiftDecisionVars(shifts[0], [nurse1], model)
        shift_vars_2 = ShiftDecisionVars(shifts[1], [nurse1], model)
        shift_vars_3 = ShiftDecisionVars(shifts[2], [nurse1], model)
        
        
        MaximumConsecutiveShiftsModuleSet().build(instance, model, [shift_vars_1, shift_vars_2, shift_vars_3])
        shift_vars_1.fix(nurse1.uid, True)
        shift_vars_2.fix(nurse1.uid, True)
        shift_vars_3.fix(nurse1.uid, True)
        
        
