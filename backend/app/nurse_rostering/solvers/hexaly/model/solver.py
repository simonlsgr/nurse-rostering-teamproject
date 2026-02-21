import hexaly.optimizer
from nurse_rostering.solvers.hexaly.utils.generalize_return_status import generalize_return_status
from nurse_rostering.solvers.hexaly.model.nurse_vars import ShiftDecisionVars
from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution
from nurse_rostering.solvers.hexaly.model.modules import (
    ShiftAssignmentModule,
    OneShiftPerDayModule,
    ShiftRotationModule,
    MaximumShiftTypesModule,
    LimitWorkTimeModule,
    MaximumConsecutiveShiftsModule,
    MinimumConsecutiveShiftsModule,
    MinimumConsecutiveDaysOffModule,
    MaximumNumberOfWeekendsModule,
    DaysOffModule,
    CoverRequirementsModule,
    PreferStaffModule,
    PreferredShiftsModule,
)

class NurseRosteringModel:
    """
    A compact and extensible solver for the nurse rostering problem using Hexaly.
    """
    
    def __init__(
        self, instance: NurseRosteringInstance, model = None
    ):
        self.instance = instance
        
        

        self.modules: list[ShiftAssignmentModule] = [
            OneShiftPerDayModule(),
            ShiftRotationModule(),
            MaximumShiftTypesModule(),
            LimitWorkTimeModule(),
            MaximumConsecutiveShiftsModule(),
            MinimumConsecutiveShiftsModule(),
            MinimumConsecutiveDaysOffModule(),
            MaximumNumberOfWeekendsModule(),
            DaysOffModule(),
            CoverRequirementsModule(),
            PreferStaffModule(),
            PreferredShiftsModule(),
        ]

    def __str__(self) -> str:
        return "Hexaly Nurse Rostering Model" 
        
    def solve(
        self,
        log_search_progress: bool = True,
        max_time_in_seconds: int = 60,
        **solver_params,
    ) -> NurseRosteringSolution:
        
        with hexaly.optimizer.HexalyOptimizer() as optimizer:
            
            
            model = optimizer.model
            
            self.shift_vars = [
                ShiftDecisionVars(shift, self.instance.nurses, model)
                for shift in self.instance.shifts
            ]
            
            objective = model.sum(
                module.build(self.instance, model, self.shift_vars)  # type: ignore
                for module in self.modules
            )
            
            model.minimize(objective)
            
            model.close()
            
            optimizer.param.time_limit = max_time_in_seconds
            optimizer.param.verbosity = int(log_search_progress)
            
            for key, value in solver_params.items():
                setattr(optimizer.param, key, value)

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