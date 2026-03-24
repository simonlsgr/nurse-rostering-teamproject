import time

from nurse_rostering.heuristics.greedy import NurseRosteringGreedyHeuristic
from nurse_rostering.solvers.cp_sat.model.solver import NurseRosteringModel as CPSolver
from nurse_rostering.solvers.gurobi.model.solver import NurseRosteringModel as GRBSolver
from nurse_rostering.solvers.hexaly.model.solver import NurseRosteringModel as HXLYSolver
from nurse_rostering.solvers.hybrid.solver import  NurseRosteringModel as HYBRDSolver
from nurse_rostering.data_schema import NurseRosteringInstance, SolverFormulation, NurseRosteringSolution, \
    SolverReturnStatus
from nurse_rostering.benchmarks._utils.callback_utils_cpsat import CPSatBoundCallback, CPSatSolutionCallback, \
    combine_cpsat_output
from nurse_rostering.benchmarks._utils.callback_utils_hexaly import HXLYCallback
from nurse_rostering.benchmarks._utils.timer import Timer

from datetime import datetime
import gurobi_logtools as glt
import pandas as pd
import os


def run_cpsat(formulation: SolverFormulation, instance: NurseRosteringInstance, time_limit: int):
    model = CPSolver(instance, formulation=formulation)
    timer = Timer()

    solution_callback = CPSatSolutionCallback(timer, formulation)
    best_bound_callback = CPSatBoundCallback(model, timer, formulation)

    solution: NurseRosteringSolution = model.solve(max_time_in_seconds=time_limit, log_search_progress=True,
                                                   meta_param_callback=solution_callback,
                                                   meta_param_best_bound_callback=best_bound_callback)
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


def run_cpsat_heuristics(formulation: SolverFormulation, instance: NurseRosteringInstance, time_limit: int):
    start = time.perf_counter()
    heuristic_sol = NurseRosteringGreedyHeuristic(instance).solve()
    elapsed = time.perf_counter() - start
    time_limit -= elapsed
    print(elapsed)
    model = CPSolver(instance, formulation=formulation, hints=heuristic_sol.nurses_at_shifts)
    timer = Timer()

    solution_callback = CPSatSolutionCallback(timer, formulation, elapsed,"heuristics")
    best_bound_callback = CPSatBoundCallback(model, timer, formulation, elapsed,"heuristics")

    solution: NurseRosteringSolution = model.solve(max_time_in_seconds=time_limit, log_search_progress=True,
                                                   meta_param_callback=solution_callback,
                                                   meta_param_best_bound_callback=best_bound_callback)
    opt = solution.return_status
    opt_time = 0
    if opt == SolverReturnStatus.OPTIMAL:
        opt_time = timer.time()
    data = best_bound_callback.data + solution_callback.data
    df = pd.DataFrame(data, columns=["type", "solver", "value", "time"])

    df = combine_cpsat_output(df)
    if opt == SolverReturnStatus.OPTIMAL:
        df.loc[len(df)] = [
            "cpsat-" + formulation.lower() + "-heuristics",
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


def run_gurobi_heuristics(formulation: SolverFormulation, instance: NurseRosteringInstance, time_limit: int):
    start = time.perf_counter()
    heuristic_sol = NurseRosteringGreedyHeuristic(instance).solve()
    elapsed = time.perf_counter() - start
    time_limit -= elapsed
    model = GRBSolver(instance, hints=heuristic_sol.nurses_at_shifts)
    solution = model.solve(max_time_in_seconds=time_limit, log_search_progress=True, LogFile="gurobi-temp.log")

    results = glt.parse(["gurobi-temp.log"])

    progress = results.progress()

    df_filtered = progress[["Time", "Incumbent", "BestBd"]].copy()
    df_filtered.columns = ["time", "objective", "bound"]
    df_filtered["solver"] = "gurobi-ip-heuristics"

    df_filtered = df_filtered[["solver", "time", "objective", "bound"]]

    os.remove("gurobi-temp.log")

    return df_filtered


def run_hybrid(instance: NurseRosteringInstance, time_limit: int, solver_ratio: float = 0.3):
    cb = HXLYCallback(SolverFormulation.TABLE)
    log_file = "gurobi-temp.log"

    model = HYBRDSolver(instance)

    solution = model.solve(
        max_time_in_seconds=time_limit,
        log_search_progress=True,
        solver_ratio=solver_ratio,
        hexaly_meta_param_callback=cb,
        gurobi_LogFile=log_file,
    )

    dfs = []

    df_hexaly = pd.DataFrame(cb.data, columns=["solver", "time", "objective", "bound"])
    if not df_hexaly.empty:
        df_hexaly["solver"] = "hybrid"
        dfs.append(df_hexaly[["solver", "time", "objective", "bound"]])

    if os.path.exists(log_file):
        results = glt.parse([log_file])
        progress = results.progress()

        if not progress.empty:
            df_gurobi = progress[["Time", "Incumbent", "BestBd"]].copy()
            df_gurobi.columns = ["time", "objective", "bound"]

            hexaly_time = int(time_limit * solver_ratio)
            df_gurobi["time"] = df_gurobi["time"] + hexaly_time
            df_gurobi["solver"] = "hybrid"

            dfs.append(df_gurobi[["solver", "time", "objective", "bound"]])

        os.remove(log_file)

    if dfs:
        return pd.concat(dfs, ignore_index=True)

    return pd.DataFrame(columns=["solver", "time", "objective", "bound"])


def run_hexaly(formulation: SolverFormulation, instance: NurseRosteringInstance, time_limit: int):
    cb = HXLYCallback(formulation)
    model = HXLYSolver(instance, formulation=formulation)
    timer = Timer()
    solution = model.solve(max_time_in_seconds=time_limit, meta_param_callback=cb)

    df = pd.DataFrame(cb.data, columns=["solver", "time", "objective", "bound"])
    return df


def main(instance_path, time_limit, instance_nb):
    with open(instance_path, "r") as f:
        data = f.read()

    instance = NurseRosteringInstance.model_validate_json(data)

    # df_cpsat_automaton = run_cpsat(SolverFormulation.AUTOMATON, instance, time_limit)
    # df_cpsat_ip = run_cpsat(SolverFormulation.IP, instance, time_limit)
    # df_gurobi_ip = run_gurobi(SolverFormulation.IP, instance, time_limit)
    # df_hexaly_ip = run_hexaly(SolverFormulation.IP, instance, time_limit)
    # df_hexaly_set = run_hexaly(SolverFormulation.SET, instance, time_limit)
    # df_hexaly_table = run_hexaly(SolverFormulation.TABLE, instance, time_limit)
    df_hybrid = run_hybrid(instance, time_limit)
    df_cpsat_heur = run_cpsat_heuristics(SolverFormulation.IP, instance, time_limit)
    df_gurobi_heur = run_gurobi_heuristics(SolverFormulation.IP, instance, time_limit)

    df = pd.concat([
        # df_gurobi_ip, df_hexaly_ip, df_hexaly_set, df_cpsat_ip, df_cpsat_automaton, df_hexaly_table
        df_hybrid, df_cpsat_heur, df_gurobi_heur
    ],
                   ignore_index=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"./output/gap_instance_{instance_nb}_{timestamp}_{time_limit}.csv"

    df.to_csv(filename, index=False)


def run(time_limit):
    for i in range(1, 21):
        main(f"../examples/data_processed/Instance{i}.json", time_limit, i)


if __name__ == "__main__":
    run(180)


