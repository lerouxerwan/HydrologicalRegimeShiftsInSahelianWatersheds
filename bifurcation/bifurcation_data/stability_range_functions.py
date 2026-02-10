from typing import Union

import numpy as np

from bifurcation.bifurcation_data.bistability_functions import is_bistable, \
    compute_is_bistable


def compute_stability_ranges(forcing_to_attractors: dict[float, list[np.ndarray]],
                             stability_detection: Union[float, dict[float, np.ndarray]],
                             min_forcing: float, max_forcing: float) -> tuple[tuple[float, float], tuple[np.ndarray, np.ndarray]]:
    """
    Compute the range of stability which are returned as two tuples
    The first tuple corresponds to the forcing range, e.g. (120.0, 142.0), or (250.0, 632.0)
    The second tuple corresponds to the two state values reached at the forcing range.

    For bistable dynamical model, each value of the forcing range has a single attractor.

    For monostable dynamical model, the forcing range are defined as the location where the slope
    of the attractor curve is respectively the highest and the lowest.
    In the case, stability_detection is a dictionary that maps each forcing to its corresponding attractor value
    """
    if compute_is_bistable(stability_detection):
        #   Bistable case: Stability_detection is a float value that correspond to a bistable forcing.
        forcing_with_bistability = stability_detection
        assert min_forcing < forcing_with_bistability < max_forcing
        #  Compute lower bound. In the case where min_forcing is bistable,
        # we raise an StabilityRangeError to mention that the search failed
        min_forcing_attractors = forcing_to_attractors[min_forcing]
        if is_bistable(min_forcing_attractors):
            raise StabilityRangeError("min_forcing is bistable, min_forcing should be decreased "
                                      "to find the full stability range")
        lower_bound = find_lower_bound(forcing_to_attractors, min_forcing, forcing_with_bistability)
        attractor_left = forcing_to_attractors[lower_bound][0]
        #  Compute upper bound. In the case where max_forcing is bistable,
        #  we set upper_bound to np.nan and attractor_right to np.array(np.nan)
        max_forcing_attractors = forcing_to_attractors[max_forcing]
        if is_bistable(max_forcing_attractors):
            upper_bound = np.nan
            attractor_right = np.array([np.nan])
        else:
            upper_bound = find_upper_bound(forcing_to_attractors, forcing_with_bistability, max_forcing)
            attractor_right = forcing_to_attractors[upper_bound][0]
        #  Check that the stability range is within the search region
        assert min_forcing <= lower_bound, lower_bound
        assert np.isnan(upper_bound) or (lower_bound < upper_bound <= max_forcing), upper_bound
    else:
        #  Stability ranges in the monostable case
        upper_bound, lower_bound = np.nan, np.nan
        attractor_left, attractor_right = np.array([np.nan]), np.array([np.nan])

    stability_forcing_range = lower_bound, upper_bound
    stability_state_range = attractor_left, attractor_right
    return stability_forcing_range, stability_state_range


class StabilityRangeError(ValueError):
    pass


def find_lower_bound(forcing_to_attractors: dict[float, list[np.ndarray]],
                     forcing_without_bistability: float, forcing_with_bistability: float) -> float:
    """
    Find the largest forcing_without_bistability below the bistable range
    For the initial call to this recursive function, we must have
    forcing_without_bistability < forcing_with_bistability
    This algorithm is roughly equivalent to a "binary search algorithm"
    """
    mean_forcing = float((forcing_without_bistability + forcing_with_bistability) // 2)
    if mean_forcing != forcing_without_bistability:
        #  we test the bistability of the mean_forcing and iterate the search function depending on the result
        if is_bistable(forcing_to_attractors[mean_forcing]):
            return find_lower_bound(forcing_to_attractors, forcing_without_bistability, mean_forcing)
        else:
            return find_lower_bound(forcing_to_attractors, mean_forcing, forcing_with_bistability)
    else:
        return forcing_without_bistability


def find_upper_bound(forcing_to_attractors: dict[float, list[np.ndarray]],
                     forcing_with_bistability: float, forcing_without_bistability: float) -> float:
    """
    Find the lowest forcing_without_bistability above the bistable range
    For the initial call to this recursive function, we must have
    forcing_with_bistability < forcing_without_bistability
    This algorithm is roughly equivalent to a "binary search algorithm"
    """
    mean_forcing = float((forcing_with_bistability + forcing_without_bistability) // 2)
    if mean_forcing + 1 != forcing_without_bistability:
        #  we test the bistability of the mean_forcing and iterate the search function depending on the result
        if is_bistable(forcing_to_attractors[mean_forcing]):
            return find_upper_bound(forcing_to_attractors, mean_forcing, forcing_without_bistability)
        else:
            return find_upper_bound(forcing_to_attractors, forcing_with_bistability, mean_forcing)
    else:
        if not is_bistable(forcing_to_attractors[mean_forcing]):
            forcing_without_bistability = mean_forcing
        return forcing_without_bistability
