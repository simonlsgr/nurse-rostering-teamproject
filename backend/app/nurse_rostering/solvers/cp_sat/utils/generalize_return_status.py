
from ortools.sat.python import cp_model
from nurse_rostering.data_schema import SolverReturnStatus

def generalize_return_status(cpsat_status) -> SolverReturnStatus:
    if cpsat_status == cp_model.OPTIMAL:
        return SolverReturnStatus.OPTIMAL
    elif cpsat_status == cp_model.FEASIBLE:
        return SolverReturnStatus.FEASIBLE
    elif cpsat_status == cp_model.INFEASIBLE:
        return SolverReturnStatus.INFEASIBLE
    elif cpsat_status == cp_model.MODEL_INVALID:
        return SolverReturnStatus.MODEL_INVALID
    elif cpsat_status == cp_model.UNKNOWN:
        return SolverReturnStatus.UNKNOWN