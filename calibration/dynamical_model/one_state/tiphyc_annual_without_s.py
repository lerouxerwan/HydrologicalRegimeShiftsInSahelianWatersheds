import numpy as np

from calibration.dynamical_model.dynamical_model import DynamicalModel
from calibration.forcing_function.forcing_function import ForcingFunction
from calibration.forcing_function.rain.rain_forcing_function import RAIN_STR
from calibration.observation_constraint.observation_constraint import ObservationConstraint
from calibration.observation_constraint.runoff.runoff_coefficient_constraint import \
    RunoffCoefficientObservationConstraint
from calibration.observation_constraint.vegetation.vegetation_and_runoff_coefficient_constraint import \
    VegetationAndRunoffCoefficientObservationConstraint


class DynamicalModelTipHycAnnualWithoutS(DynamicalModel):
    WATER_HOLDING_STATE_STR = 'c'

    def __init__(self, forcing_function: ForcingFunction):
        #   Names of the state variables
        state_names = [self.WATER_HOLDING_STATE_STR]
        #  Name of the parameters
        parameter_names = ['c_croiss', 'i_croiss', 'c_max', 'c_mort', 'i_mort',
                           'mu_c', 'p_ini', 'p_0max', 'a', 'b', 'Ke_max']
        #  For each parameter specify the value or the range for uniform sampling
        parameter_name_to_value_or_range = {
            'c_croiss': (0.2, 2),
            'i_croiss': (150, 700),
            'c_max': 1.0,
            'c_mort': (0.5, 5),
            'i_mort': (10, 200),
            'mu_c': (2e-3, 5e-3),
            'p_ini': (0, 140),
            'p_0max': (600, 800),
            'a': 1.5,
            'b': 8.0,
            'Ke_max': (0.1, 1.0)
        }
        super().__init__(forcing_function, state_names, parameter_names, parameter_name_to_value_or_range)

    def derivative(self, states: dict[str, float], forcings: dict[str, float], params: dict[str, float]) -> float:
        #  Cast c_t in the good range of values and store it in the states dictionary
        c_t = max(min(states[self.WATER_HOLDING_STATE_STR], 1), 0)
        states[self.WATER_HOLDING_STATE_STR] = c_t
        #  Compute the intermediate values
        ke = self.compute_ke(states, forcings, params)
        i_l = self.compute_i(ke, forcings)
        #  Compute the derivative
        first_term = params['c_croiss'] * i_l / (i_l + params['i_croiss']) * c_t * (1 - c_t / params['c_max'])
        second_term = c_t * params['c_mort'] * params['i_mort'] / (i_l + params['i_mort'])
        third_term = params['mu_c'] * (1 - c_t)
        dcdt = first_term - second_term + third_term
        return dcdt

    def compute_ke(self, states: dict[str, float], forcings: dict[str, float], params: dict[str, float]) -> float:
        p_0 = params['p_ini'] + states[self.WATER_HOLDING_STATE_STR] * (params['p_0max'] - params['p_ini'])
        #  At the local scale
        ratio = (forcings[RAIN_STR] ** params['a']) / (forcings[RAIN_STR] ** params['a'] + p_0 ** params['a'])
        return (ratio ** params['b']) * params['Ke_max']

    @staticmethod
    def compute_i(ke: float, forcings: dict[str, float]) -> float:
        return forcings[RAIN_STR] * (1 - ke)

    @property
    def variable_name_to_color(self) -> dict[str, str]:
        return {
            'c': 'blue',
            'Ke': 'blueviolet',
        }

    @property
    def name(self) -> str:
        return "TiphycAnnualWithoutS"

    def plot_dynamical_model(self, ax, times, params: dict[str, float], states_list, highlight=False):
        variable_name_to_variables = super().plot_dynamical_model(ax, times, params, states_list, highlight)
        #  Add plot for the flow
        variable_name = 'Ke'
        ke_list = [self.get_variable(variable_name, forcings, states, params)
                   for forcings, states in zip(self.forcing_function.get_forcings_list(times), states_list)]
        variable_name_to_variables[variable_name] = ke_list
        self.plot_variable(ax, times, ke_list, variable_name, highlight)
        return variable_name_to_variables

    def get_variable(self, variable_name: str, forcings: dict[str, float], states: dict[str, float],
                     params: dict[str, float]) -> float:
        assert isinstance(forcings, dict)
        if variable_name == 'Ke':
            return self.compute_ke(states, forcings, params)
        else:
            return super().get_variable(variable_name, forcings, states, params)

    def get_state(self, forcings: dict[str, float], year: int, params: dict[str, float],
                  observation_constraint: ObservationConstraint) -> list[float]:
        if isinstance(observation_constraint, (RunoffCoefficientObservationConstraint,
                                               VegetationAndRunoffCoefficientObservationConstraint)):
            variable_name = 'Ke'
            ke = observation_constraint.get_constraint_value(variable_name, year)
            return self._get_state(forcings, params, ke, observation_constraint)
        else:
            raise NotImplementedError

    def _get_state(self, forcings: dict[str, float], params: dict[str, float], constraint_value: float,
                   observation_constraint: ObservationConstraint) -> list[float]:
        if isinstance(observation_constraint, (RunoffCoefficientObservationConstraint,
                                               VegetationAndRunoffCoefficientObservationConstraint)):
            return [self.compute_c_t_from_ke(constraint_value, forcings, params)]
        else:
            raise NotImplementedError

    def compute_c_t_from_ke(self, ke, forcings, params):
        """This function was computed by end by inverting the equation of the model Wendling2022"""
        intermediate_value = (ke / params['Ke_max']) ** (-1 / params['b'])
        if intermediate_value > 1:
            p_o = forcings[RAIN_STR] * (intermediate_value - 1) ** (1 / params['a'])
            c_t = (p_o - params['p_ini']) / (params['p_0max'] - params['p_ini'])
            return max(min(c_t, 1), 0)
        else:
            return np.nan

    @property
    def extremal_initial_states(self):
        return [[0.01], [0.99]]


