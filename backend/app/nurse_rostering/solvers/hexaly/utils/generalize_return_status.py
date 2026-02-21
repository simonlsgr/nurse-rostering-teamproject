import hexaly.optimizer as hx
from nurse_rostering.data_schema import SolverReturnStatus

def generalize_return_status(hexaly_status: hx.HxSolutionStatus):
    if hexaly_status == hx.HxSolutionStatus.OPTIMAL:
        return SolverReturnStatus.OPTIMAL
    elif hexaly_status == hx.HxSolutionStatus.FEASIBLE:
        return SolverReturnStatus.FEASIBLE
    elif hexaly_status == hx.HxSolutionStatus.INFEASIBLE:
        return SolverReturnStatus.INFEASIBLE
    elif hexaly_status == hx.HxSolutionStatus.INCONSISTENT:
        return SolverReturnStatus.MODEL_INVALID