import datetime

from nurse_rostering.solvers.hexaly.model.modules_set import DaysOffModuleSet
from nurse_rostering.solvers.hexaly.model.nurse_vars import ShiftDecisionVars
from nurse_rostering.data_schema import Shift, Nurse
from nurse_rostering.utils._generate import create_shifts, create_nurse
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.data_schema import NurseRosteringInstance
import hexaly.optimizer as hx

def test_days_off_feasible():
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
    ]
    
    nurse1 = Nurse(
        name="n1",
        days_off={datetime.date(2018, 1, 2)},
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )
    
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    with AssertModelFeasible() as model:
        shift_vars_1 = ShiftDecisionVars(shifts[0], [nurse1], model)
        shift_vars_2 = ShiftDecisionVars(shifts[1], [nurse1], model)
        DaysOffModuleSet().build(instance, model, [shift_vars_1, shift_vars_2])
        shift_vars_1.fix(nurse1.uid, True)
        shift_vars_2.fix(nurse1.uid, False)

def test_days_off_infeasible():
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
    ]
    
    nurse1 = Nurse(
        name="n1",
        days_off={datetime.date(2018, 1, 2)},
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )
    
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    with AssertModelInfeasible() as model:
        shift_vars_1 = ShiftDecisionVars(shifts[0], [nurse1], model)
        shift_vars_2 = ShiftDecisionVars(shifts[1], [nurse1], model)
        DaysOffModuleSet().build(instance, model, [shift_vars_1, shift_vars_2])
        shift_vars_1.fix(nurse1.uid, True)
        shift_vars_2.fix(nurse1.uid, True)
        