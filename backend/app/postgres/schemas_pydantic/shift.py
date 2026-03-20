from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional


class ShiftCreate(BaseModel):
    id: UUID
    uid: int
    name: str
    start_time: str  # ISO datetime string
    end_time: str    # ISO datetime string
    demand: int = 0
    type: str
    not_followed_by_shift_types: List[UUID] = Field(default_factory=list)
    weight_below_demand: int = 0
    weight_above_demand: int = 0


class ShiftUpdate(BaseModel):
    name: str
    start_time: str
    end_time: str
    demand: int
    type: str
    not_followed_by_shift_types: List[UUID]
    weight_below_demand: int
    weight_above_demand: int


class ShiftResponse(BaseModel):
    id: UUID
    uid: int
    name: str
    start_time: str
    end_time: str
    demand: int
    type: str
    not_followed_by_shift_types: List[UUID]
    weight_below_demand: int
    weight_above_demand: int

    class Config:
        from_attributes = True