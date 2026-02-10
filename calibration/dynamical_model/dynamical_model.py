from abc import ABC, abstractmethod
from collections import OrderedDict
from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
from functools import cached_property
from typing import Union

import numpy as np

from calibration.forcing_function.forcing_function import ForcingFunction
from calibration.observation_constraint.observation_constraint import ObservationConstraint
from calibration.utils_calibration.convert import get_time_from_year
from utils.utils_exception import MissingConstraintValue


@dataclass
class DynamicalModel(ABC):
    """Define states, functions and parameters of a dynamical model"""
    forcing_function: ForcingFunction
    state_names: list[str]
    parameter_names: list[str]
    parameter_name_to_value_or_range: dict[str, Union[float, tuple[float, float]]]

    def __post_init__(self):
        self.params_for_model_function = None
        self.back_up_original_forcing_function = deepcopy(self.forcing_function)
        self.check_types()

    def model_function(self, time: float, state_vector: np.ndarray) -> float:
        """Compute dy/dt the derivative of y with respect to t"""
        #  Transform np.ndarray as dictionaries and call derivative function
        forcings = self.forcing_function.get_forcings_for_ivt_solver(time)
        states = self.create_states(state_vector)
        return self.derivative(states, forcings, self.params_for_model_function)

    ###########################################
    #
    #           Methods that must be defined in child classes
    #
    ###########################################
    @abstractmethod
    def derivative(self, states: dict[str, float], forcings: dict[str, float], params: dict[str, float]) -> float:
        """Compute dy/dt the derivative of y with respect to t. This function must be defined in the child classes"""
        pass

    def get_variable(self, variable_name: str, forcings: dict[str, float], states: dict[str, float],
                     params: dict[str, float]) -> float:
        """Compute a variable for a given forcing/state/parameters of the models"""
        #  By default, any dynamical model return only its state values,
        #   other variables must be defined in the child classes
        if variable_name in self.state_names:
            return states[variable_name]
        else:
            raise NotImplementedError('variable_name={}'.format(variable_name))

    @abstractmethod
    def get_state(self, forcings: dict[str, float], year: int, params: dict[str, float],
                  observation_constraint: ObservationConstraint) -> list[float]:
        """Compute state for a given forcing/parameters of the models"""
        pass

    @abstractmethod
    def _get_state(self, forcings: dict[str, float], params: dict[str, float], constraint_value: float,
                   observation_constraint: ObservationConstraint) -> list[float]:
        """Compute state for a given forcing/parameters of the models"""
        pass

    def get_initial_state(self, years: list[int], params: dict[str, float],
                          observation_constraint: ObservationConstraint) -> list[float]:
        initial_forcings = self.forcing_function.get_forcings(get_time_from_year(years[0]))
        if len(years) == 1:
            return self.get_state(initial_forcings, years[0], params, observation_constraint)
        else:
            constraint_values = []
            for year in years:
                try:
                    constraint_values.append(observation_constraint.get_unique_constraint_value(year))
                except MissingConstraintValue:
                    pass
            mean_constraint_value = np.mean([np.min(constraint_values), np.max(constraint_values)])
            return self._get_state(initial_forcings, params, mean_constraint_value, observation_constraint)

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def extremal_initial_states(self):
        raise NotImplementedError

    ###########################################
    #
    #           Utils Functions
    #
    ###########################################

    def check_types(self):
        """Ensure that attributes are well-defined"""
        assert len(self.state_names) > 0
        assert len(self.parameter_names) > 0
        for parameter_name in self.parameter_names:
            assert parameter_name in self.parameter_name_to_value_or_range
        assert all([isinstance(value_or_range, (tuple, float))
                    for value_or_range in self.parameter_name_to_value_or_range.values()])
        assert len(self.extremal_initial_states) <= 2
        if len(self.state_names) == 1:
            assert self.extremal_initial_states[0][0] < self.extremal_initial_states[1][0]

    @cached_property
    def parameter_name_to_range(self) -> dict[str, tuple]:
        d = OrderedDict()
        for parameter_name in self.parameter_names:
            value_or_range = self.parameter_name_to_value_or_range[parameter_name]
            if isinstance(value_or_range, tuple):
                assert len(value_or_range) == 2
                d[parameter_name] = value_or_range
        return d

    @cached_property
    def parameter_name_to_value(self) -> dict[str, float]:
        d = OrderedDict()
        for parameter_name in self.parameter_names:
            value_or_range = self.parameter_name_to_value_or_range[parameter_name]
            if isinstance(value_or_range, float):
                d[parameter_name] = value_or_range
        return d

    @property
    def unique_state_name(self) -> str:
        assert len(self.state_names) == 1
        return self.state_names[0]

    @property
    def nb_states(self) -> int:
        return len(self.state_names)

    def get_params(self, params_vector: np.ndarray) -> dict[str, float]:
        """Load a dictionary of parameters
        :param params_vector: an array containing the parameters in the order
        :return: a dictionary that maps each parameter name to its value"""
        return dict(zip(self.parameter_names, params_vector))

    def get_params_vector(self, params: dict[str, float]) -> np.ndarray:
        """Load a vector of parameters
        :param params: a dictionary that maps each parameter name to its value
        :return: an array containing the parameters in the order"""
        return np.array([params[param_name] for param_name in self.parameter_names])

    def create_states(self, state_vector: np.ndarray) -> dict[str, float]:
        """Load a dictionary of states
        :param state_vector: an array containing the state values in the order
        :return: a dictionary that maps each state name to its value"""
        return dict(zip(self.state_names, state_vector))

    ###########################################
    #
    #           Plot Functions
    #
    ###########################################

    def plot_dynamical_model(self, ax, times: Iterable[float], params, states_list, highlight=False):
        variable_name_to_variables = {}
        for i, state_name in enumerate(self.state_names):
            variables = [states[state_name] for states in states_list]
            variable_name_to_variables[state_name] = variables
            self.plot_variable(ax, times, variables, state_name, highlight)
        ax.legend(loc='upper left')
        return variable_name_to_variables

    def plot_variable(self, ax, times, variables, variable_name, highlight):
        linewidth = 2 if highlight else 0.2
        color = self.variable_name_to_color[variable_name]
        label = self.variable_name_to_label[variable_name]
        ax.plot(times, variables, color, label=label, linewidth=linewidth)

    @property
    def variable_name_to_color(self):
        raise NotImplementedError

    @cached_property
    def variable_name_to_label(self):
        return {
            'Ke': 'Runoff coefficient',
            'V': 'Vegetation',
            'c': 'Water holding strength',
            'w': 'Woody vegetation',
            'b': 'Bare vegetation',
        }

    @cached_property
    def label_to_variable_name(self):
        return {l: v for v, l in self.variable_name_to_label.items()}
