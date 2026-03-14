from nurse_rostering.solvers.hexaly.model.modules_set import DemandSatisfactionModule
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVars
from nurse_rostering.utils._generate import create_shifts, create_nurse
from nurse_rostering.data_schema import NurseRosteringInstance
import hexaly.optimizer as hx

def test_demand_satisfaction_met():
    shifts = create_shifts(1)
    shifts[0].demand = 2
    nurse1 = create_nurse("N1")
    nurse2 = create_nurse("N2")
    instance = NurseRosteringInstance(nurses=[nurse1, nurse2], shifts=shifts)

    with hx.HexalyOptimizer() as optimizer:
        model = optimizer.model
        
        nurse_vars1 = NurseDecisionVars(nurse1, shifts, model)
        nurse_vars2 = NurseDecisionVars(nurse2, shifts, model)
        DemandSatisfactionModule().build(instance, model, [nurse_vars1, nurse_vars2])
        model.minimize(0)
        model.close()
        
        optimizer.solve()
        
        if optimizer.solution.status != hx.HxSolutionStatus.OPTIMAL:
            raise Exception(f"Expected optimal, but got status {optimizer.solution.status}")



def test_demand_satisfaction_understaffed():
    shifts = create_shifts(1)
    shifts[0].demand = 2
    nurse1 = create_nurse("N1")
    nurse2 = create_nurse("N2")
    instance = NurseRosteringInstance(nurses=[nurse1, nurse2], shifts=shifts)

    with hx.HexalyOptimizer() as optimizer:
        model = optimizer.model
        
        nurse_vars1 = NurseDecisionVars(nurse1, shifts, model)
        nurse_vars2 = NurseDecisionVars(nurse2, shifts, model)
        DemandSatisfactionModule().build(instance, model, [nurse_vars1, nurse_vars2])
        nurse_vars2.fix(shifts[0].uid, False)
        model.minimize(0)
        model.close()
        optimizer.solve()
        
        if optimizer.solution.status != hx.HxSolutionStatus.INFEASIBLE and optimizer.solution.status != hx.HxSolutionStatus.INCONSISTENT:
            raise Exception(f"Expected feasible, but got status {optimizer.solution.status}")
        
