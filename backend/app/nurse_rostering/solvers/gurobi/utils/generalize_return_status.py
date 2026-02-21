
import gurobipy as gp
from gurobipy import GRB
from nurse_rostering.data_schema import SolverReturnStatus

# TODO: imporove status mapping
def generalize_return_status(status, solCount) -> SolverReturnStatus:
    if status == GRB.OPTIMAL:
        return SolverReturnStatus.OPTIMAL
    elif solCount > 0:
        return SolverReturnStatus.FEASIBLE
    elif status == GRB.INFEASIBLE:
        return SolverReturnStatus.INFEASIBLE
    else:
        return SolverReturnStatus.UNKNOWN