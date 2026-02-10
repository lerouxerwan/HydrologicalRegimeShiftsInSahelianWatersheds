from collections import OrderedDict

import numpy as np

from calibration.dynamical_model.dynamical_model import DynamicalModel
from calibration.forcing_function.constant_forcing_function import RainConstantForcingOnlyForSolver
from calibration.utils_calibration.convert import load_times
from calibration.utils_calibration.solve import SolverIvp, SolverMethod


def get_forcing_to_attractors(stability_detection):
    if isinstance(stability_detection, dict):
        return {forcing: [attractor] for forcing, attractor in stability_detection.items()}
    else:
        return dict()


def compute_forcing_to_attractors(dynamical_model: DynamicalModel, params: dict[str, float],
                                  stability_detection, min_forcing: float, max_forcing: float,
                                  solver_method: SolverMethod):
    if isinstance(stability_detection, dict):
        return get_forcing_to_attractors(stability_detection)
    else:
        forcings = np.arange(min_forcing, max_forcing + 1)
        ordered_dict_forcing_to_attractor = OrderedDict()
        for forcing in forcings:
            attractors = get_attractors(dynamical_model, params, forcing, solver_method)
            ordered_dict_forcing_to_attractor[forcing] = attractors
        return ordered_dict_forcing_to_attractor


def get_attractors(dynamical_model: DynamicalModel, params: dict[str, float], forcing: float, solver_method: SolverMethod) -> list[np.ndarray]:
    """
    Compute attractors for a given forcing/parameters of the models
    :param dynamical_model: the dynamical model considered
    :param params: a dictionary specifying the parameters of the dynamical model
    :param forcing: a float that represents the value of the forcing
    :return: a list of state that correspond to the attractors
    """
    attractors = [get_lower_attractor(dynamical_model, params, forcing, solver_method),
                  get_upper_attractor(dynamical_model, params, forcing, solver_method)]
    monostable_attractor = np.mean(attractors, axis=0)
    # First case, the two attractors are close, we conclude they correspond to the same monostable attractor
    if np.allclose(attractors[0], attractors[1], rtol=1e-2):
        return [monostable_attractor]
    # Second case, the "lower attractor" is above the "upper attractor" (which can be due to converge issue),
    # we conclude they correspond to the same monostable attractor if th
    elif (attractors[0] > attractors[1]).all():
        assert np.allclose(attractors[0], attractors[1], rtol=1e-1), 'Gap is too large for a simple convergence issue'
        return [monostable_attractor]
    else:
        return attractors


def get_lower_attractor(dynamical_model: DynamicalModel, params: dict[str, float], forcing: float, solver_method: SolverMethod):
    return get_attractor(dynamical_model, params, forcing, dynamical_model.extremal_initial_states[0], solver_method)


def get_upper_attractor(dynamical_model: DynamicalModel, params: dict[str, float], forcing: float, solver_method: SolverMethod):
    return get_attractor(dynamical_model, params, forcing, dynamical_model.extremal_initial_states[1], solver_method)


def get_attractor(dynamical_model: DynamicalModel, params: dict[str, float], forcing: float,
                  initial_state: np.ndarray, solver_method: SolverMethod) -> np.ndarray:
    assert isinstance(forcing, float)
    for nb_iterations in [20, 40, 60, 80, 100, 200, 1000, 2000, 10000]:
        attractor, has_converged = _get_attractor(dynamical_model, params, forcing, initial_state, nb_iterations,
                                                  solver_method)
        #  If process has converged we return the attractor
        if has_converged:
            return attractor
    #  We return the final state for the longest trajectory
    return attractor


def _get_attractor(dynamical_model: DynamicalModel, params: dict[str, float], forcing: float,
                   initial_state: np.ndarray, nb_iterations: int, solver_method: SolverMethod):
    states = solve_trajectory(dynamical_model, params, forcing, initial_state, nb_iterations, solver_method)
    attractor = states[-1]
    has_converged = all([np.allclose(attractor, state, rtol=1e-3) for state in states[-5:-1]])
    return attractor, has_converged


def solve_trajectory(dynamical_model: DynamicalModel, params: dict[str, float], forcing: float,
                     initial_state: np.ndarray, nb_iterations: int, solver_method: SolverMethod):
    """Solve the trajectory for a constant forcing """
    #   We temporarily replace the forcing_function attribution using a MonkeyPatch technique
    dynamical_model.forcing_function = RainConstantForcingOnlyForSolver(nb_years=nb_iterations, constant_value=forcing)
    times = load_times(dynamical_model.forcing_function.initial_year, dynamical_model.forcing_function.final_year - 1)
    states_list = SolverIvp.solve(dynamical_model, initial_state, times, params, solver_method)
    #  Then we reset the original forcing function
    dynamical_model.forcing_function = dynamical_model.back_up_original_forcing_function
    return states_list
