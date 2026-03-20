from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from ..database import Base
import uuid


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uid = Column(BigInteger, nullable=False, unique=True)

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    project = relationship("Project", back_populates="shifts", passive_deletes=True)

    name = Column(String, nullable=False)
    start_time = Column(String, nullable=False)  # ISO datetime string
    end_time = Column(String, nullable=False)    # ISO datetime string
    demand = Column(Integer, nullable=False, default=0)
    type = Column(String, nullable=False)
    not_followed_by_shift_types = Column(ARRAY(UUID(as_uuid=True)), nullable=False, default=list)
    weight_below_demand = Column(Integer, nullable=False, default=0)
    weight_above_demand = Column(Integer, nullable=False, default=0)