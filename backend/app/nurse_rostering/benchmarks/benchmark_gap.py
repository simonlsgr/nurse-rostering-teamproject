
from nurse_rostering.solvers.cp_sat.model.solver import NurseRosteringModel as CPSolver
from nurse_rostering.solvers.gurobi.model.solver import NurseRosteringModel as GRBSolver
from nurse_rostering.solvers.hexaly.model.solver import NurseRosteringModel as HXLYSolver
from nurse_rostering.data_schema import NurseRosteringInstance, SolverFormulation, NurseRosteringSolution, SolverReturnStatus
from nurse_rostering.benchmarks._utils.callback_utils_cpsat import CPSatBoundCallback, CPSatSolutionCallback, combine_cpsat_output
from nurse_rostering.benchmarks._utils.callback_utils_hexaly import HXLYCallback
from nurse_rostering.benchmarks._utils.timer import Timer

from datetime import datetime
import gurobi_logtools as glt
import pandas as pd
import os

def run_cpsat(formulation: SolverFormulation, instance: NurseRosteringInstance, time_limit: int):
    
    model = CPSolver(instance,formulation=formulation)
    timer = Timer()

    solution_callback = CPSatSolutionCallback(timer, formulation)
    best_bound_callback = CPSatBoundCallback(model, timer, formulation)
    
    solution: NurseRosteringSolution = model.solve(max_time_in_seconds=time_limit, log_search_progress=True, meta_param_callback=solution_callback, meta_param_best_bound_callback=best_bound_callback)
    opt = solution.return_status
    opt_time = 0
    if opt == SolverReturnStatus.OPTIMAL:
        opt_time = timer.time()
    data = best_bound_callback.data + solution_callback.data
    df = pd.DataFrame(data, columns=["type", "solver", "value", "time"])
    
    df = combine_cpsat_output(df)
    if opt == SolverReturnStatus.OPTIMAL:
        df.loc[len(df)] = [
        "cpsat-" + formulation.lower(),
        opt_time,
        solution.objective_value,
        solution.lower_bound
    ]
    
    return df


def run_gurobi(formulation: SolverFormulation, instance: NurseRosteringInstance, time_limit: int):
    
    
    model = GRBSolver(instance)
    solution = model.solve(max_time_in_seconds=time_limit, log_search_progress=True, LogFile="gurobi-temp.log")

    results = glt.parse(["gurobi-temp.log"])

    progress = results.progress()
    
    df_filtered = progress[["Time", "Incumbent", "BestBd"]].copy()
    df_filtered.columns = ["time", "objective", "bound"]
    df_filtered["solver"] = "gurobi-ip"

    df_filtered = df_filtered[["solver", "time", "objective", "bound"]]

    os.remove("gurobi-temp.log")

    return df_filtered

def run_hexaly(formulation: SolverFormulation, instance: NurseRosteringInstance, time_limit: int):
    cb = HXLYCallback(formulation)
    model = HXLYSolver(instance,formulation=formulation)
    timer = Timer()
    solution = model.solve(max_time_in_seconds=time_limit, meta_param_callback=cb)
    
    df = pd.DataFrame(cb.data, columns=["solver", "time", "objective", "bound"])
    return df

def main(instance_path, time_limit, instance_nb):
    
    with open(instance_path, "r") as f:
        data = f.read()
    
    instance = NurseRosteringInstance.model_validate_json(data)
    
    # df_cpsat_automaton  = run_cpsat(SolverFormulation.AUTOMATON, instance, time_limit)
    # df_cpsat_ip         = run_cpsat(SolverFormulation.IP, instance, time_limit)
    df_gurobi_ip        = run_gurobi(SolverFormulation.IP, instance, time_limit)
    df_hexaly_ip        = run_hexaly(SolverFormulation.IP, instance, time_limit)
    df_hexaly_set        = run_hexaly(SolverFormulation.SET, instance, time_limit)
    
    df = pd.concat([df_gurobi_ip, df_hexaly_ip, df_hexaly_set], ignore_index=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filename = f"./output/gap_instance_{instance_nb}_{timestamp}.csv"
    
    df.to_csv(filename, index=False)
    
    
    
    

if __name__ == "__main__":
    instance_nb = 13
    time_limit = 60
    main(f"../examples/data_processed/Instance{instance_nb}.json", time_limit, instance_nb)
    
    