
from nurse_rostering.data_schema import NurseRosteringInstance

def calculate_objective(nurses_at_shifts, instance: NurseRosteringInstance):
    
    nb_nurses_at_shift = {}
    for shift in instance.shifts:
        nb_nurses_at_shift[shift.uid] = len(nurses_at_shifts.get(shift.uid, []))
    
    for shift in instance.shifts:

        demand_mismatch = shift.demand - nb_nurses_at_shift[shift.uid]
        pen = 0
        if demand_mismatch >= 0:
            pen += shift.weight_below_demand * demand_mismatch
        else:
            pen += shift.weight_above_demand * abs(demand_mismatch)

    
    
    demand_penalty = 0
    for shift in instance.shifts:
        demand_mismatch = shift.demand - nb_nurses_at_shift[shift.uid]
        if demand_mismatch >= 0:
            demand_penalty += shift.weight_below_demand * demand_mismatch
        else:
            demand_penalty += shift.weight_above_demand * abs(demand_mismatch)

    total_nurse_penalty = 0
    for nurse in instance.nurses:
        nurse_penalty = 0
        nurse_worked_hours = 0
        for shift in instance.shifts:
            if shift.uid in nurse.preferred_shifts and nurse.uid not in nurses_at_shifts.get(shift.uid, []):
                nurse_penalty += nurse.preferred_shift_weight[shift.uid]
            if shift.uid in nurse.preferred_off_shifts and nurse.uid in nurses_at_shifts.get(shift.uid, []):
                nurse_penalty += nurse.preferred_off_shift_weight[shift.uid]
                
        
        total_nurse_penalty += nurse_penalty
                
            
    
    
    
    return demand_penalty + total_nurse_penalty
     