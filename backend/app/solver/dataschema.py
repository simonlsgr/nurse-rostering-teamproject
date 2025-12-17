

from pydantic import BaseModel, HttpUrl, Field


class NurseRosteringInstance(BaseModel):
    pass


class OptimizationParameters(BaseModel):
    timeout: int = Field(
        default=60,
        gt=0,
        description="The maximum time in seconds to run the optimization.",
    )


class NurseRosteringSolution(BaseModel):
    
    is_infeasible: bool = Field(
        default=False, description="Whether the instance is infeasible."
    )


