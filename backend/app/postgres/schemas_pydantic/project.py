from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Tuple

class ProjectCreate(BaseModel):
    id: UUID
    name: str
    planning_horizon: Tuple[str, str]


class ProjectUpdate(BaseModel):
    name: str
    planning_horizon: Tuple[str, str]


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    planning_horizon: Tuple[str, str]
    created_at: datetime
    last_modified: datetime

    class Config:
        from_attributes = True  # for SQLAlchemy