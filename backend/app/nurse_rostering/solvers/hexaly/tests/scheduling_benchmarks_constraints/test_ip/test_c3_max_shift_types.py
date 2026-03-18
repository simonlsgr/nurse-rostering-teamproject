import datetime

from nurse_rostering.solvers.hexaly.model.modules_ip import MaximumShiftTypesModuleIP
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVarsIP
from nurse_rostering.data_schema import Shift, Nurse
from nurse_rostering.utils._generate import create_shifts, create_nurse
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.data_schema import NurseRosteringInstance



def test_maximum_shift_types_feasible():
    shifts = [
        Shift(demand=1, 
              start_time=datetime.datetime(2018, 1, 1, 8, 0), 
              end_time=datetime.datetime(2018, 1, 1, 16, 0),
              name="Morning Shift",
              type="A",
        ),
        Shift(demand=1,
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
    with AssertModelFeasible() as model:
        nurse_vars = NurseDecisionVarsIP(nurse1, shifts, model)
        MaximumShiftTypesModuleIP().build(instance, model, [nurse_vars])
        nurse_vars.fix(shifts[0].uid, True)
        nurse_vars.fix(shifts[1].uid, True)
        
    
def test_maximum_shift_types_infeasible():
    shifts = [
        Shift(demand=1, 
              start_time=datetime.datetime(2018, 1, 1, 8, 0), 
              end_time=datetime.datetime(2018, 1, 1, 16, 0),
              name="Morning Shift",
              type="A",
        ),
        Shift(demand=1,
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
    
    with AssertModelInfeasible() as model:
        nurse_vars = NurseDecisionVarsIP(nurse1, shifts, model)
        MaximumShiftTypesModuleIP().build(instance, model, [nurse_vars])
        nurse_vars.fix(shifts[0].uid, True)
        nurse_vars.fix(shifts[1].uid, True)
        


    