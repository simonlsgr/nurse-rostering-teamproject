from nurse_rostering.solvers.hexaly.model.solver import NurseRosteringModel as NurseRosteringModelHXLY
from nurse_rostering.solvers.cp_sat.model.solver import NurseRosteringModel as NurseRosteringModelCPSAT
from nurse_rostering.solvers.gurobi.model.solver import NurseRosteringModel as NurseRosteringModelGRB
from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution
from nurse_rostering.benchmarks.display_solution import display_solution
from nurse_rostering.benchmarks.calculate_objective import calculate_objective
import pandas as pd
import datetime
import os


import json
import argparse

SOLVERS = {
    "c": NurseRosteringModelCPSAT,
    "h": NurseRosteringModelHXLY,
    "g": NurseRosteringModelGRB,
}
def parse_args():
    parser = argparse.ArgumentParser(description="Run nurse rostering benchmarks with different solvers.")
    parser.add_argument(
        "solver",
        type=str,
        choices=SOLVERS.keys(),
        help="The solver to use (e.g., cpsat, hexaly, gurobi).",
    )
    parser.add_argument(
        "instance",
        type=str,
        help="Path to the input JSON file containing the nurse rostering instance.",
    )
    parser.add_argument(
        "--time_limit",
        type=int,
        default=60,
        help="Time limit for the solver in seconds (default: 60).",
    )
    return parser.parse_args()




# with open(f"backend/app/nurse_rostering/examples/data_processed/Instance{args.instance}.json", "r") as f:
#     instance_data = f.read()
# # data = json.loads(instance_data)
# instance = NurseRosteringInstance.model_validate_json(instance_data)

# nurse_rostering_model = SOLVERS[args.solver](instance)
# solution = nurse_rostering_model.solve(max_time_in_seconds=args.time_limit)



# nurse_rostering_model = NurseRosteringModel(instance)
# solution = nurse_rostering_model.solve()

# print(instance.model_dump_json())

# print(solution.model_dump_json())
# print(len(solution.nurses_at_shifts))
# for shift in solution.nurses_at_shifts:
#     for shift_data in instance.shifts:
#         if shift_data.uid == shift:
#             print(f"Shift {shift_data.name} has nurses:")
#     for nurse_uid in solution.nurses_at_shifts[shift]:
#         for nurse_data in instance.nurses:
#             if nurse_data.uid == nurse_uid:
#                 print(f" - Nurse {nurse_data.name}")
#     print("")
    
    
def run_instance_from_file(solver, file_path: str, time_limit: int = 60) -> NurseRosteringSolution:
    with open(file_path, "r") as f:
        instance_data = f.read()
    instance = NurseRosteringInstance.model_validate_json(instance_data)
    
    solver_instance = solver(instance)
    solution = solver_instance.solve(max_time_in_seconds=time_limit)
    
    return solution, instance, time_limit

def run_all_instances(solver, time_limit: int = 60):
    solver_name = str(solver(NurseRosteringInstance(shifts=[], nurses=[])))
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out_path = f"backend/app/nurse_rostering/benchmarks/benchmark_results_{date}.csv"
    
    for i in range(1, 25):
        file_path = f"backend/app/nurse_rostering/examples/data_processed/Instance{i}.json"
        solution, instance, time_limit = run_instance_from_file(solver, file_path, time_limit)
        
        row = pd.DataFrame([{
            "solver": solver_name,
            "instance": f"Instance{i}",
            "objective": solution.objective_value,
            "lower_bound": solution.lower_bound,
            "return_status": solution.return_status,
            "time_limit": time_limit
        }])
        
        row.to_csv(
                   out_path,
                   mode="a",
                   header=not os.path.exists(out_path),
                   index=False
                   )

if __name__ == "__main__":
    args = parse_args()
    run_instance_from_file(SOLVERS[args.solver], f"backend/app/nurse_rostering/examples/data_processed/Instance{args.instance}.json")
    # run_all_instances(SOLVERS[args.solver], time_limit=60)
    # sol, inst, tl = run_instance_from_file(SOLVERS[args.solver], "backend/app/nurse_rostering/examples/data_processed/Instance8.json", time_limit=5)
    # print(f"Objective: {sol.objective_value}, lower bound: {sol.lower_bound} with time limit {tl} seconds.")
    
