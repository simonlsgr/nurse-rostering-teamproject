import uuid
from sqlalchemy import Column, Text, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..database import Base
from sqlalchemy.orm import relationship


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    planning_start = Column(Date, nullable=False)
    planning_end = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_modified = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


    nurses = relationship(
        "Nurse",
        back_populates="project",
        passive_deletes=True
    )

    shift_types = relationship(
        "ShiftType",
        back_populates="project",
        passive_deletes=True
    )

    shifts = relationship(
        "Shift",
        back_populates="project",
        passive_deletes=True
    )


    @property
    def planning_horizon(self):
        if self.planning_start and self.planning_end:
            return (
                self.planning_start.isoformat(),
                self.planning_end.isoformat(),
            )
        return None