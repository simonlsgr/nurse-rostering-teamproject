
import gurobipy as gp
from gurobipy import GRB
from nurse_rostering.data_schema import SolverReturnStatus

# TODO: imporove status mapping
def generalize_return_status(cpsat_status) -> SolverReturnStatus:
    if cpsat_status == GRB.OPTIMAL:
        return SolverReturnStatus.OPTIMAL
    elif cpsat_status == GRB.INFEASIBLE:
        return SolverReturnStatus.INFEASIBLE
    else:
        return SolverReturnStatus.UNKNOWN