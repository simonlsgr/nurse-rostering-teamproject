import gurobipy as gp
from gurobipy import GRB

from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution
from .nurse_vars import NurseDecisionVars
from .modules import (
    ShiftAssignmentModule,
    OneShiftPerDayModule,
    ShiftRotationModule,
    MaximumShiftTypesModule,
    MaximizePreferences,
    OffPreferences,
    PreferStaffModule,
    LimitWorkTimeModule,
    MaximumConsecutiveShiftsModule,
    MinimumConsecutiveShiftsModule,
    MinimumConsecutiveDaysOffModule,
    MaximumNumberOfWeekendsModule,
    DaysOffModule,
    CoverRequirementsModule,
)
from nurse_rostering.solvers.gurobi.utils.generalize_return_status import generalize_return_status


class NurseRosteringModel:
    """
    A compact and extensible solver for the nurse rostering problem using Gurobi.
    """

    def __init__(self, instance: NurseRosteringInstance, model: gp.Model | None = None):
        self.instance = instance
        self.model = model or gp.Model("nurse_rostering")
        self.nurse_vars = [
            NurseDecisionVars(nurse, instance.shifts, self.model) for nurse in instance.nurses
        ]

        self.modules: list[ShiftAssignmentModule] = [
            MaximumShiftTypesModule(),
            OneShiftPerDayModule(),
            ShiftRotationModule(),
            MaximizePreferences(),
            PreferStaffModule(),
            LimitWorkTimeModule(),
            MaximumConsecutiveShiftsModule(),
            MinimumConsecutiveShiftsModule(),
            MinimumConsecutiveDaysOffModule(),
            MaximumNumberOfWeekendsModule(),
            CoverRequirementsModule(),
            OffPreferences(),
            DaysOffModule(),
        ]

        # Build constraints + objective expression
        terms = [module.build(instance, self.model, self.nurse_vars) for module in self.modules]
        objective = gp.quicksum(
            term if term is not None else 0 for term in terms
        )
        self.model.setObjective(objective, GRB.MINIMIZE)

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

        
        status = self.model.Status
        if self.model.SolCount < 1:
            return NurseRosteringSolution(
                nurses_at_shifts={},
                objective_value=-1,
                return_status=generalize_return_status(status, self.model.SolCount),
                lower_bound=-1,
            )
            
            


        nurses_at_shifts: dict[int, list[int]] = {}
        for nurse_model in self.nurse_vars:
            for shift_uid in nurse_model.extract():
                nurses_at_shifts.setdefault(shift_uid, []).append(nurse_model.nurse.uid)

        obj_val = self.model.ObjVal

        return NurseRosteringSolution(
            nurses_at_shifts=nurses_at_shifts,
            objective_value=int(round(obj_val)),
            return_status=generalize_return_status(status, self.model.SolCount),
            lower_bound=round(round(self.model.ObjBound)),
        )
