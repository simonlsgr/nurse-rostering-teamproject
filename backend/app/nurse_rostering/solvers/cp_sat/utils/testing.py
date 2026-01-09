from ortools.sat.python import cp_model
from nurse_rostering.solvers.cp_sat.cp_sat_adapter import CpSatAdapter

class AssertModelFeasible:
    """
    Context manager that asserts a CP-SAT model is feasible which was created by the CpSatAdapter.

    Usage:
        with AssertModelFeasible() as model:
            # build model constraints
            x = model.new_bool_var("x")
            y = model.new_int_var(0, 10, "y")
            model.add(x + y == 1)
            # This will raise a RuntimeError if the model is infeasible.


    Raises:
        RuntimeError: If the model status is neither OPTIMAL nor FEASIBLE.
    """

    def __init__(
        self
    ):
        self.model = CpSatAdapter()

    def __enter__(self) -> cp_model.CpModel:
        return self.model

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            # Propagate exceptions raised inside the with-block
            raise exc_type(exc_val)
        status = self.model.solver.solve(self.model.model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise RuntimeError(
                f"Expected feasible, but solver returned status {status}."
            )


class AssertModelInfeasible:
    """
    Context manager that asserts a CP-SAT model is infeasible which was created by the CpSatAdapter.

    Usage:
        with AssertModelInfeasible() as model:
            # build model constraints that cannot all be satisfied
            x = model.new_bool_var("x")
            y = model.new_bool_var("y")
            model.add(x + y == 1)
            model.add(x + y == 2)
            # This will raise a RuntimeError if the model is feasible.

    Raises:
        RuntimeError: If the model is found to be feasible.
    """

    def __init__(
        self,
    ):
        self.model = CpSatAdapter()

    def __enter__(self) -> cp_model.CpModel:
        return self.model

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            raise exc_type(exc_val)
        status = self.model.solver.solve(self.model.model)
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise RuntimeError(
                f"Expected infeasible, but solver returned status {status}."
            )
            

def _solve(model: cp_model.CpModel, solver=None, time_limit=None):
    solver = solver or cp_model.CpSolver()
    if time_limit is not None:
        solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(model)
    return solver, status    

def assert_objective(
    adapter: CpSatAdapter,
    expected: float,
    tol: float = 1e-8,
    time_limit: float | None = None,
):
    """
    Solve `model`, assert it's feasible or optimal, then
    check |ObjectiveValue - expected| <= tol.
    """
    solver, status = _solve(adapter.model, adapter.solver, time_limit)
    assert status in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE,
    ), f"Expected feasible or optimal, got {status}"
    val = solver.objective_value
    assert abs(val - expected) <= tol, f"Expected objective≈{expected}, got {val}"
    return solver