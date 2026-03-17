

from hexaly.optimizer import HxCallbackType, HxSolutionStatus
from nurse_rostering.data_schema import SolverFormulation


class HXLYCallback:
    def __init__(self, formulation: SolverFormulation) -> None:
        self.cbType = HxCallbackType.TIME_TICKED
        self.data = []  
        self.formulation = formulation

    def call(self, optimizer, cb_type):
        stats = optimizer.statistics
        obj = optimizer.model.objectives[0].value
        bound = optimizer.solution.get_objective_bound(0)
        if optimizer.solution.status in (HxSolutionStatus.FEASIBLE, HxSolutionStatus.OPTIMAL):
            self.data.append(["hexaly-"+self.formulation.lower(), stats.get_running_time(), obj, bound])
        