from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    BigInteger
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from ..database import Base
import uuid



class Nurse(Base):
    __tablename__ = "nurses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project = relationship("Project", back_populates="nurses")

    uid = Column(BigInteger, nullable=False, unique=True)
    name = Column(String, nullable=False)

    preferred_shifts = Column(ARRAY(BigInteger), nullable=False, default=list)
    preferred_off_shifts = Column(ARRAY(BigInteger), nullable=False, default=list)
    blocked_shifts = Column(ARRAY(BigInteger), nullable=False, default=list)
    days_off = Column(ARRAY(String), nullable=False, default=list)

    staff = Column(Boolean, nullable=False)

    min_time_between_shifts = Column(String, nullable=False)

    preferred_shift_weight = Column(JSONB, nullable=False, default=dict)
    preferred_off_shift_weight = Column(JSONB, nullable=False, default=dict)

    minimum_work_time = Column(Integer, nullable=False)
    maximum_work_time = Column(Integer, nullable=False)

    minimum_consecutive_shifts = Column(Integer, nullable=False)
    maximum_consecutive_shifts = Column(Integer, nullable=False)

    minimum_consecutive_days_off = Column(Integer, nullable=False)

    maximum_weekends = Column(Integer, nullable=False)

    maximum_number_of_shifts_per_type = Column(JSONB, nullable=False, default=dict)