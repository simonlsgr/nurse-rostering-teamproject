import datetime

from nurse_rostering.solvers.hexaly.model.modules_ip import CoverRequirementsModuleIP
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVarsIP
from nurse_rostering.data_schema import Shift, Nurse
from nurse_rostering.utils._generate import create_shifts, create_nurse
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.data_schema import NurseRosteringInstance

import hexaly.optimizer as hx

def test_cover_requirements_feasible():
    shifts = [
        Shift(
            demand=3, 
            start_time=datetime.datetime(2018, 1, 1, 8, 0), 
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
        ),
    ]
    
    nurse1 = Nurse(
        name="n1",
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )
    
    nurse2 = Nurse(
        name="n2",
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )
    
    
    instance = NurseRosteringInstance(nurses=[nurse1, nurse2], shifts=shifts)
    with hx.HexalyOptimizer() as optimizer:
        model = optimizer.model
        
        nurse_vars_1 = NurseDecisionVarsIP(nurse1, shifts, model)
        nurse_vars_2 = NurseDecisionVarsIP(nurse2, shifts, model)
        
        goal = CoverRequirementsModuleIP().build(instance, model, [nurse_vars_1, nurse_vars_2])
        
        model.minimize(goal)
        
        model.close()
        
        optimizer.solve()
        
        assert optimizer.solution.status == hx.HxSolutionStatus.OPTIMAL
        assert goal.value == 1
    
