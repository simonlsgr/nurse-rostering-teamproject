from solvers.model.modules import DemandSatisfactionModule
from solvers.model.nurse_vars import NurseDecisionVars
from cpsat_utils.testing import AssertModelFeasible, AssertModelInfeasible
from ortools.sat.python import cp_model
from solvers.utils._generate import create_shifts, create_nurse
from solvers.data_schema import NurseRosteringInstance
from solvers.cp_sat.cp_sat_adapter import CpSatAdapter

def test_demand_satisfaction_met():
    shifts = create_shifts(1)
    shifts[0].demand = 2
    nurse1 = create_nurse("N1")
    nurse2 = create_nurse("N2")
    instance = NurseRosteringInstance(nurses=[nurse1, nurse2], shifts=shifts)

    model = CpSatAdapter()
    nurse_vars1 = NurseDecisionVars(nurse1, shifts, model) 
    nurse_vars2 = NurseDecisionVars(nurse2, shifts, model)
    DemandSatisfactionModule().build(instance, model, [nurse_vars1, nurse_vars2])
    status = model.solver.solve(model.model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError(
            f"Expected feasible, but solver returned status {status}."
        )

""" 
def test_demand_satisfaction_understaffed():
    shifts = create_shifts(1)
    shifts[0].demand = 2
    nurse1 = create_nurse("N1")
    nurse2 = create_nurse("N2")
    instance = NurseRosteringInstance(nurses=[nurse1, nurse2], shifts=shifts)

    with AssertModelInfeasible() as model:
        nurse_vars1 = NurseDecisionVars(nurse1, shifts, model)
        nurse_vars2 = NurseDecisionVars(nurse2, shifts, model)
        DemandSatisfactionModule().build(instance, model, [nurse_vars1, nurse_vars2])
        nurse_vars2.fix(shifts[0].uid, False)
 """