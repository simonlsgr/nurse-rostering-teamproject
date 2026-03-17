"""
This module provides a basic container to manage the variables for a single nurse in the nurse rostering problem.
"""

from collections.abc import Iterable
from datetime import date
from typing import Any

from hexaly.optimizer import HxModel, HxOperator
from nurse_rostering.data_schema import Nurse, Shift, ShiftUid, NurseUid, NurseRosteringInstance
from nurse_rostering.utils.data_utils import group_shifts_by_date


class ShiftDecisionVars:
    def __init__(self, shift: Shift, nurses: list[Nurse], model: HxModel):
        self.shift = shift
        self.model = model
        self.nurses = nurses
        self.number_of_nurses = len(self.nurses)
        self.nurses_assigned = model.list(self.number_of_nurses)
        
    def fix(self, nurse_uid: int, value: bool):
        nurse_index = -1
        for idx, nurse in enumerate(self.nurses):
            if nurse.uid == nurse_uid:
                nurse_index = idx
                break
                
        if nurse_index < 0 or nurse_index >= self.number_of_nurses:
            raise ValueError(
                f"Nurse index {nurse_index} is out of bounds for shift {self.shift.uid}."
            )
        self.model.add_constraint(self.model.contains(self.nurses_assigned, nurse_index) == int(value))
    
    # def assigns_nurse(self, nurse_index: int):
    #     return self.model.contains(self.nurses_assigned, nurse_index)
    
    def extract(self) -> list[NurseUid]:
        nurses_assigned_list = list(self.nurses_assigned.value) or []
        return [nurse.uid for idx, nurse in enumerate(self.nurses) if idx in nurses_assigned_list]
    
            

class NurseDecisionVarsTable:
    """
    A container to create and manage the decision variables for a single nurse.

    Each nurse has one Boolean variable for each shift, indicating whether the nurse is assigned to that shift.
    This class also provides helper methods to iterate over assignments and extract results.
    """

    def __init__(self, nurse: Nurse, shifts: list[Shift], model: HxModel, dates: dict[date, list[ShiftUid]]):
        self.nurse = nurse
        self.shifts = shifts
        self.dates = dates
        self.model = model
        self._x = {}
        for _date, shift_uids in self.dates.items():
            shift_count = len(shift_uids)
            self._x[_date] = self.model.int(0, shift_count)


    def fix(self, _date: date, value: int):
        """
        Fix the assignment variable for the given shift UID to a specific value (True or False).
        Useful for setting hard constraints or testing the model.
        """
        if _date not in self._x:
            raise ValueError(
                f"Date {_date} not found in nurse {self.nurse.uid} assignments."
            )
        if value not in range(len(self.dates.get(_date, []))+1):
            raise ValueError(
                f"Shift {value} does not exist on date {_date} for nurse {self.nurse.uid} assignments."
            )
        self.model.add_constraint(self._x[_date] == value)

    def is_assigned_to(self, _date: date):# -> cp_model.BoolVarT:
        """
        Return the decision variable for the given shift UID.
        This variable is True if the nurse is assigned to that shift, and False otherwise.
        """
        return self._x[_date]

    def iter_shifts(self):# -> Iterable[tuple[Shift, cp_model.BoolVarT]]:
        """
        Iterate over all (shift, variable) pairs for this nurse.
        """
        for _date in self.dates.keys():
            yield _date, self.is_assigned_to(_date=_date)

    def extract(self) -> list[ShiftUid]:
        """
        Extract a list of shift UIDs that this nurse is assigned to in the solution.
        """
        result = []
        for _date, shift_uids in self.dates.items():
            shift = self.is_assigned_to(_date).value
            if not shift:
                continue
            mapping = {i+1: shift_uids[i] for i in range(len(shift_uids))}
            result.append(mapping[shift])
        return result






class NurseDecisionVarsIP:
    """
    A container to create and manage the decision variables for a single nurse.

    Each nurse has one Boolean variable for each shift, indicating whether the nurse is assigned to that shift.
    This class also provides helper methods to iterate over assignments and extract results.
    """

    def __init__(self, nurse: Nurse, shifts: list[Shift], model: HxModel):
        self.nurse = nurse
        self.shifts = shifts
        self.model = model
        # Create one Boolean decision variable per shift for this nurse
        self._x = {
            shift.uid: model.bool()
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
        self.model.add_constraint(self._x[shift_uid] == value)

    def is_assigned_to(self, shift_uid: ShiftUid):# -> cp_model.BoolVarT:
        """
        Return the decision variable for the given shift UID.
        This variable is True if the nurse is assigned to that shift, and False otherwise.
        """
        return self._x[shift_uid]

    def iter_shifts(self):# -> Iterable[tuple[Shift, cp_model.BoolVarT]]:
        """
        Iterate over all (shift, variable) pairs for this nurse.
        """
        for shift in self.shifts:
            yield shift, self.is_assigned_to(shift_uid=shift.uid)

    def extract(self) -> list[ShiftUid]:
        """
        Extract a list of shift UIDs that this nurse is assigned to in the solution.
        """
        return [shift_uid for shift_uid in self._x if self._x[shift_uid].value]
    

class NurseWorksAtWeekendVarsIP:
    """
    Weekend indicator: 1 if nurse works any shift on Saturday or Sunday.
    CP-SAT used add_max_equality; in Gurobi we linearize:
      weekend_var >= each shift_var
      weekend_var <= sum(shift_vars)
    """
    def __init__(self, nv: NurseDecisionVarsIP, weekends, shifts_by_date, model: HxModel):
        saturday = 0
        sunday = 1
        self.nurse = nv.nurse
        self.model = model
        self._x = {
            weekend: model.bool() for weekend in weekends
        }
        for weekend in weekends:
            shifts_on_weekend = shifts_by_date.get(weekend[saturday], []) + shifts_by_date.get(weekend[sunday], [])
            _vars = [nv.is_assigned_to(shift) for shift in shifts_on_weekend]
            if _vars:
                
                for shift in shifts_on_weekend:
                    model.add_constraint(self._x[weekend] >= nv.is_assigned_to(shift))
                model.add_constraint(self._x[weekend] <= model.sum(nv.is_assigned_to(shift) for shift in shifts_on_weekend))
                
            else:
                model.add_constraint(self._x[weekend] == 0)

    def is_assigned_to(self, weekend):
        return self._x[weekend]
    
class PreferredCoverDecisionVarsIP:
    def __init__(self, shifts: list[Shift], model: HxModel):
        
        self.total_below_preferred = {
            shift.uid: model.int(0, len(shifts))
            for shift in shifts
        }
        self.total_above_preferred = {
            shift.uid: model.int(0, len(shifts))
            for shift in shifts
        }
        self.cover_vars = (self.total_below_preferred, self.total_above_preferred)