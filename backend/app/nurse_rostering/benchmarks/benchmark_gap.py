
from nurse_rostering.solvers.cp_sat.model.solver import NurseRosteringModel as CPSolver
from nurse_rostering.solvers.gurobi.model.solver import NurseRosteringModel as GRBSolver
from nurse_rostering.solvers.hexaly.model.solver import NurseRosteringModel as HXLYSolver
from nurse_rostering.solvers.hybrid.solver import NurseRosteringModel as HybridSolver
from nurse_rostering.data_schema import NurseRosteringInstance, SolverFormulation, NurseRosteringSolution, SolverReturnStatus
from nurse_rostering.heuristics.greedy import NurseRosteringGreedyHeuristic
from nurse_rostering.benchmarks._utils.callback_utils_cpsat import CPSatBoundCallback, CPSatSolutionCallback, combine_cpsat_output
from nurse_rostering.benchmarks._utils.callback_utils_hexaly import HXLYCallback
from nurse_rostering.benchmarks._utils.timer import Timer

from datetime import datetime
import gurobi_logtools as glt
import pandas as pd
import os

def run_cpsat(formulation: SolverFormulation, instance: NurseRosteringInstance, time_limit: int, hints = None):
    
    model = CPSolver(instance,formulation=formulation,hints=hints)
    timer = Timer()

    solution_callback = CPSatSolutionCallback(timer, formulation)
    best_bound_callback = CPSatBoundCallback(model, timer, formulation)
    
    solution: NurseRosteringSolution = model.solve(max_time_in_seconds=time_limit, log_search_progress=False, meta_param_callback=solution_callback, meta_param_best_bound_callback=best_bound_callback)
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


def run_gurobi(formulation: SolverFormulation, instance: NurseRosteringInstance, time_limit: int, hints = None):
    
    
    model = GRBSolver(instance, hints=hints)
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

def run_hybrid(instance: NurseRosteringInstance, time_limit: int, solver_ratio: float):
    
    cb = HXLYCallback(SolverFormulation.TABLE)
    model = HybridSolver(instance)
    
    solution = model.solve(
        log_search_progress=True,
        max_time_in_seconds=time_limit,
        solver_ratio=solver_ratio,
        hexaly_meta_param_callback=cb,
        gurobi_LogFile="gurobi-temp.log",
    )
    
    
    df_hexaly = pd.DataFrame(cb.data, columns=["solver", "time", "objective", "bound"])
    
    hexaly_offset = df_hexaly["time"].iloc[-1]
    
    results = glt.parse(["gurobi-temp.log"])

    progress = results.progress()
    
    df_gurobi = progress[["Time", "Incumbent", "BestBd"]].copy()
    df_gurobi.columns = ["time", "objective", "bound"]
    df_gurobi["solver"] = "gurobi-ip"

    df_gurobi = df_gurobi[["solver", "time", "objective", "bound"]]

    df_gurobi["time"] += hexaly_offset
    df_hexaly["solver"] = f"hybrid-{solver_ratio}"
    df_gurobi["solver"] = f"hybrid-{solver_ratio}"
    
    df_combined = pd.concat([df_hexaly, df_gurobi], ignore_index=True)
    df_combined = df_combined.sort_values("time").reset_index(drop=True)
    
    os.remove("gurobi-temp.log")
    
    return df_combined
    


def main(instance_path, time_limit, instance_nb):
    
    with open(instance_path, "r") as f:
        data = f.read()
    
    instance = NurseRosteringInstance.model_validate_json(data)
    
    df_cpsat_automaton  = run_cpsat(SolverFormulation.AUTOMATON, instance, time_limit)
    df_cpsat_ip         = run_cpsat(SolverFormulation.IP, instance, time_limit)
    df_gurobi_ip        = run_gurobi(SolverFormulation.IP, instance, time_limit)
    df_hexaly_ip        = run_hexaly(SolverFormulation.IP, instance, time_limit)
    df_hexaly_set       = run_hexaly(SolverFormulation.TABLE, instance, time_limit)
    df_hybrid           = run_hybrid(instance, time_limit, solver_ratio=.3)
    
    df = pd.concat([df_hybrid, ], ignore_index=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filename = f"./output/gap_instance_{instance_nb}_{timestamp}.csv"
    
    df.to_csv(filename, index=False)
    
    
    
    

if __name__ == "__main__":
    instance_nb = 15
    time_limit = 60
    main(f"../examples/data_processed/Instance{instance_nb}.json", time_limit, instance_nb)
    
    