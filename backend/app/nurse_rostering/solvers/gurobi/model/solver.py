from typing import Any

import gurobipy as gp
from gurobipy import GRB

from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution, ShiftUid, NurseUid, SolverFormulation
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

    def __init__(self, instance: NurseRosteringInstance, model: gp.Model | None = None, hints: dict[ShiftUid, list[NurseUid]] | None = None, formulation: SolverFormulation | None = SolverFormulation.IP):
        if formulation != SolverFormulation.IP:
            raise ValueError(f"Gurobi only supports an IP formulation. {formulation} was provided.")
        
        self.instance = instance
        self.model = model or gp.Model("nurse_rostering")
        self.hints = hints
        
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

        if self.hints is not None:
            for nv in self.nurse_vars:
                for shiftuid, nurseuids in self.hints.items():
                    if nv.nurse.uid in nurseuids:
                        nv._x[shiftuid].Start = 1
        
        # Build constraints + objective expression
        terms = [module.build(instance, self.model, self.nurse_vars) for module in self.modules]
        objective = gp.quicksum(
            term if term is not None else 0 for term in terms
        )
        self.model.setObjective(objective, GRB.MINIMIZE)

    def _set_nurses_to_shifts(self, nurses_at_shifts_forced) -> None:
        if not nurses_at_shifts_forced:
            return

        nurse_vars_by_uid = {nv.nurse.uid: nv for nv in self.nurse_vars}

        for shift_uid, nurse_uids in nurses_at_shifts_forced.items():

            for nurse_uid in nurse_uids:
                nurse_vars = nurse_vars_by_uid.get(nurse_uid)
                nurse_vars.fix(int(shift_uid), True)

    def solve(
        self,
        log_search_progress: bool = True,
        max_time_in_seconds: float = 60.0,
        **solver_params,
    ) -> NurseRosteringSolution:
        # Basic params
        self.model.Params.OutputFlag = 1 if log_search_progress else 0
        self.model.Params.TimeLimit = float(max_time_in_seconds)
        meta_params: dict[str, Any] = {}
        for key, value in solver_params.items():
            if key.startswith("meta_param_"):
                meta_key = key[len("meta_param_"):]
                meta_params[meta_key] = value
                continue

        nurses_at_shifts_forced = meta_params.get("nurses_at_shifts_forced")
        if nurses_at_shifts_forced is not None:
            self._set_nurses_to_shifts(nurses_at_shifts_forced)

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
