from typing import Any

import hexaly.optimizer
from nurse_rostering.solvers.hexaly.utils.generalize_return_status import generalize_return_status
from nurse_rostering.solvers.hexaly.model.nurse_vars import ShiftDecisionVars, NurseDecisionVarsIP, \
    NurseDecisionVarsTable
from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution, SolverFormulation
from nurse_rostering.solvers.hexaly.model.modules_set import (
    ShiftAssignmentModuleSet,
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
from nurse_rostering.solvers.hexaly.model.modules_ip import (
    ShiftAssignmentModuleIP,
    OneShiftPerDayModuleIP,
    ShiftRotationModuleIP,
    MaximumShiftTypesModuleIP,
    LimitWorkTimeModuleIP,
    MaximumConsecutiveShiftsModuleIP,
    MinimumConsecutiveShiftsModuleIP,
    MinimumConsecutiveDaysOffModuleIP,
    MaximumNumberOfWeekendsModuleIP,
    DaysOffModuleIP,
    CoverRequirementsModuleIP,
    PreferStaffModuleIP,
    MaximizePreferencesIP,
    OffPreferencesIP,
)
from nurse_rostering.solvers.hexaly.model.modules_table import (
    OneShiftPerDayModuleTable,
    ShiftRotationModuleTable, MaximizePreferencesTable, LimitWorkTimeModuleTable,
    MaximumConsecutiveShiftsModuleTable, MinimumConsecutiveShiftsModuleTable, MinimumConsecutiveDaysOffModuleTable,
    MaximumNumberOfWeekendsModuleTable, CoverRequirementsModuleTable, DaysOffModuleTable,
    MaximumShiftTypesModuleTable

)
from nurse_rostering.utils.data_utils import group_shifts_by_date


class NurseRosteringModel:
    """
    A compact and extensible solver for the nurse rostering problem using Hexaly.
    """
    
    def __init__(
        self, instance: NurseRosteringInstance, model = None, formulation: SolverFormulation = SolverFormulation.TABLE
    ):
        self.instance = instance
        self.formulation = formulation
        
        
        if self.formulation == SolverFormulation.SET:
            self.modules: list[ShiftAssignmentModuleSet] = [
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
        elif self.formulation == SolverFormulation.IP:
            self.modules: list[ShiftAssignmentModuleIP] = [
                MaximumShiftTypesModuleIP(),
                OneShiftPerDayModuleIP(),
                ShiftRotationModuleIP(),
                MaximizePreferencesIP(),
                PreferStaffModuleIP(),
                LimitWorkTimeModuleIP(),
                MaximumConsecutiveShiftsModuleIP(),
                MinimumConsecutiveShiftsModuleIP(),
                MinimumConsecutiveDaysOffModuleIP(),
                MaximumNumberOfWeekendsModuleIP(),
                CoverRequirementsModuleIP(),
                OffPreferencesIP(),
                DaysOffModuleIP(),
            ]

        elif self.formulation == SolverFormulation.TABLE:
            self.modules: list[ShiftRotationModuleTable] = [
                OneShiftPerDayModuleTable(),
                ShiftRotationModuleTable(),
                MaximumShiftTypesModuleTable(),
                MaximizePreferencesTable(),
                LimitWorkTimeModuleTable(),
                MaximumConsecutiveShiftsModuleTable(),
                MinimumConsecutiveShiftsModuleTable(),
                MinimumConsecutiveDaysOffModuleTable(),
                MaximumNumberOfWeekendsModuleTable(),
                CoverRequirementsModuleTable(),
                DaysOffModuleTable(),
            ]




        
    def solve(
        self,
        log_search_progress: bool = True,
        max_time_in_seconds: int = 60,
        **solver_params,
    ) -> NurseRosteringSolution:

        
        with hexaly.optimizer.HexalyOptimizer() as optimizer:
            meta_params: dict[str, Any] = {}
            for key, value in solver_params.items():
                if key.startswith("meta_param_"):
                    meta_key = key[len("meta_param_"):]
                    meta_params[meta_key] = value
                    continue
                else:
                    setattr(optimizer.param, key, value)
            
            callback = meta_params.get("callback")
            if callback is not None:
                optimizer.add_callback(callback.cbType, callback.call)
            
            model = optimizer.model
            objective = 0
            dates = {}
            nurse_vars = []
            nurse_var = None
            if self.formulation == SolverFormulation.SET:
                self.shift_vars = [
                    ShiftDecisionVars(shift, self.instance.nurses, model)
                    for shift in self.instance.shifts
                ]
                
                objective = model.sum(
                    module.build(self.instance, model, self.shift_vars)  # type: ignore
                    for module in self.modules
                )

                def _set_nurses_to_shifts(nurses_at_shifts_forced) -> None:
                    if not nurses_at_shifts_forced:
                        return

                    shift_var_by_uid = {shift_var.shift.uid: shift_var for shift_var in self.shift_vars}
                    for shift_uid, nurse_uids in nurses_at_shifts_forced.items():
                        shift_var = shift_var_by_uid[int(shift_uid)]
                        for nurse_uid in nurse_uids:
                            shift_var.fix(nurse_uid, True)

                _set_nurses_to_shifts(nurses_at_shifts_forced=meta_params.get("nurses_at_shifts_forced"))
            elif self.formulation == SolverFormulation.IP:
                nurse_vars = [
                    NurseDecisionVarsIP(nurse, self.instance.shifts, model) for nurse in self.instance.nurses
                ]
                
                objective = model.sum(
                    module.build(self.instance, model, nurse_vars)  # type: ignore
                    for module in self.modules
                )

            elif self.formulation == SolverFormulation.TABLE:
                dates = group_shifts_by_date(self.instance)
                nurse_var = NurseDecisionVarsTable(self.instance, model, dates)
                objective = model.sum(
                    module.build(self.instance, model, nurse_var, dates)  # type: ignore
                    for module in self.modules
                )

                
                
                
            
            model.minimize(objective)
            
            model.close()
            
            optimizer.param.time_limit = max_time_in_seconds
            optimizer.param.verbosity = 2 if log_search_progress else 0
            
                

            optimizer.solve()

            if optimizer.solution.status in (hexaly.optimizer.HxSolutionStatus.INFEASIBLE, hexaly.optimizer.HxSolutionStatus.INCONSISTENT):
                return NurseRosteringSolution(
                    nurses_at_shifts={},
                    objective_value=-1,
                    return_status=generalize_return_status(optimizer.solution.status),
                    lower_bound=-1
                )
                
            nurses_at_shifts: dict[int, list[int]] = {}
            
            if self.formulation == SolverFormulation.SET:    
                for shift_var in self.shift_vars:
                    for n_idx, nurse in enumerate(shift_var.nurses):
                        if n_idx in shift_var.nurses_assigned.value:
                            nurses_at_shifts.setdefault(shift_var.shift.uid, []).append(nurse.uid)
            elif self.formulation == SolverFormulation.IP:
                nurses_at_shifts: dict[int, list[int]] = {}
                for nurse_model in nurse_vars:
                    for shift_uid in nurse_model.extract():
                        nurses_at_shifts.setdefault(shift_uid, []).append(nurse_model.nurse.uid)
            elif self.formulation == SolverFormulation.TABLE:
                nurses_at_shifts: dict[int, list[int]] = nurse_var.extract()

            return NurseRosteringSolution(
                nurses_at_shifts=nurses_at_shifts,
                objective_value=objective.value,
                return_status=generalize_return_status(optimizer.solution.status),
                lower_bound=optimizer.solution.get_objective_bound(0)
            )
            
if __name__ == "__main__":
    instance_nb = 2
    time_limit = 60
    instance_path= f"../../../examples/data_processed/Instance{instance_nb}.json"
    
    with open(instance_path, "r") as f:
        data = f.read()
    
    instance = NurseRosteringInstance.model_validate_json(data)
        
    solver = NurseRosteringModel(instance,formulation=SolverFormulation.TABLE)
    solver.solve()
    