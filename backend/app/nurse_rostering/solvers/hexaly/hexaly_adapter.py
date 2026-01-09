import hexaly.optimizer

from nurse_rostering.model.model_interface import ModelInterface

class HexalyAdapter(ModelInterface):
    
    def __init__(self, model):
        self.model = model
    
    def add_var(self, name, var_type="bool", lb=None, ub=None):
        
        if var_type == "bool":
            v = self.model.bool()
        
        elif var_type == "int":
            v = self.model.int(lb, ub)
        
        else:  # float
            v = self.model.float(lb, ub)
            
        return v
    
    
    def add_constraint(self, expr, if_var=None):

        if if_var is None:
            self.model.constraint(expr)
            
        else:
            raise NotImplementedError("Hexaly adapter only supports int/bool variables")
        
    def add_max_equality(self, expr_lhs, expr_rhs):

        self.model.constraint(expr_lhs == max(expr_rhs))
        
    def set_objective(self, expr, sense="min"):
        if sense == "min":
            self.model.minimize(expr)

        else:
            self.model.maximize(expr)

    def sum(self, iterable):
        return self.model.sum(iterable)
    
    def get_solution_value(self, var):
        return var.value