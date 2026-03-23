"""
This module provides a basic container to manage the variables for a single nurse in the nurse rostering problem.
"""

from collections.abc import Iterable
from ortools.sat.python import cp_model
from nurse_rostering.data_schema import Nurse, Shift, ShiftUid, NurseRosteringInstance


class PreferredCoverDecisionVars:
    def __init__(self, instance: NurseRosteringInstance, model: cp_model.CpModel):
        
        max_demand = max([shift.demand for shift in instance.shifts])+1
        
        self.total_below_preferred = {
            shift.uid: model.new_int_var(0, max_demand, f"total_below_preferred_{shift.uid}")
            for shift in instance.shifts
        }
        self.total_above_preferred = {
            shift.uid: model.new_int_var(0, max_demand, f"total_above_preferred_{shift.uid}")
            for shift in instance.shifts
        }
        self.cover_vars = (self.total_below_preferred, self.total_above_preferred)


class NurseDecisionVars:
    """
    A container to create and manage the decision variables for a single nurse.

    Each nurse has one Boolean variable for each shift, indicating whether the nurse is assigned to that shift.
    This class also provides helper methods to iterate over assignments and extract results.
    """

    def __init__(self, nurse: Nurse, shifts: list[Shift], model: cp_model.CpModel):
        self.nurse = nurse
        self.shifts = shifts
        self.model = model
        # Create one Boolean decision variable per shift for this nurse
        self._x = {
            shift.uid: model.new_bool_var(f"assign_{nurse.uid}_{shift.uid}")
            for shift in shifts
        }

    def fix(self, shift_uid: ShiftUid, value: bool):
        """
        Fix the assignment variable for the given shift UID to a specific value (True or False).
        Useful for setting hard constraints or testing the model.
        """
        if shift_uid not in self._x:
            raise ValueError(
                f"Shift UID {shift_uid} not found in nurse {self.nurse.uid} assignments."
            )
        self.model.add(self._x[shift_uid] == value)

    def is_assigned_to(self, shift_uid: ShiftUid) -> cp_model.BoolVarT:
        """
        Return the decision variable for the given shift UID.
        This variable is True if the nurse is assigned to that shift, and False otherwise.
        """
        return self._x[shift_uid]

    def iter_shifts(self) -> Iterable[tuple[Shift, cp_model.BoolVarT]]:
        """
        Iterate over all (shift, variable) pairs for this nurse.
        """
        for shift in self.shifts:
            yield shift, self.is_assigned_to(shift_uid=shift.uid)

    def extract(self, solver: cp_model.CpSolver) -> list[ShiftUid]:
        """
        Extract a list of shift UIDs that this nurse is assigned to in the solution.
        """
        return [shift_uid for shift_uid in self._x if solver.value(self._x[shift_uid])]


class NurseWorksAtWeekendVars:
    def __init__(self, nv: NurseDecisionVars, weekends, shifts_by_date, model: cp_model.CpModel):
        saturday = 0
        sunday = 1
        self.nurse = nv.nurse
        self.model = model
        self._x = {
            weekend: model.new_bool_var(f"{self.nurse.uid}_weekend_{weekend[saturday].isoformat()}_{weekend[sunday].isoformat()}") for weekend in weekends
        }
        for weekend in weekends:
            shifts_on_weekend = shifts_by_date.get(weekend[saturday], []) + shifts_by_date.get(weekend[sunday], [])
            _vars = [nv.is_assigned_to(shift) for shift in shifts_on_weekend]
            if _vars:
                model.add_max_equality(self._x[weekend], [nv.is_assigned_to(shift) for shift in shifts_on_weekend])
            else:
                model.add(self._x[weekend] == 0)

    def is_assigned_to(self, weekend):
        return self._x[weekend]
