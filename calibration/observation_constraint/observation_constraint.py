from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Union

import numpy as np

from utils.utils_exception import MissingConstraintValue


@dataclass
class ObservationConstraint(ABC):
    """Define an observation constraint for a dynamical model"""
    years: list[int]  #  list of years when we have at least one constraint, i.e. one constraint not equal to np.nan
    constraint_names: list[str]
    constraint_name_to_values: dict[str, list[float]]  # maps each constraint to its values (same order as self.years)
    final_year: Union[None, int] = None

    def __post_init__(self):
        #   If final_year is not None, we delete all years strictly above it
        if self.final_year is not None:
            index_to_remove = set([i for i, year in enumerate(self.years) if year > self.final_year])
            self.years = [year for i, year in enumerate(self.years) if i not in index_to_remove]
            self.constraint_name_to_values = {
                name: [v for i, v in enumerate(values) if i not in index_to_remove]
                for name, values in self.constraint_name_to_values.items()
            }
        #   dictionary that maps each year to its correspond index in the list self.years
        self.year_to_index = {year: i for i, year in enumerate(self.years)}

    def get_constraint_value(self, constraint_name: str, year: int) -> float:
        #  Constraint is valid for the whole year
        assert isinstance(year, int)
        if year in self.year_to_index:
            return self.constraint_name_to_values[constraint_name][self.year_to_index[year]]
        else:
            raise MissingConstraintValue(f'no constraint for year = {year}')

    def get_unique_constraint_value(self, year: int) -> float:
        assert len(self.constraint_names) == 1
        return self.get_constraint_value(self.constraint_names[0], year)


    @property
    def name(self) -> str:
        suffix = '' if self.final_year is None else 'until{}'.format(self.final_year)
        return self._name + suffix

    @property
    @abstractmethod
    def _name(self) -> str:
        pass

    ###########################################
    #
    #           Plot Functions
    #
    ###########################################

    @cached_property
    def constraint_name_to_marker(self) -> dict[str, str]:
        markers = ['o', 'x']
        assert len(self.constraint_names) <= len(markers), 'add markers'
        return dict(zip(self.constraint_names, markers))

    def plot_observation_constraint(self, ax, user_label=False, initial_year=None,
                                    user_color=None, user_marker=None, linestyle='',
                                    user_markersize=None):
        #  By default, the initial year is the first year
        if initial_year is None:
            initial_year = self.years[0]
        for constraint_name in self.constraint_names:
            if isinstance(user_label, str):
                label = user_label
            else:
                assert isinstance(user_label, bool)
                label = constraint_name if user_label else None
            color = self.constraint_name_to_color[constraint_name] if user_color is None else user_color
            marker = self.constraint_name_to_marker[constraint_name] if user_marker is None else user_marker
            values = self.constraint_name_to_values[constraint_name]
            markersize = 7 if user_markersize is None else user_markersize
            if (len(values) > 0) and (not all([np.isnan(v) for v in values])):
                years_for_plot, values_for_plot = zip(
                    *[(year, value) for year, value in zip(self.years, values) if
                      (not np.isnan(value)) and (year >= initial_year)])
                # Shift the year by 0.5 so that they are displayed in the middle of the year,
                # and illustrate well the fact that the constraint is applied for all the year.
                years_for_plot = [year + 0.5 for year in years_for_plot]
                ax.plot(years_for_plot, values_for_plot, marker=marker, color=color, markersize=markersize,
                        label=label, linestyle=linestyle)

    @property
    @abstractmethod
    def constraint_name_to_color(self) -> dict[str, str]:
        pass
