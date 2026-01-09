from abc import ABC, abstractmethod


class ModelInterface(ABC):

    @abstractmethod
    def add_var(self, name, type="bool", lb=None, ub=None, hx_model=None):
        """
        hx_model: optional, is only used for the hexaly implementation to accommodate the different structure.
        """
        pass
      
    @abstractmethod
    def add_constraint(self, expr, if_var=None, hx_model=None):
        """
        if_var: optional, bool variable to conditionally enforce this constraint (does not work yet)
        hx_model: optional, is only used for the hexaly implementation to accommodate the different structure.
        """
        pass
      
    @abstractmethod
    def set_objective(self, expr, sense="min", hx_model=None):
        """
        hx_model: optional, is only used for the hexaly implementation to accommodate the different structure.
        """
        pass
      
    @abstractmethod
    def add_max_equality(self, expr_lhs, expr_rhs, hx_model=None):
        """
        hx_model: optional, is only used for the hexaly implementation to accommodate the different structure.
        """
        pass
      
    @abstractmethod
    def sum(self, iterable, hx_model=None):
        """
        hx_model: optional, is only used for the hexaly implementation to accommodate the different structure.
        """
        pass
      
    @abstractmethod
    def get_solution_value(self, var, hx_model=None):
        """
        hx_model: optional, is only used for the hexaly implementation to accommodate the different structure.
        """
        pass