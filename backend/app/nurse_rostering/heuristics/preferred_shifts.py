




from typing import Any
from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution, Nurse, SolverReturnStatus
from nurse_rostering.utils.data_utils import group_shifts_by_date, get_shiftuid_dict, get_types_and_length_in_instance, get_shift_type_dict
from nurse_rostering.utils.calculate_objective import calculate_objective
from nurse_rostering.utils.validation import assert_solution_is_feasible
from datetime import datetime, timedelta, date




class NurseRosteringPreferenceBasedHeuristic:
    def __init__(
        self, instance: NurseRosteringInstance
    ):
        self.instance: NurseRosteringInstance = instance.model_copy()        
    
    
    def solve(self, **solver_params):
        
        meta_params: dict[str, Any] = {}
        for key, value in solver_params.items():
            if key.startswith("meta_param_"):
                meta_key = key[len("meta_param_"):]
                meta_params[meta_key] = value
                continue
            
        nurses_at_shifts = {}
        
        for nurse in self.instance.nurses:
            for preferred_shift in nurse.preferred_shifts:
                nurses_at_shifts.setdefault(preferred_shift, []).append(nurse.uid)
        
        objective_value = calculate_objective(nurses_at_shifts, self.instance)

        sol = NurseRosteringSolution(
            nurses_at_shifts=nurses_at_shifts,
            objective_value=objective_value,
            return_status=SolverReturnStatus.FEASIBLE,
            lower_bound=None,
        )
        
        try:
            assert_solution_is_feasible(self.instance, sol)
            return sol
        except:
            return NurseRosteringSolution(
            nurses_at_shifts=nurses_at_shifts,
            objective_value=objective_value,
            return_status=SolverReturnStatus.UNKNOWN,
            lower_bound=None,
        )
            
                
                
                    
                
                

if __name__ == "__main__":
    
    for i in range(1,25):
    
        with open(f"../examples/data_processed/Instance{i}.json", "r") as f:
            instance_data = f.read()
        instance = NurseRosteringInstance.model_validate_json(instance_data)

        h = NurseRosteringPreferenceBasedHeuristic(instance)
        sol = h.solve()

        print(i, sol.objective_value)