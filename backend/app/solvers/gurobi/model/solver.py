import gurobipy as gp
from gurobipy import GRB 
from .nurse_vars import NurseDecisionVars
from ...data_schema import NurseRosteringInstance, NurseRosteringSolution
from .modules import (
    ShiftAssignmentModule,
    NoBlockedShiftsModule,
    DemandSatisfactionModule,
    MinTimeBetweenShifts,
    MaximizePreferences,
    PreferStaffModule,
)


class NurseRosteringModel:
    """
    A compact and extensible solver for the nurse rostering problem using Gurobi.
    """

    def __init__(
        self, instance: NurseRosteringInstance, model: gp.Model | None = None
    ):
        self.instance = instance
        self.model = model or gp.Model()
        self.nurse_vars = [
            NurseDecisionVars(nurse, instance.shifts, self.model)
            for nurse in instance.nurses
        ]

        self.modules: list[ShiftAssignmentModule] = [
            NoBlockedShiftsModule(),
            DemandSatisfactionModule(),
            MinTimeBetweenShifts(),
            MaximizePreferences(),
            PreferStaffModule(),
        ]

        objective = gp.quicksum(
            module.build(instance, self.model, self.nurse_vars)  # type: ignore
            for module in self.modules
        )
        self.model.setObjective(objective, GRB.MINIMIZE)

    def solve(
        self,
        log_search_progress: bool = True,
        max_time_in_seconds: float = 60.0,
        **solver_params,
    ) -> NurseRosteringSolution:

        solver = self.model

        solver.Params.LogToConsole = log_search_progress
        solver.Params.TimeLimit = max_time_in_seconds
        
        for key, value in solver_params.items():
            setattr(solver.Params, key, value)

        solver.optimize()

        if solver.status == GRB.INFEASIBLE:
            raise ValueError("The model is infeasible.")
        elif solver.SolCount < 1:
            raise ValueError("Solver failed to find a feasible solution.")

        nurses_at_shifts = {}
        for nurse_model in self.nurse_vars:
            for shift_uid in nurse_model.extract(solver):
                nurses_at_shifts.setdefault(shift_uid, []).append(nurse_model.nurse.uid)

        return NurseRosteringSolution(
            nurses_at_shifts=nurses_at_shifts,
            objective_value=round(solver.ObjVal),
        )
