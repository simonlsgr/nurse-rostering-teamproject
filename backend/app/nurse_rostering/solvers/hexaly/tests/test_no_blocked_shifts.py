from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVars
from nurse_rostering.utils._generate import create_shifts, create_nurse
from nurse_rostering.data_schema import NurseRosteringInstance
from nurse_rostering.solvers.hexaly.model.modules import NoBlockedShiftsModule
import hexaly.optimizer

def test_no_blocked_shifts_trivial():
    """
    Just create the variables for a nurse without any blocked shifts.
    This should be feasible and not raise any exceptions.
    """
    shifts = create_shifts(2)  # two consecutive shifts
    nurse = create_nurse("Nurse A", blocked_shifts=set())
    instance = NurseRosteringInstance(nurses=[nurse], shifts=shifts)
    
    with hexaly.optimizer.HexalyOptimizer() as optimizer:
        model = optimizer.model
        nurse_vars = NurseDecisionVars(nurse, shifts, model)
        NoBlockedShiftsModule().build(instance, model, [nurse_vars])
        model.minimize(0)
        model.close()
        optimizer.solve()


def test_no_blocked_shifts_infeasible():
    """
    Test that the model is infeasible when a nurse is assigned to a blocked shift.
    """
    shifts = create_shifts(2)  # two consecutive shifts
    nurse = create_nurse("Nurse A", blocked_shifts={shifts[0].uid})  # Blocked shift 0
    instance = NurseRosteringInstance(nurses=[nurse], shifts=shifts)
    
    with hexaly.optimizer.HexalyOptimizer() as optimizer:
        model = optimizer.model
        
        nurse_vars = NurseDecisionVars(nurse, shifts, model)
        NoBlockedShiftsModule().build(instance, model, [nurse_vars])
        nurse_vars.fix(shifts[0].uid, True)
        model.minimize(0)
        model.close()
        
        optimizer.solve()
        
        if optimizer.solution.status != hexaly.optimizer.HxSolutionStatus.INFEASIBLE and optimizer.solution.status != hexaly.optimizer.HxSolutionStatus.INCONSISTENT:
            raise Exception(f"Expected infeasible, but got status {optimizer.solution.status}")


def test_no_blocked_shifts_feasible():
    """
    Test that the model is feasible when the assigned shift is not blocked.
    """
    shifts = create_shifts(2)  # two consecutive shifts
    nurse = create_nurse("Nurse A", blocked_shifts={shifts[0].uid})  # Blocked shift 1
    instance = NurseRosteringInstance(nurses=[nurse], shifts=shifts)
    with hexaly.optimizer.HexalyOptimizer() as optimizer:
        model = optimizer.model
        
        nurse_vars = NurseDecisionVars(nurse, shifts, model)
        NoBlockedShiftsModule().build(instance, model, [nurse_vars])
        nurse_vars.fix(shifts[1].uid, True)  # This time we fix the other shift
        model.minimize(0)
        model.close()
        optimizer.solve()

        if optimizer.solution.status != hexaly.optimizer.HxSolutionStatus.OPTIMAL and optimizer.solution.status != hexaly.optimizer.HxSolutionStatus.FEASIBLE:
            raise Exception(f"Expected feasible, but got status {optimizer.solution.status}")