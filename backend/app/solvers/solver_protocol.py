from typing import Protocol
from solvers.data_schema import NurseRosteringInstance, NurseRosteringSolution

"""
This is a protocol defining the strucure the model of a solver has to fulfill. Therefore, it is the interface all solvers should implement.
"""
class NurseRosteringModel(Protocol):
    
    def __init__(self, instance: NurseRosteringInstance, model) -> None:
        ...
    
    def solve(self, log_search_progress: bool = True, max_time_in_seconds: float = 60.0, **solver_params) -> NurseRosteringSolution:
        ...