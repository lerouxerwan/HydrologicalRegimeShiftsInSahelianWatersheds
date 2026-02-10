import numpy as np

from calibration.forcing_function.forcing_function import ForcingFunction
from calibration.forcing_function.unidimensional_forcing_function import UnidimensionalForcingFunction


class AggregatedForcingFunction(UnidimensionalForcingFunction):
    """Forcing Function that aggregates the trajectory of several climate_simulation into one single trajectory"""

    def __init__(self, forcing_functions: list[ForcingFunction]):
        min_year = min([forcing_function.years[0] for forcing_function in forcing_functions])
        max_year = max([forcing_function.years[-1] for forcing_function in forcing_functions])
        years = list(range(min_year, max_year + 1))
        all_forcings = []
        for forcing_function in forcing_functions:
            forcing_list = []
            for year in years:
                if year in forcing_function.year_to_forcing:
                    forcing_list.append(forcing_function.year_to_forcing[year])
                else:
                    forcing_list.append(np.nan)
            all_forcings.append(forcing_list)
        forcing_vector_list = [np.array([f]) for f in self.aggregate_function(all_forcings, axis=0)]
        super().__init__(years, forcing_vector_list)

    @property
    def forcing_name(self) -> str:
        return self.name

    @property
    def aggregate_function(self):
        raise NotImplementedError

    @property
    def name(self) -> str:
        s = str(self.aggregate_function).split(' at'[0])
        return f'aggregation with {s}'

    @property
    def y_label(self) -> str:
        return self.name


class MinForcingFunction(AggregatedForcingFunction):

    @property
    def aggregate_function(self):
        return np.min


class MeanForcingFunction(AggregatedForcingFunction):

    @property
    def aggregate_function(self):
        return np.mean


class MaxForcingFunction(AggregatedForcingFunction):

    @property
    def aggregate_function(self):
        return np.max
