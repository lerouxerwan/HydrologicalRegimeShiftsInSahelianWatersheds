import time

import numpy as np

from calibration.dynamical_model.dynamical_model import DynamicalModel
from calibration.observation_constraint.observation_constraint import ObservationConstraint
from calibration.utils_calibration.sampling import Sampling
from calibration.utils_calibration.solve import SolverMethod
from calibration.utils_calibration.utils_sample import params_sampled
from utils.utils_log import log_info


def load_params_vector_list_sample_v2(dynamical_model: DynamicalModel, nb_samples: int, initial_year: int = None,
                                      initial_forcings: dict[str, float] = None,
                                      observation_constraint: ObservationConstraint = None,
                                      sampling: Sampling = Sampling.V2_INITIAL,
                                      solver_method: SolverMethod = SolverMethod.RK45) -> np.ndarray:
    """Sample parameters using a LatinHypercube
    Eliminate samples that do not fulfill the desired constraint, e.g. a valid value for the initial state
    :return: A matrix where each row correspond to a vector of parameters"""
    assert isinstance(nb_samples, int) and nb_samples > 0
    log_info(f'Start sampling {nb_samples} parameters')
    start = time.time()
    #  Insert the columns for the random parameters
    params_vector_list = []
    for params in params_sampled(dynamical_model, nb_samples):
        if condition(params, dynamical_model, initial_year, initial_forcings, observation_constraint, sampling):
            params_vector = dynamical_model.get_params_vector(params)
            params_vector_list.append(params_vector)
        if len(params_vector_list) == nb_samples:
            break
    if len(params_vector_list) < nb_samples:
        raise ValueError('Sampling failed, change conditions or increase multiplicative factor')
    log_info(f'End sampling {nb_samples} parameters in {time.time() - start}s')
    return np.array(params_vector_list)


def condition(params: dict[str, float], dynamical_model: DynamicalModel,
              initial_year: int = None, initial_forcings: dict[str, float] = None,
              observation_constraint: ObservationConstraint = None,
              sampling: Sampling = Sampling.V2_INITIAL) -> bool:
    # Compute initial state
    initial_state = dynamical_model.get_state(initial_forcings, initial_year, params, observation_constraint)
    condition_initial_state_is_not_nan = not np.isnan(initial_state).any()
    if sampling is Sampling.V2_INITIAL:
        return condition_initial_state_is_not_nan
    else:
        raise NotImplementedError











