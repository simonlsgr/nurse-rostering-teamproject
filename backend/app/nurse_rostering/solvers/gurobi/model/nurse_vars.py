"""
This module provides a basic container to manage the variables for a single nurse in the nurse rostering problem.
"""

from collections.abc import Iterable
import gurobipy as gp
from gurobipy import GRB
from nurse_rostering.data_schema import Nurse, Shift, ShiftUid


class PreferredCoverDecisionVars:
    def __init__(self, shifts: list[Shift], model: gp.Model):
        
        self.total_below_preferred = {
            shift.uid: model.addVar(vtype=GRB.INTEGER, lb=0, ub=len(shifts), name=f"total_below_preferred_{shift.uid}")
            for shift in shifts
        }
        self.total_above_preferred = {
            shift.uid: model.addVar(vtype=GRB.INTEGER, lb=0, ub=len(shifts), name=f"total_above_preferred_{shift.uid}")
            for shift in shifts
        }
        self.cover_vars = (self.total_below_preferred, self.total_above_preferred)


class NurseDecisionVars:
    """
    One binary variable per shift for a nurse: assign_{nurse}_{shift} in {0,1}
    """

    def __init__(self, nurse: Nurse, shifts: list[Shift], model: gp.Model):
        self.nurse = nurse
        self.shifts = shifts
        self.model = model
        self._x = {
            shift.uid: model.addVar(vtype=GRB.BINARY, name=f"assign_{nurse.uid}_{shift.uid}")
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
        v = self._x[shift_uid]
        v.LB = int(value)
        v.UB = int(value)

    def is_assigned_to(self, shift_uid: ShiftUid) -> gp.Var:
        """
        Return the decision variable for the given shift UID.
        This variable is True if the nurse is assigned to that shift, and False otherwise.
        """
        return self._x[shift_uid]

    def iter_shifts(self) -> Iterable[tuple[Shift, gp.Var]]:
        """
        Iterate over all (shift, variable) pairs for this nurse.
        """
        for shift in self.shifts:
            yield shift, self._x[shift.uid]

    def extract(self) -> list[ShiftUid]:
        """
        Extract a list of shift UIDs that this nurse is assigned to in the solution.
        """
        return [shift_uid for shift_uid in self._x if self._x[shift_uid].X > 0.5]


class NurseWorksAtWeekendVars:
    def __init__(self, nv: NurseDecisionVars, weekends, shifts_by_date, model: gp.Model):
        saturday = 0
        sunday = 1
        self.nurse = nv.nurse
        self.model = model
        self._x = {
            weekend: model.addVar(vtype=GRB.BINARY, name=f"{self.nurse.uid}_weekend_{weekend[saturday].isoformat()}_{weekend[sunday].isoformat()}") for weekend in weekends
        }
        for weekend in weekends:
            shifts_on_weekend = shifts_by_date.get(weekend[saturday], []) + shifts_by_date.get(weekend[sunday], [])
            _vars = [nv.is_assigned_to(shift) for shift in shifts_on_weekend]
            if _vars:
                
                for shift in shifts_on_weekend:
                    model.addConstr(self._x[weekend] >= nv.is_assigned_to(shift))
                model.addConstr(self._x[weekend] <= gp.quicksum(nv.is_assigned_to(shift) for shift in shifts_on_weekend))
            else:
                model.addConstr(self._x[weekend] == 0)

    def is_assigned_to(self, weekend):
        return self._x[weekend]
    
