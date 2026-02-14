
from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution, Nurse, Shift

def calculate_objective(solution: NurseRosteringSolution, instance: NurseRosteringInstance):
    
    nb_nurses_at_shift = {}
    for shift in instance.shifts:
        nb_nurses_at_shift[shift.uid] = len(solution.nurses_at_shifts.get(shift.uid, []))
    
    for shift in instance.shifts:
        print(shift.name)
        demand_mismatch = shift.demand - nb_nurses_at_shift[shift.uid]
        pen = 0
        if demand_mismatch >= 0:
            pen += shift.weight_below_demand * demand_mismatch
        else:
            pen += shift.weight_above_demand * abs(demand_mismatch)
        print(f"     Demand: {nb_nurses_at_shift[shift.uid]}/{shift.demand}, Penalty: {abs(pen)}")
    
    
    demand_penalty = 0
    for shift in instance.shifts:
        demand_mismatch = shift.demand - nb_nurses_at_shift[shift.uid]
        if demand_mismatch >= 0:
            demand_penalty += shift.weight_below_demand * demand_mismatch
        else:
            demand_penalty += shift.weight_above_demand * abs(demand_mismatch)
    
    print()
    print()
    print("nurses:")
    total_nurse_penalty = 0
    for nurse in instance.nurses:
        nurse_penalty = 0
        nurse_worked_hours = 0
        for shift in instance.shifts:
            if shift.uid in nurse.preferred_shifts and nurse.uid not in solution.nurses_at_shifts.get(shift.uid, []):
                nurse_penalty += nurse.preferred_shift_weight[shift.uid]
            if shift.uid in nurse.preferred_off_shifts and nurse.uid in solution.nurses_at_shifts.get(shift.uid, []):
                nurse_penalty += nurse.preferred_off_shift_weight[shift.uid]
                
        print(nurse.name)
        print(f"     Penalty: {nurse_penalty}")
        
        total_nurse_penalty += nurse_penalty
                
            
    
    
    print("Demand penalty: ", demand_penalty)
    print("Nurse penalty: ", total_nurse_penalty)
    
     