import numpy as np

from calibration.dynamical_model.dynamical_model import DynamicalModel
from calibration.forcing_function.forcing_function import ForcingFunction
from calibration.forcing_function.rain.rain_forcing_function import RAIN_STR
from calibration.observation_constraint.observation_constraint import ObservationConstraint
from calibration.observation_constraint.vegetation.ortonde_vegetation_constraint import OrtondeVegetationConstraint


class DynamicalModelWendling2019(DynamicalModel):
    WOODY_STR = 'w'
    BARE_STR = 'b'

    def __init__(self, forcing_function: ForcingFunction):
        #   Names of the state variables
        state_names = [self.WOODY_STR, self.BARE_STR]
        #  Name of the parameters
        parameter_names = ['r_g', 'r_r', 'r_d', 'i_g', 'i_d', 'mu', 'alpha_p', 'alpha_r', 'ke_b', 'l']
        #  For each parameter specify the value or the range for uniform sampling
        parameter_name_to_value_or_range = {
            'r_g': (0, 1.5),
            'r_r': (0, 1.5),
            'r_d': (0, 1.5),
            'i_g': (250, 350),
            'i_d': (100, 200),
            'mu': (1e-4, 1e-3),
            'alpha_p': (2e-4, 2e-3),
            'alpha_r': (5e-3, 5e-2),
            'ke_b': 0.5,
            'l': (80, 220),
        }
        super().__init__(forcing_function, state_names, parameter_names, parameter_name_to_value_or_range)

    @property
    def extremal_initial_states(self):
        return [[0.01, 0.99], [0.99, 0.01]]

    def derivative(self, states, forcings, params):
        b_t = states[self.BARE_STR]
        w_t = states[self.WOODY_STR]
        #  Compute intermediary values
        p_t = forcings[RAIN_STR]
        h_t = 1 - w_t - b_t
        ke = self.compute_ke(states, params)
        i_t = p_t * (1 - ke)
        r_t = p_t * ke
        #  Valentin explained that they fixed i_r = i_g
        #  which means that same water on the ground for the growth and recolonization
        i_r = params['i_g']
        intermediary2_t = params['r_r'] * i_t * w_t * b_t / (i_t + i_r)
        #  Compute derivative with respect to w
        dwdt = params['r_g'] * i_t * w_t * h_t / (i_t + params['i_g'])
        dwdt += intermediary2_t
        dwdt -= params['r_d'] * params['i_d'] * w_t / (i_t + params['i_d'])
        dwdt += params['mu']
        #  Compute derivative with respect to b
        dbdt = h_t * params['alpha_p'] * p_t
        dbdt += h_t * params['alpha_r'] * r_t
        dbdt -= intermediary2_t
        #  Return the tuple of derivatives
        return dwdt, dbdt

    def compute_ke(self, states, params):
        fl_star = self.compute_fl_star(states, params)
        ke = params['ke_b'] * fl_star
        return ke

    def compute_fl_star(self, states, params):
        intermediary_t = params['l'] * (1 - states[self.BARE_STR])
        fl_star = 2 * states[self.BARE_STR] * (intermediary_t - 1 + np.exp(-intermediary_t)) / (intermediary_t ** 2)
        return fl_star

    def get_variable(self, variable_name: str, forcings: dict[str, float], states: dict[str, float], params: dict[str, float]) -> float:
        if variable_name == 'Ke':
            return self.compute_ke(states, params)
        else:
            return super().get_variable(variable_name, forcings, states, params)

    @property
    def variable_name_to_color(self):
        return {
            self.WOODY_STR: 'g',
            self.BARE_STR: 'r',
            'Ke': 'violet'
        }

    @property
    def name(self) -> str:
        return "Wendling2019"

    def plot_dynamical_model(self, ax, times, params, states_list, highlight=False):
        variable_name_to_variables = super().plot_dynamical_model(ax, times, params, states_list, highlight)
        ax.set_ylim((0, 1))
        #  Add plot for the flow
        variable_name = 'Ke'
        ke_list = [self.compute_ke(states, params) for states in states_list]
        variable_name_to_variables[variable_name] = ke_list
        self.plot_variable(ax, times, ke_list, variable_name, highlight)
        return variable_name_to_variables

    def get_state(self, forcings: dict[str, float], year: int, params: dict[str, float],
                  observation_constraint: ObservationConstraint) -> list[float]:
        if isinstance(observation_constraint, OrtondeVegetationConstraint):
            return [observation_constraint.get_constraint_value(state_name, year) for state_name in self.state_names]
        raise NotImplementedError

    def _get_state(self, forcings: dict[str, float], params: dict[str, float], constraint_value: float,
                   observation_constraint: ObservationConstraint) -> list[float]:
        raise NotImplementedError


