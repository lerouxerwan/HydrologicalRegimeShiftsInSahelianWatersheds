import logging
from enum import Enum

import numpy as np
from scipy.integrate import solve_ivp

from calibration.dynamical_model.dynamical_model import DynamicalModel
from utils.utils_run import CustomizedValueError


class SolverMethod(Enum):
    RK45 = 'RK45'
    LSODA = 'LSODA'


solver_method_to_str = {
    SolverMethod.RK45: 'RK45',
    SolverMethod.LSODA: 'LSODA',
}


class SolverIvp(object):

    @classmethod
    def solve(cls, dynamical_model: DynamicalModel, initial_state: np.ndarray, times: np.ndarray,
              params: dict[str, float], solver_method: SolverMethod) -> np.ndarray:
        assert len(times) > 1, times
        times = times.copy()
        length_of_times = len(times)
        try:
            if np.isnan(initial_state).any():
                raise CustomizedValueError('nan in the initial state')
            dynamical_model.params_for_model_function = params
            ode_result = solve_ivp(dynamical_model.model_function, t_span=(times[0], times[-1]), y0=initial_state,
                                   method=solver_method_to_str[solver_method], t_eval=times)
            res = ode_result.y.transpose()[-length_of_times:]
            #  If the solver fail to return a result for each time step, we return an exception
            if len(res) < length_of_times:
                raise CustomizedValueError('solver crashed')
        except CustomizedValueError as e:
            logging.warning(e.__repr__())
            # Create a trajectory with only np.nan values but with the expected dimension for the result
            res = [np.array(initial_state) * np.nan for _ in range(length_of_times)]
        finally:
            dynamical_model.params_for_model_function = None
        return res
