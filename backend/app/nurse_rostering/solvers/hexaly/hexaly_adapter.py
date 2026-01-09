import hexaly.optimizer

from nurse_rostering.model.model_interface import ModelInterface

class HexalyAdapter(ModelInterface):
    
    def __init__(self):
        pass
    
    def add_var(self, name, var_type="bool", lb=None, ub=None, hx_model=None):
        
        if var_type == "bool":
            v = hx_model.bool()
        
        elif var_type == "int":
            v = hx_model.int(lb, ub)
        
        else:  # float
            v = hx_model.float(lb, ub)
            
        return v
    
    
    def add_constraint(self, expr, if_var=None, hx_model=None):

        if if_var is None:
            hx_model.constraint(expr)
            
        else:
            raise NotImplementedError("Hexaly adapter only supports int/bool variables")
        
    def add_max_equality(self, expr_lhs, expr_rhs, hx_model=None):

        hx_model.constraint(expr_lhs == max(expr_rhs))
        
    def set_objective(self, expr, sense="min", hx_model=None):
        if sense == "min":
            hx_model.minimize(expr)

        else:
            hx_model.maximize(expr)

    def sum(self, iterable, hx_model=None):
        return hx_model.sum(iterable)
    
    def get_solution_value(self, var, hx_model=None):
        return var.value