import hexaly.optimizer
from ...model.nurse_vars import NurseDecisionVars
from ...data_schema import NurseRosteringInstance, NurseRosteringSolution
from ...model.modules import (
    ShiftAssignmentModule,
    NoBlockedShiftsModule,
    DemandSatisfactionModule,
    MinTimeBetweenShifts,
    MaximizePreferences,
    PreferStaffModule,
)
from .hexaly_adapter import HexalyAdapter

class NurseRosteringModel:
    """
    A compact and extensible solver for the nurse rostering problem using Hexaly.
    """
    
    def __init__(
        self, instance: NurseRosteringInstance, model = None
    ):
        self.instance = instance
        
        self.nurse_vars = [
            NurseDecisionVars(nurse, instance.shifts, self.adapter)
            for nurse in instance.nurses
        ]

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
        max_time_in_seconds: float = 60.0,
        **solver_params,
    ) -> NurseRosteringSolution:
        
        with hexaly.optimizer.HexalyOptimizer() as optimizer:
            
            self.adapter = model or HexalyAdapter(optimizer.model)
            
            model = optimizer.model
            
            objective = self.adapter.sum(
                module.build(self.instance, self.adapter, self.nurse_vars)  # type: ignore
                for module in self.modules
            )
            self.adapter.set_objective(objective, "min")
            
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
            objective_value=round(objective.value),
        )