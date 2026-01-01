"""
This file contains the implementation of additional data models for the optimization API.
"""

from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field
from uuid import UUID, uuid4
from solvers.data_schema import NurseRosteringInstance, OptimizationParameters, NurseRosteringSolution


class NurseRosteringJobRequest(BaseModel):
    """
    A request model for a Nurse Rostering job.
    """

    nurse_rostering_instance: NurseRosteringInstance = Field(..., description="The Nurse Rostering instance to solve.")
    optimization_parameters: OptimizationParameters = Field(
        default_factory=OptimizationParameters,
        description="The optimization parameters.",
    )
    webhook_url: HttpUrl | None = Field(
        default=None, description="The URL to call once the computation is complete."
    )
    

class NurseRosteringJobStatus(BaseModel):
    """
    A response model for the status of a Nurse Rostering job.
    """

    task_id: UUID = Field(default_factory=uuid4, description="The ID of the task.")
    status: str = Field(default="Submitted", description="The status of the task.")
    submitted_at: datetime = Field(
        default_factory=datetime.now, description="The time the task was submitted."
    )
    started_at: datetime | None = Field(
        default=None, description="The time the task was started."
    )
    completed_at: datetime | None = Field(
        default=None, description="The time the task was completed."
    )
    error: str | None = Field(
        default=None, description="The error message if the task failed."
    )