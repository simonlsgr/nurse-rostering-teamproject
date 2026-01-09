import gurobipy as gp
from gurobipy import GRB 
from nurse_rostering.model.model_interface import ModelInterface

class GurobiAdapter(ModelInterface):
 
 
    def __init__(self):
    
        self.model = gp.Model()

    def add_var(self, name, var_type="bool", lb=None, ub=None):
    
        if var_type == "bool":
            v = self.model.addVar(vtype=GRB.BINARY, name=name)
        
        elif var_type == "int":
            v = self.model.addVar(vtype=GRB.INTEGER,
                                  lb=lb if lb is not None else 0,
                                  ub=ub if ub is not None else GRB.INFINITY,
                                  name=name)
        
        else:  # float
            v = self.model.addVar(vtype=GRB.CONTINUOUS,
                                  lb=lb if lb is not None else -GRB.INFINITY,
                                  ub=ub if ub is not None else GRB.INFINITY,
                                  name=name)
            
        return v

    def add_constraint(self, expr, if_var=None):

        if if_var is None:
            self.model.addConstr(expr)

        else:
            raise NotImplementedError("Gurobi adapter only supports int/bool variables")

    def add_max_equality(self, expr_lhs, expr_rhs):
        self.model.addConstr(expr_lhs == max(expr_rhs))


    def set_objective(self, expr, sense="min"):

        if sense == "min":
            self.model.setObjective(expr, GRB.MINIMIZE)

        else:
            self.model.setObjective(expr, GRB.MAXIMIZE)

    def sum(self, iterable):
        return gp.quicksum(iterable)

    def get_solution_value(self, var):
        return var.X