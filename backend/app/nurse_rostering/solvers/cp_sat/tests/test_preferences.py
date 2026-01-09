from nurse_rostering.model.modules import MaximizePreferences, DemandSatisfactionModule
from nurse_rostering.solvers.cp_sat.utils.testing import assert_objective
from nurse_rostering.utils._generate import create_shifts, create_nurse

from nurse_rostering.model.nurse_vars import NurseDecisionVars
from nurse_rostering.data_schema import NurseRosteringInstance

from ortools.sat.python import cp_model

from nurse_rostering.solvers.cp_sat.cp_sat_adapter import CpSatAdapter

def test_maximize_preferences_module():
    """
    Prefer assigning the nurse to their preferred shift (objective = -1).
    """
    shifts = create_shifts(1)
    shifts[0].demand = 1

    nurse = create_nurse("Preferred Nurse", preferred_shifts={shifts[0].uid})
    instance = NurseRosteringInstance(nurses=[nurse], shifts=shifts)

    adapter = CpSatAdapter()
    
    nurse_vars = NurseDecisionVars(nurse, shifts, adapter)
    
    pref_mod = MaximizePreferences()

    DemandSatisfactionModule().build(instance, adapter, [nurse_vars])

    adapter.model.minimize(pref_mod.build(instance, adapter, [nurse_vars]))

    assert_objective(adapter=adapter, expected=-1.0)

    assert adapter.solver.value(nurse_vars.is_assigned_to(shifts[0].uid)) == 1, (
        "Nurse should be assigned to their preferred shift"
    )
