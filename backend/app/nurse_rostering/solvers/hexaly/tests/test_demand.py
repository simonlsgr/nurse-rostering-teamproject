import hexaly.optimizer
from hexaly.optimizer import HxSolutionStatus
from nurse_rostering.model.modules import DemandSatisfactionModule
from nurse_rostering.model.nurse_vars import NurseDecisionVars
from cpsat_utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.utils._generate import create_shifts, create_nurse
from nurse_rostering.data_schema import NurseRosteringInstance
import gurobipy as gp
from nurse_rostering.solvers.hexaly.hexaly_adapter import HexalyAdapter

def test_demand_satisfaction_met():
    shifts = create_shifts(1)
    shifts[0].demand = 2
    nurse1 = create_nurse("N1")
    nurse2 = create_nurse("N2")
    instance = NurseRosteringInstance(nurses=[nurse1, nurse2], shifts=shifts)

    with hexaly.optimizer.HexalyOptimizer() as optimizer:
        
        model = HexalyAdapter(optimizer.model)
        
        nurse_vars1 = NurseDecisionVars(nurse1, shifts, model)
        nurse_vars2 = NurseDecisionVars(nurse2, shifts, model)
        DemandSatisfactionModule().build(instance, model, [nurse_vars1, nurse_vars2])
        model.set_objective(0) # needed so that hexaly starts
        optimizer.model.close()
        try:
            optimizer.solve()
        except Exception as e:
            raise RuntimeError(
                f"Expected feasible but solver returned {e}."
            )
    


def test_demand_satisfaction_understaffed():
    shifts = create_shifts(1)
    shifts[0].demand = 2
    nurse1 = create_nurse("N1")
    nurse2 = create_nurse("N2")
    instance = NurseRosteringInstance(nurses=[nurse1, nurse2], shifts=shifts)

    
    with hexaly.optimizer.HexalyOptimizer() as optimizer:
        
        model = HexalyAdapter(optimizer.model)
        
        nurse_vars1 = NurseDecisionVars(nurse1, shifts, model)
        nurse_vars2 = NurseDecisionVars(nurse2, shifts, model)
        DemandSatisfactionModule().build(instance, model, [nurse_vars1, nurse_vars2])
        nurse_vars2.fix(shifts[0].uid, False)
        
        model.set_objective(0) # needed so that hexaly starts


        optimizer.model.close()
        optimizer.solve()
        if optimizer.solution.status in (HxSolutionStatus.FEASIBLE, HxSolutionStatus.OPTIMAL):
            raise RuntimeError(
                f"Expected infeasible, but solver returned status {optimizer.solution.status}."
            )
            

        