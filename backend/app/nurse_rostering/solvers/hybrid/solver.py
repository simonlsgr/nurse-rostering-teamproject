from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution, SolverFormulation, SolverReturnStatus
from nurse_rostering.solvers.hexaly.model.solver import NurseRosteringModel as HXLYSolver
from nurse_rostering.solvers.gurobi.model.solver import NurseRosteringModel as GRBSolver



class NurseRosteringModel:
    """
    A compact and extensible solver for the nurse rostering problem using Gurobi and Hexaly.
    """

    def __init__(
        self, instance: NurseRosteringInstance
    ):
        self.instance = instance
    
                

    def solve(
        self,
        log_search_progress: bool = False,
        max_time_in_seconds: float = 60.0,
        solver_ratio: float = .3,
        **solver_params,
    ) -> NurseRosteringSolution:
        
        
        hexaly_params = {}
        gurobi_params = {}
        for key, value in solver_params.items():
                if key.startswith("hexaly_"):
                    meta_key = key[len("hexaly_"):]
                    hexaly_params[meta_key] = value
                elif key.startswith("gurobi_"):
                    meta_key = key[len("gurobi_"):]
                    gurobi_params[meta_key] = value
                    
        if solver_ratio > 1 or solver_ratio < 0:
            raise ValueError("solver_ratio must be in [0,1]!")
        
        hexaly_time = int(max_time_in_seconds * solver_ratio)
        gurobi_time = max_time_in_seconds - hexaly_time
        
        hints = {}
        hxly_sol = None
        if hexaly_time:
            hxly = HXLYSolver(instance=self.instance, formulation=SolverFormulation.TABLE)
            
            
            hxly_sol = hxly.solve(log_search_progress=log_search_progress, max_time_in_seconds=hexaly_time, **hexaly_params)
            
            if hxly_sol.return_status == SolverReturnStatus.OPTIMAL:
                return hxly_sol
            elif hxly_sol.return_status == SolverReturnStatus.FEASIBLE:
                hints = hxly_sol.nurses_at_shifts
        
        if gurobi_time:
            grb = GRBSolver(instance=self.instance, hints=hints, formulation=SolverFormulation.IP)
            
            grb_sol = grb.solve(log_search_progress=log_search_progress, max_time_in_seconds=gurobi_time, **gurobi_params)
        
            return grb_sol
        return hxly_sol
        

if __name__ == "__main__":
    instance_nb = 15
    time_limit = 30
    instance_path = f"../../examples/data_processed/Instance{instance_nb}.json"

    with open(instance_path, "r") as f:
        data = f.read()


    instance = NurseRosteringInstance.model_validate_json(data)


    solver = NurseRosteringModel(instance)
    sol = solver.solve(max_time_in_seconds=time_limit, log_search_progress=True) 
    print(sol)
        
        
        