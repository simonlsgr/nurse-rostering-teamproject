from nurse_rostering.data_schema import SolverFormulation
from ortools.sat.python import cp_model
import pandas as pd

class CPSatSolutionCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self, timer, formulation: SolverFormulation):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.timer = timer
        self.formulation = formulation
        self.data = []

    def on_solution_callback(self):
        
        obj = self.ObjectiveValue()
        self.data.append(["objective", "cpsat-"+self.formulation.lower(), obj, self.timer.time()])


class CPSatBoundCallback:
    def __init__(self, solver, timer, formulation: SolverFormulation) -> None:
        self.timer = timer
        self.solver = solver
        self.formulation = formulation
        self.data = []

    def __call__(self, bound):
        self.data.append(["bound", "cpsat-"+self.formulation.lower(), bound, self.timer.time()])
        

def combine_cpsat_output(df) -> pd.DataFrame:
        
    rows = []
    for solver, group in df.groupby("solver"):
        bound_latest = None
        obj_latest = None
        
        times = sorted(group['time'].unique())
        
        for t in times:
            bounds_at_t = group[(group['type'] == 'bound') & (group['time'] <= t)]
            if not bounds_at_t.empty:
                bound_latest = bounds_at_t.iloc[-1]['value']
            
            objs_at_t = group[(group['type'] == 'objective') & (group['time'] <= t)]
            if not objs_at_t.empty:
                obj_latest = objs_at_t.iloc[-1]['value']
            
            rows.append({
                "solver": solver,
                "time": t,
                "objective": obj_latest,
                "bound": bound_latest
            })


    return pd.DataFrame(rows)   