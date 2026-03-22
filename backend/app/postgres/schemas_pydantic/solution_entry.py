from pydantic import BaseModel
from typing import Dict, Any
from uuid import UUID
from datetime import datetime

class SolutionEntryCreate(BaseModel):
    solution_name: str
    solution: Dict[str, Any]
    solver: str
    return_status: str

class SolutionEntryUpdate(BaseModel):
    solution_name: str
    solution: Dict[str, Any]
    solver: str
    return_status: str

class SolutionEntryResponse(BaseModel):
    id: UUID
    solution_name: str
    solution: Dict[str, Any]
    solver: str
    return_status: str

    class Config:
        from_attributes = True