from ortools.sat.python import cp_model
from nurse_rostering.solvers.cp_sat.model.nurse_vars import NurseDecisionVars, PreferredCoverDecisionVars
from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution
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
    OneShiftPerDayModule
)
from nurse_rostering.solvers.cp_sat.utils.generalize_return_status import generalize_return_status


class NurseRosteringModel:
    """
    A compact and extensible solver for the nurse rostering problem using CP-SAT.
    """

    def __init__(
        self, instance: NurseRosteringInstance, model: cp_model.CpModel | None = None
    ):
        self.instance = instance
        self.model = model or cp_model.CpModel()
        self.nurse_vars = [
            NurseDecisionVars(nurse, instance.shifts, self.model)
            for nurse in instance.nurses
        ]

        self.modules: list[ShiftAssignmentModule] = [
            OneShiftPerDayModule(),
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

        terms = [module.build(instance, self.model, self.nurse_vars) for module in self.modules]
        objective = sum(
            term if term is not None else 0 for term in terms
        )
        self.model.minimize(objective)

    def solve(
        self,
        log_search_progress: bool = True,
        max_time_in_seconds: float = 60.0,
        **solver_params,
    ) -> NurseRosteringSolution:
        solver = cp_model.CpSolver()
        solver.parameters.log_search_progress = log_search_progress
        solver.parameters.max_time_in_seconds = max_time_in_seconds
        for key, value in solver_params.items():
            setattr(solver.parameters, key, value)

        status = solver.solve(self.model)
        if status == cp_model.INFEASIBLE:
            raise ValueError("The model is infeasible.")
        elif status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise ValueError("Solver failed to find a feasible solution.")

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
