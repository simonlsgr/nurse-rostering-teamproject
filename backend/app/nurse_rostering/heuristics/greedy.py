




from typing import Any
from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution, Nurse, SolverReturnStatus
from nurse_rostering.utils.data_utils import group_shifts_by_date, get_shiftuid_dict, get_types_and_length_in_instance, get_shift_type_dict
from nurse_rostering.utils.calculate_objective import calculate_objective
from nurse_rostering.utils.validation import assert_solution_is_feasible
from datetime import datetime, timedelta, date




class NurseRosteringGreedyHeuristic:
    def __init__(
        self, instance: NurseRosteringInstance
    ):
        self.instance: NurseRosteringInstance = instance.model_copy()        
    
    def _weekend_day_feasible(self, nurse: Nurse, day: date, nurse_weekends_assigend, nurse_days_assigned):
        
        if day.weekday() == 5:
            if sum(nurse_weekends_assigend) >= nurse.maximum_weekends:
                return False
        
        if day.weekday() == 6:
            if sum(nurse_weekends_assigend) >= nurse.maximum_weekends and nurse_days_assigned[len(nurse_days_assigned)-1] == 0:
                return False
        
        return True
        
        
    def _get_feasible_shiftuids(self, shiftuids, nurse: Nurse, day, nurse_shift_types_assigned, nurse_days_assigned, nurse_weekends_assigend):
        
        work_time = 0
        for stype, nb_assgined in nurse_shift_types_assigned.items():
            work_time += nb_assgined * self.shift_types_and_length[stype]
                
        new_shiftuids = []
        for shiftuid in shiftuids:
            
            if day in nurse.days_off:
                return []
            
            if not self._weekend_day_feasible(nurse, day, nurse_weekends_assigend, nurse_days_assigned):
                return []
            
            
            if len(nurse_days_assigned) >= nurse.minimum_consecutive_days_off:
                if(not nurse_days_assigned[len(nurse_days_assigned)-1]):
                    if(any(nurse_days_assigned[len(nurse_days_assigned)-nurse.minimum_consecutive_days_off:len(nurse_days_assigned)])):
                        return []
            
            if len(nurse_days_assigned) >= nurse.maximum_consecutive_shifts:
                if(all(nurse_days_assigned[len(nurse_days_assigned)-nurse.maximum_consecutive_shifts:len(nurse_days_assigned)])):
                    return []
            
            
            stype = self.shiftuid_dict[shiftuid].type
            if (
                nurse_shift_types_assigned[stype] < nurse.maximum_number_of_shifts_per_type[stype] and
                work_time + self.shiftuid_dict[shiftuid].length <= nurse.maximum_work_time
            ):
                new_shiftuids.append(shiftuid)
                   
        
        
        return new_shiftuids
    
    def solve(self, **solver_params):
        
        meta_params: dict[str, Any] = {}
        for key, value in solver_params.items():
            if key.startswith("meta_param_"):
                meta_key = key[len("meta_param_"):]
                meta_params[meta_key] = value
                continue
        
        
        self.shift_types_and_length = get_types_and_length_in_instance(self.instance)
        self.start_date = self.instance.shifts[0].start_time.date()
        
        self.not_followed_by_shifts = get_shift_type_dict(self.instance)
        self.shifts_by_day = group_shifts_by_date(self.instance)
        self.shiftuid_dict = get_shiftuid_dict(self.instance)
        
        horizon = self.instance.planning_horizon_in_days
        
        self.nurses_at_shifts: dict[int, list[int]] = {}
        for nurse in self.instance.nurses:
            nurse_shift_types_assigned = {stype: 0 for stype in self.shift_types_and_length}
            nurse_weekends_assigend = [0]*(horizon//7)
            nurse_days_assigned = []
            nurse_shifts_assigned = []
            for day, shiftuids in self.shifts_by_day.items():
                feasible_shifts = self._get_feasible_shiftuids(shiftuids, nurse, day, nurse_shift_types_assigned, nurse_days_assigned, nurse_weekends_assigend)
                if len(feasible_shifts) == 0:
                    nurse_days_assigned.append(0)
                    nurse_shifts_assigned.append(0)
                    continue
                
                nurse_days_assigned.append(1)
                nurse_shifts_assigned.append(feasible_shifts[0])
                
                if day.weekday() >= 5:
                    nurse_weekends_assigend[(day-self.start_date).days//7] = 1
                nurse_shift_types_assigned[self.shiftuid_dict[feasible_shifts[0]].type] += 1
                
                self.nurses_at_shifts.setdefault(feasible_shifts[0], []).append(nurse.uid)
            
            i = 0              
            while i < horizon - nurse.minimum_consecutive_shifts:
                if nurse_days_assigned[i] == 1:
                    if (not all(nurse_days_assigned[i:i+nurse.minimum_consecutive_shifts])):
                        self.nurses_at_shifts[nurse_shifts_assigned[i]].remove(nurse.uid)
                        i += 1
                    else: 
                        while nurse_days_assigned[i] == 1 and i < horizon - nurse.minimum_consecutive_shifts:
                            i+=1
                else: 
                    while nurse_days_assigned[i] == 0 and i < horizon - nurse.minimum_consecutive_shifts:
                        i+=1

        objective_value = calculate_objective(self.nurses_at_shifts, self.instance)

        sol = NurseRosteringSolution(
            nurses_at_shifts=self.nurses_at_shifts,
            objective_value=objective_value,
            return_status=SolverReturnStatus.FEASIBLE,
            lower_bound=None,
        )
        
        try:
            assert_solution_is_feasible(self.instance, sol)
            return sol
        except:
            return NurseRosteringSolution(
            nurses_at_shifts=self.nurses_at_shifts,
            objective_value=0,
            return_status=SolverReturnStatus.UNKNOWN,
            lower_bound=None,
        )
            
                
                
                    
                
                

if __name__ == "__main__":
    
    with open("backend/app/nurse_rostering/examples/data_processed/Instance2.json", "r") as f:
        instance_data = f.read()
    instance = NurseRosteringInstance.model_validate_json(instance_data)
    
    h = NurseRosteringGreedyHeuristic(instance)
    
    h.solve()