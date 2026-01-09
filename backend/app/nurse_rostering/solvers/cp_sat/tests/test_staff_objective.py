from nurse_rostering.model.modules import PreferStaffModule, DemandSatisfactionModule
from nurse_rostering.solvers.cp_sat.utils.testing import assert_objective
from nurse_rostering.utils._generate import create_shifts, create_nurse

from nurse_rostering.model.nurse_vars import NurseDecisionVars
from nurse_rostering.data_schema import NurseRosteringInstance

from ortools.sat.python import cp_model
from nurse_rostering.solvers.cp_sat.cp_sat_adapter import CpSatAdapter

def test_prefer_staff_module():
    """
    Prefer assigning the staff nurse (objective = 0).
    """
    shifts = create_shifts(1)
    shifts[0].demand = 1

    staff = create_nurse("Staff", staff=True)
    contractor = create_nurse("Contractor", staff=False)
    instance = NurseRosteringInstance(nurses=[staff, contractor], shifts=shifts)

    adapter = CpSatAdapter()
    vars_staff = NurseDecisionVars(staff, shifts, adapter)
    vars_contractor = NurseDecisionVars(contractor, shifts, adapter)
    staff_mod = PreferStaffModule()
    DemandSatisfactionModule().build(instance, adapter, [vars_staff, vars_contractor])

    adapter.model.minimize(staff_mod.build(instance, adapter.model, [vars_staff, vars_contractor]))
    assert_objective(
        adapter=adapter, expected=0.0
    )  # will run solve automatically
    assert adapter.solver.value(vars_staff.is_assigned_to(shifts[0].uid)) == 1, (
        "Staff nurse should be assigned to the shift"
    )
    assert adapter.solver.value(vars_contractor.is_assigned_to(shifts[0].uid)) == 0, (
        "Contractor nurse should not be assigned to the shift"
    )
