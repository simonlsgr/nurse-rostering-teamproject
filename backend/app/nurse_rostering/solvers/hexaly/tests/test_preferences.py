from nurse_rostering.solvers.hexaly.model.modules_set import MaximizePreferences, DemandSatisfactionModule
from cpsat_utils.testing import assert_objective
from nurse_rostering.utils._generate import create_shifts, create_nurse

from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVars
from nurse_rostering.data_schema import NurseRosteringInstance
import hexaly.optimizer


def test_maximize_preferences_module():
    """
    Prefer assigning the nurse to their preferred shift (objective = -1).
    """
    shifts = create_shifts(1)
    shifts[0].demand = 1

    nurse = create_nurse("Preferred Nurse", preferred_shifts={shifts[0].uid})
    instance = NurseRosteringInstance(nurses=[nurse], shifts=shifts)

    with hexaly.optimizer.HexalyOptimizer() as optimizer:
        model = optimizer.model
        
        nurse_vars = NurseDecisionVars(nurse, shifts, model)
        
        pref_mod = MaximizePreferences()

        DemandSatisfactionModule().build(instance, model, [nurse_vars])

        objective = pref_mod.build(instance, model, [nurse_vars])
        model.minimize(objective)
        model.close()
        
        optimizer.solve()
        
        val = objective.value
        assert abs(val - (-1.0)) <= 1e-8, f"Expected objective≈{-1}, got {val}"

        # assert_objective(model=model, solver=solver, expected=-1.0)

        assert nurse_vars.is_assigned_to(shifts[0].uid).value == 1, (
            "Nurse should be assigned to their preferred shift"
        )
