"""
This module defines the data schema for the nurse rostering problem.
Note that this is just a random variant of the nurse rostering problem.

We define the instance and solution data structures using Pydantic.
"""

from datetime import datetime, timedelta, date
from pydantic import BaseModel, Field, NonNegativeInt, model_validator
import uuid
from typing import Optional
import enum

# Semantic type aliases for clarity
NurseUid = int
ShiftUid = int


def generate_random_uid() -> int:
    # Use uuid4 and convert to an integer (truncated to 64 bits for practical use)
    return uuid.uuid4().int & ((1 << 53) - 1)


# create an enum class which has the return status values
class SolverReturnStatus(str, enum.Enum):
    OPTIMAL = "OPTIMAL"
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    UNBOUNDED = "UNBOUNDED"
    MODEL_INVALID = "MODEL_INVALID"
    UNKNOWN = "UNKNOWN"

class SolverFormulation(str, enum.Enum):
    IP = "IP"
    AUTOMATON = "AUTOMATON"
    SET = "SET"
    TABLE = "TABLE"
    

class Nurse(BaseModel):
    uid: NurseUid = Field(
        default_factory=generate_random_uid,
        description="Unique identifier for the nurse",
    )
    name: str = Field(..., description="Name of the nurse")
    preferred_shifts: set[ShiftUid] = Field(
        ..., description="List of preferred shift UIDs for the nurse"
    )
    preferred_off_shifts: set[ShiftUid] = Field(
        default_factory=set,
        description="List of preferred off shift UIDs for the nurse",
    )
    
    blocked_shifts: set[ShiftUid] = Field(
        ..., description="List of blocked shift UIDs for the nurse"
    )
    days_off: Optional[set[date]] = Field(
        default=None,
        description="Days where Nurse can't work"
    )
    staff: bool = Field(
        ...,
        description="Indicates if the nurse is a staff member (True) or a contractor (False)",
    )
    min_time_between_shifts: Optional[timedelta] = Field(
        default=None,
        description="Minimum off duty time between two shifts for the same nurse"
    )
    preferred_shift_weight: dict[ShiftUid, NonNegativeInt] = Field(
        default={},
        description="The weight in the objective function for every assigned preference. Equivalent to q in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf.",
    )
    preferred_off_shift_weight: dict[ShiftUid, NonNegativeInt] = Field(
        default={},
        description="The weight in the objective function for every assigned preferred off shift. Equivalent to p in https://www.schedulingbenchmarks.org/papers/computational_results_on_new_staff_scheduling_benchmark_instances.pdf.",
    )
    minimum_work_time: Optional[int] = Field(
        default=None,
        description="Minimum work time minutes"
    )
    maximum_work_time: Optional[int] = Field(
        default=None,
        description="Maximum work time in minutes"
    )
    minimum_consecutive_shifts: Optional[int] = Field(
        default=None,
        description="Minimum consecutive shifts"
    )
    maximum_consecutive_shifts: Optional[int] = Field(
        default=None,
        description="Maximum consecutive shifts"
    )
    minimum_consecutive_days_off: Optional[int] = Field(
        default=None,
        description="Minimum consecutive days off"
    )
    maximum_weekends: Optional[int] = Field(
        default=None,
        description="Maximum weekends"
    )
    maximum_number_of_shifts_per_type: Optional[dict[str, int]] = Field(
        default=None,
        description="Maximum number of shifts per shift type for the nurse",
    )
    
    



class Shift(BaseModel):
    uid: ShiftUid = Field(
        default_factory=generate_random_uid,
        description="Unique identifier for the shift",
    )
    name: str = Field(..., description="Name of the shift (e.g., '2025-01-01 Morning')")
    start_time: datetime = Field(
        ..., description="Start time of the shift as a full datetime (YYYY-MM-DD HH:MM)"
    )
    end_time: datetime = Field(
        ..., description="End time of the shift as a full datetime (YYYY-MM-DD HH:MM)"
    )
    demand: NonNegativeInt = Field(
        ..., description="Number of nurses required for this shift"
    )
    type: Optional[str] = Field(
        default=None,
        description="Optional type/category of the shift (e.g., 'morning', 'night')",
    )
    not_followed_by_shift_types: Optional[set[str]] = Field(
        default=None,
        description="Set of shift types that can not directly follow this shift",
    )
    weight_below_demand: Optional[int] = Field(
        default=1,
        description="The weight in the objective function for each understaffed nurse below demand.",
    )
    weight_above_demand: Optional[int] = Field(
        default=1,
        description="The weight in the objective function for each overstaffed nurse above demand.",
    )
    @property
    def length(self) -> int:
        """
        Compute the length of the shift as in minutes.
        """
        delta: timedelta = self.end_time - self.start_time
        return int(delta.total_seconds() // 60)
    


class NurseRosteringInstance(BaseModel):
    """
    This schema defines the INPUT for the nurse rostering problem.
    """

    nurses: list[Nurse] = Field(
        ..., description="List of nurses in the rostering instance"
    )
    shifts: list[Shift] = Field(
        ...,
        description="List of shifts that need to be covered. Shifts must be sorted in time.",
    )
    staff_weight: int = Field(
        default=1,
        description="The weight in the objective function for each assigned staff nurse.",
    )
    
    @property
    def planning_horizon_in_days(self) -> int:
        """
        Compute the planning horizon in days based on the shifts.
        """
        if not self.shifts:
            return 0
        start_date = self.shifts[0].start_time.date()
        end_date = self.shifts[-1].start_time.date()
        return (end_date - start_date).days + 1

    @model_validator(mode="after")
    def validate_shifts_unique_uids(self):
        """
        Ensure that all shifts have unique UIDs to avoid conflicts.
        """
        shift_uids = {shift.uid for shift in self.shifts}
        if len(shift_uids) != len(self.shifts):
            raise ValueError("Shift UIDs must be unique.")
        return self

    @model_validator(mode="after")
    def validate_nurses_unique_uids(self):
        """
        Ensure that all nurses have unique UIDs to avoid conflicts.
        """
        nurse_uids = {nurse.uid for nurse in self.nurses}
        if len(nurse_uids) != len(self.nurses):
            raise ValueError("Nurse UIDs must be unique.")
        return self

    @model_validator(mode="after")
    def validate_shifts_sorted_by_time(self):
        """
        Ensure that shifts are sorted by start time.
        """
        for shift_a, shift_b in zip(self.shifts, self.shifts[1:]):
            if shift_a.start_time > shift_b.start_time:
                raise ValueError("Shifts must be sorted by start time.")
        return self


class NurseRosteringSolution(BaseModel):
    """
    This schema defines the OUTPUT for the nurse rostering problem.
    """

    nurses_at_shifts: dict[ShiftUid, list[NurseUid]] = Field(
        ..., description="Maps shift UIDs to lists of assigned nurse UIDs."
    )
    objective_value: int = Field(
        description="Objective value of the computed solution."
    )
    return_status: SolverReturnStatus = Field(
        ..., description="Return status of the solver after attempting to solve the instance."
    )
    lower_bound: Optional[int] = Field(
        default=None,
        description="Lower bound on the objective value, if available from the solver.",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Time when the solution was generated. Takes little space and can be extremely useful when investigating issues with the solution. Optimally, also add the revision of the algorithm that generated the solution, e.g., by using a git commit hash.",
    )
    
    # Validation of the solution will be handled in a separate module.


class OptimizationParameters(BaseModel):
    timeout: int = Field(
        default=60,
        gt=0,
        description="The maximum time in seconds to run the optimization.",
    )
    nurses_at_shifts_forced: dict = Field(
        default={},
        description="A dictionary containing shiftuids as keys and a list of nursuids as values. If a nurse-shift pair appears, the corresponding variable will be fixed to 1."
    )
