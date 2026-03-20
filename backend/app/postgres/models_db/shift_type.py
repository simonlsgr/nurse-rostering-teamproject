from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from ..database import Base
import uuid

class ShiftType(Base):
    __tablename__ = "shift_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    project = relationship("Project", back_populates="shift_types")

    name = Column(String, nullable=False)

    duration = Column(String, nullable=False)  # "HH:mm:ss"
    start = Column(String, nullable=False)     # "HH:mm:ss"
    end = Column(String, nullable=False)       # "HH:mm:ss"

    # list of ids of other shift types
    not_followed_by_shift_types = Column(
        ARRAY(UUID(as_uuid=True)),
        nullable=False,
        default=list
    )