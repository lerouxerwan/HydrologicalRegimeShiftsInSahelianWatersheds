from collections import OrderedDict
from collections.abc import Iterable
from typing import Union

import numpy as np

from calibration.dynamical_model.dynamical_model import DynamicalModel
from bifurcation.bifurcation_data.attractor_functions import get_attractor
from calibration.utils_calibration.solve import SolverMethod
from tests.bifurcation.test_stability_ranges import solver_method


def compute_empty_forcing_to_repulsor(stability_ranges, max_forcing):
    stability_forcing_range = stability_ranges[0]
    if np.isnan(stability_forcing_range[0]):
        return {}
    else:
        return {forcing: np.nan for forcing in forcing_inside_bistable_range(max_forcing, stability_ranges)}


def compute_forcing_to_repulsor(dynamical_model, params, stability_ranges, is_bistable, max_forcing, solver_method: SolverMethod):
    return repulsors_bistable_range(dynamical_model, params, stability_ranges, max_forcing, solver_method) if is_bistable else dict()


def repulsors_bistable_range(dynamical_model: DynamicalModel, params: dict[str, float], stability_ranges, max_forcing,
                             solver_method: SolverMethod):
    """
    Compute the repulsor for each forcing that is strictly inside the bistability range.
    """
    assert max_forcing.is_integer()
    # Load list of forcings
    forcings_inside_bistable_range = forcing_inside_bistable_range(max_forcing, stability_ranges)
    return repulsors_for_bistable_forcings(dynamical_model, params, forcings_inside_bistable_range, solver_method)


def forcing_inside_bistable_range(max_forcing, stability_ranges):
    stability_forcing_range = stability_ranges[0]
    initial_forcing = stability_forcing_range[0]
    final_forcing = stability_forcing_range[1] if not np.isnan(stability_forcing_range[1]) else max_forcing
    forcings_inside_bistable_range = np.arange(initial_forcing + 1, final_forcing)
    return forcings_inside_bistable_range


def repulsors_for_bistable_forcings(dynamical_model: DynamicalModel, params: dict[str, float],
                                    bistable_forcings: Iterable[float], solver_method: SolverMethod) -> dict[float, float]:
    value_above_repulsor = dynamical_model.extremal_initial_states[1][0]
    value_under_repulsor = dynamical_model.extremal_initial_states[0][0]
    #  Compute repulsor for forcings
    forcing_to_repulsor = OrderedDict()
    for bistable_forcing in bistable_forcings:
        repulsor = find_repulsor(dynamical_model, params, bistable_forcing, 0,
                                 value_under_repulsor, value_above_repulsor, solver_method)
        #  If one method succeeded we store the computed value
        if repulsor is not None:
            forcing_to_repulsor[bistable_forcing] = repulsor
    return forcing_to_repulsor


def find_repulsor(dynamical_model: DynamicalModel, params: dict[str, float], bistable_forcing: float,
                  nb_iterations: int,
                  value_under_repulsor: float, value_above_repulsor: float,
                  solver_method: SolverMethod) -> Union[None, float]:
    """
    Recursive algorithm to find the state value where the repulsor lies for a bistable dynamical model
    The parameter forcing must be located strictly inside the bistability range.
    initial_state_under and initial_state_above are states that respectively under and above the repulsor
    attractor_under, attractor_above are optional arguments that enables us some speedup
    This algorithm is roughly equivalent to a "binary search algorithm"
    """
    assert value_under_repulsor <= value_above_repulsor
    value_middle = 0.5 * (value_under_repulsor + value_above_repulsor)
    #  End of the recursive loop if the two initial states are close enough: the repulsor is roughly in-between
    if np.isclose(value_under_repulsor, value_above_repulsor, rtol=1e-2):
        return value_middle
    #  End of the recursive loop if the maximum number of iterations is reached
    elif nb_iterations == 100:
        return None  #  None means that we did not find any repulsor
    #  Iterate on a recursive loop
    else:
        #  Compute attractors
        attractor_value_under_repulsor = \
            get_attractor(dynamical_model, params, bistable_forcing, np.array([value_under_repulsor]), solver_method)[0]
        attractor_value_above_repulsor = \
            get_attractor(dynamical_model, params, bistable_forcing, np.array([value_above_repulsor]), solver_method)[0]
        #  Iterate the search
        if attractor_value_above_repulsor < value_middle:
            return find_repulsor(dynamical_model, params, bistable_forcing, nb_iterations + 1, value_under_repulsor,
                                 value_middle, solver_method)
        elif attractor_value_under_repulsor > value_middle:
            return find_repulsor(dynamical_model, params, bistable_forcing, nb_iterations + 1, value_middle,
                                 value_above_repulsor, solver_method)
        else:
            assert attractor_value_under_repulsor <= value_middle <= attractor_value_above_repulsor
            # In this case, we relaunch the search depending on which attractor is the closest to attractor_value_middle
            attractor_value_middle = get_attractor(dynamical_model, params, bistable_forcing, np.array([value_middle]), solver_method)[
                0]
            attractor_value_middle_closer_is_above_repulsor = (
                    abs(attractor_value_above_repulsor - attractor_value_middle)
                    < abs(attractor_value_middle - attractor_value_under_repulsor))
            if attractor_value_middle_closer_is_above_repulsor:
                #  First case: attractor_middle is above repulsor, then we relaunch
                # the search between value_under_repulsor and the min value above the repulsor
                min_value_above_repulsor = min(value_middle, attractor_value_middle, attractor_value_above_repulsor)
                return find_repulsor(dynamical_model, params, bistable_forcing, nb_iterations + 1, value_under_repulsor,
                                     min_value_above_repulsor, solver_method)
            else:
                #  Second case: attractor_middle is under the repulsor, then we relaunch
                # the search between value_above_repulsor and the max state reached under the repulsor
                max_value_under_repulsor = max(value_middle, attractor_value_middle, attractor_value_under_repulsor)
                return find_repulsor(dynamical_model, params, bistable_forcing, nb_iterations + 1,
                                     max_value_under_repulsor, value_above_repulsor, solver_method)
