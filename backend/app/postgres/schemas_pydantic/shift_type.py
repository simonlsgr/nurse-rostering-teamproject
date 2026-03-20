from pydantic import BaseModel
from uuid import UUID
from typing import List


class ShiftTypeCreate(BaseModel):
    id: UUID
    name: str
    duration: str  # "HH:mm:ss"
    start: str     # "HH:mm"
    end: str
    not_followed_by_shift_types: List[str]


class ShiftTypeUpdate(BaseModel):
    name: str
    duration: str
    start: str
    end: str
    not_followed_by_shift_types: List[str]


class ShiftTypeResponse(BaseModel):
    id: UUID
    name: str
    duration: str
    start: str
    end: str
    not_followed_by_shift_types: List[str]

    class Config:
        from_attributes = True