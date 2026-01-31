import datetime

from nurse_rostering.solvers.cp_sat.model.modules import CoverRequirementsModule
from nurse_rostering.solvers.cp_sat.model.nurse_vars import NurseDecisionVars
from nurse_rostering.data_schema import Shift, Nurse
from nurse_rostering.utils._generate import create_shifts, create_nurse
from cpsat_utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.data_schema import NurseRosteringInstance

from ortools.sat.python import cp_model

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
    
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()
    
    nurse_vars_1 = NurseDecisionVars(nurse1, shifts, model)
    nurse_vars_2 = NurseDecisionVars(nurse2, shifts, model)
    goal = CoverRequirementsModule().build(instance, model, [nurse_vars_1, nurse_vars_2])
    
    model.minimize(goal)
    
    status = solver.solve(model)
    
    assert status == cp_model.OPTIMAL
    assert solver.objective_value == 1
    
