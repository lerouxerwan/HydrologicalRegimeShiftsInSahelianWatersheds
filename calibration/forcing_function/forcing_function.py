from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property

import numpy as np

from calibration.utils_calibration.convert import get_year_from_time, get_time_from_year
from utils.utils_run import CustomizedValueError


@dataclass
class ForcingFunction(ABC):
    """
    Define a forcing function for a dynamical model
    """
    years: list[int]
    forcing_vector_list: list[np.ndarray]
    forcing_names: list[str]

    def __post_init__(self):
        self.year_to_forcing_vector = dict(zip(self.years, self.forcing_vector_list))
        self.check_types()

    @cached_property
    def year_to_forcing(self) -> dict[int, float]:
        return {year: forcing[0] for year, forcing in self.year_to_forcing_vector.items()}

    @cached_property
    def forcings_array(self) -> np.ndarray:
        return np.array([forcing[0] for forcing in self.forcing_vector_list])

    def get_forcings_for_ivt_solver(self, time: float) -> dict[str, float]:
        """Load forcings - this function should be used only for the ivt solver"""
        year = get_year_from_time(time)
        if year > self.final_year:
            #  This case might happen due to a bug in the select_initial_step functions of ivt solver
            #  As a fix, when it occurs, we return the last value of the forcing instead
            #   This fix does not impact the solution of the solver, but only the design of the initial step size
            #  see https://github.com/scipy/scipy/issues/9198 for more details
            time = get_time_from_year(self.final_year)
        return self.get_forcings(time)

    def get_forcings(self, time: float) -> dict[str, float]:
        """Load a dictionary that map each forcing name to its value"""
        year = get_year_from_time(time)
        #  Forcing is a function where the value is valid for the whole year, i.e. a step function
        if not (self.initial_year <= year <= self.final_year):
            raise CustomizedValueError(
                '{} is beyond the range of the forcing ({}, {})'
                .format(year, self.initial_year, self.final_year))
        return self.create_forcings(self.year_to_forcing_vector[year])

    def create_forcings(self, forcing_vector: Iterable[float]) -> dict[str, float]:
        """Function that creates a forcings from a forcing_vector"""
        return dict(zip(self.forcing_names, forcing_vector))

    def get_forcings_list(self, times: Iterable[float]) -> list[dict[str, float]]:
        """Load the list of forcings corresponding to a list of time"""
        return [self.get_forcings(time) for time in times]

    @property
    def initial_year(self) -> int:
        return self.years[0]

    @property
    def final_year(self) -> int:
        return self.years[-1]

    @abstractmethod
    def plot_forcing_function(self, ax, years: list[int]) -> None:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def check_types(self) -> None:
        assert isinstance(self.years, list)
        assert isinstance(self.years[0], int), self.years[0]
        assert isinstance(self.forcing_vector_list, list)
        first_forcing_vector = self.forcing_vector_list[0]
        assert isinstance(first_forcing_vector, np.ndarray), first_forcing_vector
        assert all([isinstance(f, float) for f in first_forcing_vector])
        assert isinstance(self.forcing_names, list)
        assert isinstance(self.forcing_names[0], str)
        assert len(first_forcing_vector) == len(self.forcing_names)
        assert len(self.years) == len(self.forcing_vector_list)
