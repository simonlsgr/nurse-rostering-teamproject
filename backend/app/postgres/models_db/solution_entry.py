from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from ..database import Base

import uuid

class SolutionEntry(Base):
    __tablename__ = "solution_entries"

    solutionId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    project = relationship("Project", back_populates="solutions", passive_deletes=True)

    solution_name = Column(String, nullable=False)
    solver = Column(String, nullable=False)
    return_status = Column(String, nullable=False)

    solution = Column(JSONB, nullable=False)