from ortools.sat.python import cp_model
from nurse_rostering.solvers.cp_sat.model.nurse_vars import NurseDecisionVars, PreferredCoverDecisionVars
from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution, NurseUid, ShiftUid
from typing import Any

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
    CoverRequirementsModule, NoBlockedShiftsModule,
)
from nurse_rostering.solvers.cp_sat.utils.generalize_return_status import generalize_return_status


class NurseRosteringModel:
    """
    A compact and extensible solver for the nurse rostering problem using CP-SAT.
    """

    def __init__(
        self, instance: NurseRosteringInstance, model: cp_model.CpModel | None = None, hints: dict[Any, Any] | None = None
    ):
        self.instance = instance
        self.model = model or cp_model.CpModel()
        self.nurse_vars = [
            NurseDecisionVars(nurse, instance.shifts, self.model)
            for nurse in instance.nurses
        ]
        self.hints = hints

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
            NoBlockedShiftsModule(),
        ]

        objective = sum(
            module.build(instance, self.model, self.nurse_vars) for module in self.modules
        )

        if self.hints is not None:
            for nv in self.nurse_vars:
                shifts = self.hints.get(nv.nurse.uid, [])
                for shift in shifts:
                    self.model.add_hint(nv.is_assigned_to(shift), 1)

        
        self.model.minimize(objective)
    
    def _set_nurses_to_shifts(self, nurses_at_shifts_forced) -> None:
        print("-------------DDDDDDDDDDDDDDDDDDDDDDDDDDDD", nurses_at_shifts_forced)
        if not nurses_at_shifts_forced:
            return

        nurse_vars_by_uid = {nv.nurse.uid: nv for nv in self.nurse_vars}

        for shift_uid, nurse_uids in nurses_at_shifts_forced.items():
            for nurse_uid in nurse_uids:
                nurse_vars = nurse_vars_by_uid.get(nurse_uid)
                nurse_vars.fix(int(shift_uid), True)
                

    def solve(
        self,
        log_search_progress: bool = False,
        max_time_in_seconds: float = 60.0,
        **solver_params,
    ) -> NurseRosteringSolution:
        solver = cp_model.CpSolver()
        solver.parameters.log_search_progress = log_search_progress
        solver.parameters.max_time_in_seconds = max_time_in_seconds
        meta_params: dict[str, Any] = {}
        print(solver_params)
        for key, value in solver_params.items():
            if key.startswith("meta_param_"):
                meta_key = key[len("meta_param_"):]
                meta_params[meta_key] = value
                continue

            setattr(solver.parameters, key, value)

        nurses_at_shifts_forced = meta_params.get("nurses_at_shifts_forced")
        if nurses_at_shifts_forced is not None:
            self._set_nurses_to_shifts(nurses_at_shifts_forced)

        status = solver.solve(self.model)
        
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return NurseRosteringSolution(
                nurses_at_shifts={},
                objective_value=-1,
                return_status=generalize_return_status(status),
                lower_bound=-1,
            )

        nurses_at_shifts = {}
        for nurse_model in self.nurse_vars:
            for shift_uid in nurse_model.extract(solver):
                nurses_at_shifts.setdefault(shift_uid, []).append(nurse_model.nurse.uid)

        return NurseRosteringSolution(
            nurses_at_shifts=nurses_at_shifts,
            objective_value=round(solver.objective_value),
            return_status=generalize_return_status(status),
            lower_bound=round(solver.best_objective_bound),
        )
