import gurobipy as gp
from gurobipy import GRB



class AssertModelFeasible:

    def __enter__(self) -> gp.Model:
        self.model = gp.model()
        return self.model

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            raise exc_type(exc_val)
       
        self.model.optimize()
        status = self.model.Status

        if status not in (GRB.OPTIMAL) or self.model.SolCount < 1:
            raise RuntimeError(
                f"Expected feasible, but solver returned status {status}."
            )


class AssertModelInfeasible:

    def __enter__(self) -> gp.Model:
        self.model = gp.model()
        return self.model

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            raise exc_type(exc_val)

        self.model.optimize()
        status = self.model.Status

        if status not in (GRB.INFEASIBLE) or self.model.SolCount > 0:
            raise RuntimeError(
                f"Expected infeasible, but solver returned status {status}."
            )
