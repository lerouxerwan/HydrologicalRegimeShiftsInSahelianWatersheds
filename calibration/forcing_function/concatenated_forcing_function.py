from itertools import chain

import numpy as np

from calibration.forcing_function.forcing_function import ForcingFunction


class ConcatenatedForcingFunction(ForcingFunction):

    def __init__(self, forcing_functions: list[ForcingFunction]):
        assert len(forcing_functions) >= 2
        self.forcing_functions = forcing_functions
        # Load years
        years = set(forcing_functions[0].years)
        for forcing_function in forcing_functions[1:]:
            years = years.intersection(forcing_function.years)
        years = sorted(list(years))
        # Load forcings
        forcing_vector_list = []
        for year in years:
            iterable = [forcing_function.year_to_forcing_vector[year] for forcing_function in forcing_functions]
            values = np.array(list(chain.from_iterable(iterable)))
            forcing_vector_list.append(values)
        # Load names
        forcing_names = list(chain.from_iterable([forcing_function.forcing_names for forcing_function in self.forcing_functions]))
        super().__init__(years, forcing_vector_list, forcing_names)

    @property
    def name(self):
        return '+'.join([forcing_function.name for forcing_function in self.forcing_functions])

    def plot_forcing_function(self, ax, years: list[int]) -> None:
        raise NotImplementedError

    @property
    def y_label(self) -> str:
        raise NotImplementedError









