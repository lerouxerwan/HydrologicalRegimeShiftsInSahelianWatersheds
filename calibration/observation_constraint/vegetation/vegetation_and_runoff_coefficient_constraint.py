from typing import Union

import numpy as np

from calibration.observation_constraint.observation_constraint import ObservationConstraint
from calibration.observation_constraint.runoff.runoff_coefficient_constraint import \
    RunoffCoefficientObservationConstraint
from calibration.observation_constraint.vegetation.vegetation_constraint import \
    VegetationObservationConstraint


class VegetationAndRunoffCoefficientObservationConstraint(ObservationConstraint):
    observation_constraints: list[ObservationConstraint]

    def __init__(self, watershed_name: str, final_year: Union[None, int] = None):
        #   Name of the watershed
        self.watershed_name = watershed_name
        #  Load the two types of constraint
        self.observation_constraints = [RunoffCoefficientObservationConstraint(watershed_name, final_year),
                                        VegetationObservationConstraint(watershed_name, final_year)]
        #  This code only works for constraint with a single constraint
        if not all([len(c.constraint_names) == 1 for c in self.observation_constraints]):
            raise NotImplementedError
        #   Names of the constraint
        constraint_names = [c.constraint_names[0] for c in self.observation_constraints]
        #  Concatenate the years
        set_years_0 = set(self.observation_constraints[0].years)
        set_years_1 = set(self.observation_constraints[1].years)
        years = sorted(list(set_years_0.union(set_years_1)))
        # Specification for vegetation runoff constraint: a runoff constraint must be well-defined for the initial
        # year. Thus, we delete all the years when the runoff constraint has not yet been defined once.
        initial_year_for_runoff = self.observation_constraints[0].years[0]
        years = [year for year in years if year >= initial_year_for_runoff]
        #  Load years and list of constraint
        constraint_name_to_values = {}
        for observation_constraint in self.observation_constraints:
            constraint_name = observation_constraint.constraint_names[0]
            set_years = set(observation_constraint.years)
            values = []
            for year in years:
                if year in set_years:
                    index = observation_constraint.year_to_index[year]
                    value = observation_constraint.constraint_name_to_values[constraint_name][index]
                else:
                    value = np.nan
                values.append(value)
            constraint_name_to_values[constraint_name] = values
        super().__init__(years, constraint_names, constraint_name_to_values, final_year)

    @property
    def constraint_name_to_color(self):
        return {**self.observation_constraints[0].constraint_name_to_color,
                **self.observation_constraints[1].constraint_name_to_color}

    @property
    def _name(self):
        return '_'.join([c._name for c in self.observation_constraints])
