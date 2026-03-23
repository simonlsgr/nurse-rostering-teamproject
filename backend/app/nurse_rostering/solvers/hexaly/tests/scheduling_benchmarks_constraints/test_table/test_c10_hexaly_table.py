import datetime

from nurse_rostering.solvers.hexaly.model.modules_table import CoverRequirementsModuleTable
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVarsTable
from nurse_rostering.data_schema import Shift, Nurse
from nurse_rostering.utils._generate import create_shifts, create_nurse
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.data_schema import NurseRosteringInstance
import hexaly.optimizer as hx


def test_cover_requirements_feasible():
    shifts = [
        Shift(
            demand=3, 
            start_time=datetime.datetime(2018, 1, i, 8, 0), 
            end_time=datetime.datetime(2018, 1, i, 16, 0),
            name="Morning Shift",
            type="A",
        ) 
        for i in range(1,8)
    ]
    
    nurse1 = Nurse(
        name="n1",
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
        minimum_work_time=2000,
        maximum_work_time=3360,
    )
    
    nurse2 = Nurse(
        name="n2",
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
        minimum_work_time=2000,
        maximum_work_time=3360,
    )
    
    instance = NurseRosteringInstance(nurses=[nurse1, nurse2], shifts=shifts)
    with hx.HexalyOptimizer() as optimizer:
        model = optimizer.model
        
        nurse_var = NurseDecisionVarsTable(instance, model)
        goal = CoverRequirementsModuleTable().build(instance, model, nurse_var)
        
        model.minimize(goal)
        
        model.close()
        
        optimizer.solve()
        
        assert optimizer.solution.status == hx.HxSolutionStatus.OPTIMAL
        assert goal.value == 7
    
