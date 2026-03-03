from pydantic import BaseModel
from typing import List, Dict
from uuid import UUID


class NurseCreate(BaseModel):
    id: UUID
    uid: int
    name: str
    preferred_shifts: List[int]
    preferred_off_shifts: List[int]
    blocked_shifts: List[int]
    days_off: List[str]
    staff: bool
    min_time_between_shifts: str
    preferred_shift_weight: Dict[str, int]
    preferred_off_shift_weight: Dict[str, int]
    minimum_work_time: int
    maximum_work_time: int
    minimum_consecutive_shifts: int
    maximum_consecutive_shifts: int
    minimum_consecutive_days_off: int
    maximum_weekends: int
    maximum_number_of_shifts_per_type: Dict[str, int]


class NurseUpdate(NurseCreate):
    
    pass


class NurseResponse(NurseCreate):

    class Config:
        from_attributes = True