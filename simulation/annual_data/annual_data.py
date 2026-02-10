from abc import abstractmethod
from functools import cached_property

import numpy as np
import pandas as pd

from simulation.data import Data


class AnnualData(Data):

    @property
    @abstractmethod
    def _series(self) -> pd.Series:
        """Series must have years as index and annual values as values"""
        pass

    @cached_property
    def data(self) -> tuple[list[int], list[np.ndarray]]:
        return self._load_data()

    def _load_data(self) -> tuple[list[int], list[np.ndarray]]:
        series = self._series
        years = [int(v) for v in series.index.values]
        forcing_vector_list = [np.array([float(v)]) for v in series.values]
        assert len(years) == len(forcing_vector_list)
        return years, forcing_vector_list

    @property
    def years(self) -> list[int]:
        return self.data[0]

    @property
    def forcing_vector_list(self) -> list[np.ndarray]:
        return self.data[1]

    @property
    def values(self) -> np.ndarray:
        return np.array([forcing_vector[0] for forcing_vector in self.forcing_vector_list])

    @property
    def year_to_value(self) -> dict[int, float]:
        return {year: forcing_vector[0] for year, forcing_vector in zip(self.years, self.forcing_vector_list)}