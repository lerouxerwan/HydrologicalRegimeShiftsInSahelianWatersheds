import numpy as np

from calibration.forcing_function.rain.rain_forcing_function import RAIN_STR
from calibration.forcing_function.unidimensional_forcing_function import UnidimensionalForcingFunction


class ConstantForcing(UnidimensionalForcingFunction):

    def __init__(self, nb_years: int, constant_value: float, initial_year: int = 1955):
        assert nb_years > 0
        assert isinstance(nb_years, int)
        assert isinstance(constant_value, float)
        years = [initial_year + i for i in range(nb_years)]
        forcing_vector_list = [np.array([constant_value]) for _ in range(nb_years)]
        super().__init__(years, forcing_vector_list)
        self.constant_value = constant_value

    @property
    def name(self) -> str:
        return "constant"

    @property
    def y_label(self) -> str:
        raise f'Constant forcing equals to {self.constant_value}'


class RainConstantForcingOnlyForSolver(UnidimensionalForcingFunction):

    def __init__(self, nb_years: int, constant_value: float, initial_year: int = 1955):
        assert nb_years > 0
        assert isinstance(nb_years, int)
        assert isinstance(constant_value, float)
        #  Fake call to __init__ to improve speed (important functions are quickly overriden below)
        super().__init__([initial_year], [np.array([constant_value])])
        # Save arguments
        self._nb_years = nb_years
        self._initial_year = initial_year
        #  Create a unique dictionary for the forcing
        self._unique_forcings = {RAIN_STR: constant_value}

    def get_forcings_for_ivt_solver(self, time: float):
        return self._unique_forcings

    def get_forcings(self, time: float) -> dict[str, float]:
        #  This forcing function should only be called for the solver
        raise NotImplementedError

    @property
    def initial_year(self) -> int:
        return self._initial_year

    @property
    def final_year(self) -> int:
        return self._initial_year + self._nb_years - 1

    @property
    def name(self) -> str:
        raise ValueError('This property should not have been called')

    @property
    def y_label(self) -> str:
        raise ValueError('This property should not have been called')

