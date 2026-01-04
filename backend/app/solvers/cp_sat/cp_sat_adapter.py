from ortools.sat.python import cp_model
from solvers.model_interface import ModelInterface


class CpSatAdapter(ModelInterface):
 
 
    def __init__(self):
    
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

    def add_var(self, name, var_type="bool", lb=None, ub=None):
    
        if var_type == "bool":
            v = self.model.new_bool_var(name)

        elif var_type == "int":
            v = self.model.new_int_var(lb if lb is not None else 0,
                                     ub if ub is not None else cp_model.INT32_MAX,
                                     name)
        else:
            raise NotImplementedError("CP-SAT adapter only supports int/bool variables")

        return v

    def add_constraint(self, expr, if_var=None):
        # expr: CP-SAT LinearExpr
        if if_var is None:
          self.model.add(expr)

        else:
          self.model.add(expr).OnlyEnforceIf(if_var)

    def add_max_equality(self, expr_lhs, expr_rhs):

        self.model.add_max_equality(expr_lhs, expr_rhs)

    def set_objective(self, expr, sense="min"):

        if sense == "min":
            self.model.minimize(expr)

        else:
            self.model.maximize(expr)

    def sum(self, iterable):
        return sum(iterable)

    def get_solution_value(self, var):
        return self.solver.value(var)