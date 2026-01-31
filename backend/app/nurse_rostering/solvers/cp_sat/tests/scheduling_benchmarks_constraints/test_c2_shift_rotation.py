import datetime

from nurse_rostering.solvers.cp_sat.model.modules import ShiftRotationModule
from nurse_rostering.solvers.cp_sat.model.nurse_vars import NurseDecisionVars
from nurse_rostering.data_schema import Shift
from nurse_rostering.utils._generate import create_shifts, create_nurse
from cpsat_utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.data_schema import NurseRosteringInstance



def test_shift_rotation_infeasible():
    shifts = [
        Shift(demand=1, 
              start_time=datetime.datetime(2018, 1, 1, 8, 0), 
              end_time=datetime.datetime(2018, 1, 1, 16, 0),
              name="Morning Shift",
              type="A",
              not_followed_by_shift_types={"B"},
        ),
        Shift(demand=1,
                start_time=datetime.datetime(2018, 1, 2, 8, 0), 
                end_time=datetime.datetime(2018, 1, 2, 16, 0),
                name="Morning Shift",
                type="B",
            ),
    ]
    
    nurse1 = create_nurse("N1")
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    
    with AssertModelInfeasible() as model:
        nurse_vars = NurseDecisionVars(nurse1, shifts, model)
        ShiftRotationModule().build(instance, model, [nurse_vars])
        nurse_vars.fix(shifts[0].uid, True)
        nurse_vars.fix(shifts[1].uid, True)

def test_shift_rotation_feasible():
    shifts = [
        Shift(demand=1, 
              start_time=datetime.datetime(2018, 1, 1, 8, 0), 
              end_time=datetime.datetime(2018, 1, 1, 16, 0),
              name="Morning Shift",
              type="A",
              not_followed_by_shift_types={"B"},
        ),
        Shift(demand=1,
                start_time=datetime.datetime(2018, 1, 3, 8, 0), 
                end_time=datetime.datetime(2018, 1, 3, 16, 0),
                name="Morning Shift",
                type="B",
            ),
    ]
    nurse1 = create_nurse("N1")
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    with AssertModelFeasible() as model:
        nurse_vars = NurseDecisionVars(nurse1, shifts, model)
        ShiftRotationModule().build(instance, model, [nurse_vars])
        nurse_vars.fix(shifts[0].uid, True)
        nurse_vars.fix(shifts[1].uid, True)
        
