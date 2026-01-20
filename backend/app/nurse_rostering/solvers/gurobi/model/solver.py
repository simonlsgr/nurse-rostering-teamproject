import gurobipy as gp
from gurobipy import GRB

from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution
from nurse_rostering.solvers.gurobi.model.nurse_vars import NurseDecisionVars
from .modules import (
    ShiftAssignmentModule,
    NoBlockedShiftsModule,
    MinTimeBetweenShifts,
    MaximizePreferences,
    PreferStaffModule,
    LimitWorkTimeModule,
    MaximumConsecutiveShiftsModule,
    MinimumConsecutiveShiftsModule,
    MinimumConsecutiveDaysOffModule,
    MaximumNumberOfWeekendsModule,
    CoverRequirementsModule,
)


class NurseRosteringModel:
    """
    A compact and extensible solver for the nurse rostering problem using Gurobi.
    """

    def __init__(self, instance: NurseRosteringInstance, model: gp.Model | None = None):
        self.instance = instance
        self.model = model or gp.Model("nurse_rostering")

        # Decision vars: one binary per (nurse, shift)
        self.nurse_vars = [
            NurseDecisionVars(nurse, instance.shifts, self.model) for nurse in instance.nurses
        ]

        # Same module pipeline
        self.modules: list[ShiftAssignmentModule] = [
            NoBlockedShiftsModule(),
            MinTimeBetweenShifts(),
            MaximizePreferences(),
            PreferStaffModule(),
            LimitWorkTimeModule(),
            MaximumConsecutiveShiftsModule(),
            MinimumConsecutiveShiftsModule(),
            MinimumConsecutiveDaysOffModule(),
            MaximumNumberOfWeekendsModule(),
            CoverRequirementsModule(),
        ]

        # Build constraints + objective expression
        obj = gp.LinExpr()
        for module in self.modules:
            term = module.build(instance, self.model, self.nurse_vars)
            if term is not None:
                obj += term

        self.model.ModelSense = GRB.MINIMIZE
        self.model.setObjective(obj)

    def solve(
        self,
        log_search_progress: bool = True,
        max_time_in_seconds: float = 60.0,
        **solver_params,
    ) -> NurseRosteringSolution:
        # Basic params
        self.model.Params.OutputFlag = 1 if log_search_progress else 0
        self.model.Params.TimeLimit = float(max_time_in_seconds)

        # Optional extra params (e.g. MIPGap, Threads, etc.)
        for key, value in solver_params.items():
            try:
                setattr(self.model.Params, key, value)
            except Exception:
                # Ignore unknown params to keep interface flexible
                pass

        self.model.optimize()

        # Handle statuses
        if self.model.Status in (GRB.INFEASIBLE, GRB.INF_OR_UNBD):
            raise ValueError("The model is infeasible.")
        if self.model.Status not in (GRB.OPTIMAL, GRB.TIME_LIMIT, GRB.SUBOPTIMAL):
            raise ValueError(f"Solver failed (status={self.model.Status}).")

        # Extract solution 
        nurses_at_shifts: dict[int, list[int]] = {}
        for nurse_model in self.nurse_vars:
            for shift_uid in nurse_model.extract():
                nurses_at_shifts.setdefault(shift_uid, []).append(nurse_model.nurse.uid)

        # Objective value: Gurobi returns float, we store int like CP-SAT
        obj_val = self.model.ObjVal if self.model.SolCount > 0 else 0.0

        return NurseRosteringSolution(
            nurses_at_shifts=nurses_at_shifts,
            objective_value=int(round(obj_val)),
        )
