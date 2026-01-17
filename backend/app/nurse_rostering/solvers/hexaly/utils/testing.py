
import hexaly.optimizer


class AssertModelFeasible:
    def __enter__(self):
        self.optimizer = hexaly.optimizer.HexalyOptimizer()
        self.optimizer.__enter__()
        self.model = self.optimizer.model
        return self.model
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.model.minimize(0)
        self.model.close()
        self.optimizer.solve()
        
        if self.optimizer.solution.status not in (hexaly.optimizer.HxSolutionStatus.OPTIMAL, hexaly.optimizer.HxSolutionStatus.FEASIBLE):
            raise Exception(f"Expected feasible, but got status {self.optimizer.solution.status}")
        
        self.optimizer.__exit__()
        
class AssertModelInfeasible:
    def __enter__(self):
        self.optimizer = hexaly.optimizer.HexalyOptimizer()
        self.optimizer.__enter__()
        self.model = self.optimizer.model
        return self.model
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.model.minimize(0)
        self.model.close()
        self.optimizer.solve()
        
        if self.optimizer.solution.status not in (hexaly.optimizer.HxSolutionStatus.INFEASIBLE, hexaly.optimizer.HxSolutionStatus.INCONSISTENT):
            raise Exception(f"Expected infeasible, but got status {self.optimizer.solution.status}")
        
        self.optimizer.__exit__()