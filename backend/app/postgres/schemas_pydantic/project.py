from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str

class ProjectResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    last_modified: datetime

    class Config:
        from_attributes = True  # for SQLAlchemy