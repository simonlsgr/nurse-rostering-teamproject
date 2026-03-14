from typing import Any

import hexaly.optimizer
from nurse_rostering.solvers.hexaly.utils.generalize_return_status import generalize_return_status
from nurse_rostering.solvers.hexaly.model.nurse_vars import ShiftDecisionVars
from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution, SolverFormulation
from nurse_rostering.solvers.hexaly.model.modules import (
    ShiftAssignmentModule,
    OneShiftPerDayModuleSet,
    ShiftRotationModuleSet,
    MaximumShiftTypesModuleSet,
    LimitWorkTimeModuleSet,
    MaximumConsecutiveShiftsModuleSet,
    MinimumConsecutiveShiftsModuleSet,
    MinimumConsecutiveDaysOffModuleSet,
    MaximumNumberOfWeekendsModuleSet,
    DaysOffModuleSet,
    CoverRequirementsModuleSet,
    PreferStaffModuleSet,
    PreferredShiftsModuleSet,
)

class NurseRosteringModel:
    """
    A compact and extensible solver for the nurse rostering problem using Hexaly.
    """
    
    def __init__(
        self, instance: NurseRosteringInstance, model = None, formulation: SolverFormulation = SolverFormulation.SET
    ):
        self.instance = instance
        
        
        if formulation == SolverFormulation.SET:
            self.modules: list[ShiftAssignmentModule] = [
                OneShiftPerDayModuleSet(),
                ShiftRotationModuleSet(),
                MaximumShiftTypesModuleSet(),
                LimitWorkTimeModuleSet(),
                MaximumConsecutiveShiftsModuleSet(),
                MinimumConsecutiveShiftsModuleSet(),
                MinimumConsecutiveDaysOffModuleSet(),
                MaximumNumberOfWeekendsModuleSet(),
                DaysOffModuleSet(),
                CoverRequirementsModuleSet(),
                PreferStaffModuleSet(),
                PreferredShiftsModuleSet(),
            ]
        



        
    def solve(
        self,
        log_search_progress: bool = True,
        max_time_in_seconds: int = 60,
        **solver_params,
    ) -> NurseRosteringSolution:

        meta_params: dict[str, Any] = {}
        for key, value in solver_params.items():
            if key.startswith("meta_param_"):
                meta_key = key[len("meta_param_"):]
                meta_params[meta_key] = value
                continue
            else:
                setattr(optimizer.param, key, value)
        with hexaly.optimizer.HexalyOptimizer() as optimizer:
            
            
            model = optimizer.model
            
            self.shift_vars = [
                ShiftDecisionVars(shift, self.instance.nurses, model)
                for shift in self.instance.shifts
            ]

            def _set_nurses_to_shifts(nurses_at_shifts_forced) -> None:
                if not nurses_at_shifts_forced:
                    return

                shift_var_by_uid = {shift_var.shift.uid: shift_var for shift_var in self.shift_vars}
                for shift_uid, nurse_uids in nurses_at_shifts_forced.items():
                    shift_var = shift_var_by_uid[int(shift_uid)]
                    for nurse_uid in nurse_uids:
                        shift_var.fix(nurse_uid, True)



            
            objective = model.sum(
                module.build(self.instance, model, self.shift_vars)  # type: ignore
                for module in self.modules
            )

            _set_nurses_to_shifts(nurses_at_shifts_forced=meta_params.get("nurses_at_shifts_forced"))
            
            model.minimize(objective)
            
            model.close()
            
            optimizer.param.time_limit = max_time_in_seconds
            optimizer.param.verbosity = int(log_search_progress)
            
                

            optimizer.solve()

            if optimizer.solution.status in (hexaly.optimizer.HxSolutionStatus.INFEASIBLE, hexaly.optimizer.HxSolutionStatus.INCONSISTENT):
                return NurseRosteringSolution(
                    nurses_at_shifts={},
                    objective_value=-1,
                    return_status=generalize_return_status(optimizer.solution.status),
                    lower_bound=-1
                )
                
            nurses_at_shifts = {}
            for shift_var in self.shift_vars:
                for n_idx, nurse in enumerate(shift_var.nurses):
                    if n_idx in shift_var.nurses_assigned.value:
                        nurses_at_shifts.setdefault(shift_var.shift.uid, []).append(nurse.uid)

            return NurseRosteringSolution(
                nurses_at_shifts=nurses_at_shifts,
                objective_value=objective.value,
                return_status=generalize_return_status(optimizer.solution.status),
                lower_bound=optimizer.solution.get_objective_bound(0)
            )