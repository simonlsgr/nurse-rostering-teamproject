
from nurse_rostering.benchmarks.calculate_objective import calculate_objective
from nurse_rostering.utils.data_utils import group_shifts_by_date
from nurse_rostering.solvers.hexaly.model.solver import NurseRosteringModel as NurseRosteringModelHXLY
from nurse_rostering.solvers.cp_sat.model.solver import NurseRosteringModel as NurseRosteringModelCPSAT
from nurse_rostering.solvers.gurobi.model.solver import NurseRosteringModel as NurseRosteringModelGRB
from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution, Nurse, Shift
import pandas as pd
import datetime
import os

import json


def get_nurses_as_dict(nurses: list[Nurse]) -> dict[int, Nurse]:
    ret_dict = {}
    for nurse in nurses:
        ret_dict[nurse.uid] = nurse
    return ret_dict

def get_shifts_as_dict(shifts: list[Shift]) -> dict[int, Shift]:
    ret_dict = {}
    for shift in shifts:
        ret_dict[shift.uid] = shift
    return ret_dict
        

def display_solution(solution: NurseRosteringSolution, instance: NurseRosteringInstance):
    ret_str = ""
    ret_str += f"Solution status: {solution.return_status.capitalize()}\n"
    ret_str += f"Objective value: {solution.objective_value}\n"
    
    nurse_dict = get_nurses_as_dict(instance.nurses)
    shift_dict = get_shifts_as_dict(instance.shifts)
    
    for shift in instance.shifts:
        ret_str += f"{shift.name} Demand: {shift.demand} Length: {shift.length} | "
        for nuid in solution.nurses_at_shifts.get(shift.uid, []):
            ret_str += f"{nurse_dict[nuid].name}, "
        ret_str += "\n"
    return ret_str



def create_roster_viewer_input(solution: NurseRosteringSolution, instance: NurseRosteringInstance):
    ret_str = ""
    shifts_by_date = group_shifts_by_date(instance)
    shifts_as_dict = get_shifts_as_dict(instance.shifts)
    for nurse in instance.nurses:
        for date, shiftuids_at_date in shifts_by_date.items():
            processed_date = False
            
            for shiftuid_at_date in shiftuids_at_date:
                shift = shifts_as_dict[shiftuid_at_date]
                appendix = "	"
                if nurse.uid in solution.nurses_at_shifts.get(shift.uid, []):
                    ret_str += f"{shift.type}{appendix}"
                    processed_date = True
            
            if not processed_date:
                ret_str += "	"
        ret_str += "\n"
    
    return ret_str


if __name__ == "__main__":
    with open("backend/app/nurse_rostering/examples/data_processed/Instance2.json", "r") as f:
        instance_data = f.read()
    # data = json.loads(instance_data)
    instance = NurseRosteringInstance.model_validate_json(instance_data)

    nurse_rostering_model_cpsat = NurseRosteringModelGRB(instance)
    
    # for nv in nurse_rostering_model_cpsat.nurse_vars:
    #     if nv.nurse.name == "E":
    #         for shift in nv.shifts:
    #             if shift.name == "0_D":
    #                 nv.fix(shift.uid, False)
    #     for shift in nv.shifts:
    #         if shift.name == "1_D" and nv.nurse.name != "G":
    #             nv.fix(shift.uid, True)
        
    
    solution = nurse_rostering_model_cpsat.solve(max_time_in_seconds=480)
    print(display_solution(solution, instance))
    print(calculate_objective(solution, instance))
    with open("backend/app/nurse_rostering/benchmarks/roster_viewer_format.txt", "w") as f:
        eike = create_roster_viewer_input(solution, instance)
        f.write(eike)
        
        