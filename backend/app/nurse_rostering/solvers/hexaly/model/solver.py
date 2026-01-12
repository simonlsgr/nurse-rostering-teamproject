import hexaly.optimizer
from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVars
from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution
from nurse_rostering.solvers.hexaly.model.modules import (
    ShiftAssignmentModule,
    NoBlockedShiftsModule,
    DemandSatisfactionModule,
    MinTimeBetweenShifts,
    MaximizePreferences,
    PreferStaffModule,
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
            NoBlockedShiftsModule(),
            DemandSatisfactionModule(),
            MinTimeBetweenShifts(),
            MaximizePreferences(),
            PreferStaffModule(),
        ]

        
        
    def solve(
        self,
        log_search_progress: bool = True,
        max_time_in_seconds: int = 60,
        **solver_params,
    ) -> NurseRosteringSolution:
        
        with hexaly.optimizer.HexalyOptimizer() as optimizer:
            
            
            model = optimizer.model
            
            self.nurse_vars = [
                NurseDecisionVars(nurse, self.instance.shifts, model)
                for nurse in self.instance.nurses
            ]
            
            objective = model.sum(
                module.build(self.instance, model, self.nurse_vars)  # type: ignore
                for module in self.modules
            )
            
            model.minimize(objective)
            
            model.close()
            
            optimizer.param.time_limit = max_time_in_seconds
            optimizer.param.verbosity = int(log_search_progress)
            
            for key, value in solver_params.items():
                setattr(optimizer.param, key, value)

            optimizer.solve()


            nurses_at_shifts = {}
            for nurse_model in self.nurse_vars:
                for shift_uid in nurse_model.extract():
                    nurses_at_shifts.setdefault(shift_uid, []).append(nurse_model.nurse.uid)

            return NurseRosteringSolution(
                nurses_at_shifts=nurses_at_shifts,
                objective_value=objective.value,
            )