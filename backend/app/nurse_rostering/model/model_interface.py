from abc import ABC, abstractmethod


class ModelInterface(ABC):

    @abstractmethod
    def add_var(self, name, type="bool", lb=None, ub=None):
        pass
      
    @abstractmethod
    def add_constraint(self, expr, if_var=None):
        """
        if_var: optional, bool variable to conditionally enforce this constraint (does not work yet)
        """
        pass
      
    @abstractmethod
    def set_objective(self, expr, sense="min"):
        pass
      
    @abstractmethod
    def add_max_equality(self, expr_lhs, expr_rhs):
        pass
      
    @abstractmethod
    def sum(self, iterable):
        pass
      
    @abstractmethod
    def get_solution_value(self, var):
        pass