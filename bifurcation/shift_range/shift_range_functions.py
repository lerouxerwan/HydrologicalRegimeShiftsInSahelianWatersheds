import numpy as np

from bifurcation.shift_range.shift_range import ShiftRange


def compute_shift_range(is_bistable: bool, stability_ranges: tuple[tuple[float, float], tuple[np.ndarray, np.ndarray]],
                        forcing_to_attractors: dict[float, list[np.ndarray]], min_forcing: float, max_forcing: float) \
        -> ShiftRange:
    if is_bistable:
        return bistable_shift_range(stability_ranges, forcing_to_attractors, max_forcing)
    else:
        raise NotImplementedError


def bistable_shift_range(stability_ranges: tuple[tuple[float, float], tuple[np.ndarray, np.ndarray]],
                         forcing_to_attractors: dict[float, list[np.ndarray]], max_forcing: float) \
        -> ShiftRange:
    #  Compute the forcing/attractor at the end of the lower branch (inside the bistable range)
    upper_bound = stability_ranges[0][1]
    #  upper_bound is the first forcing after the bistability range, np.nan means that max_forcing is bistable
    #   in the case, where upper_bound is np.nan, we set the end of lower branch at max_forcing
    bistable_forcing_1 = max_forcing if np.isnan(upper_bound) else upper_bound - 1
    state1 = forcing_to_attractors[bistable_forcing_1][0]
    #  Compute the forcing/attractor at the start of the upper branch (inside the bistability range)
    bistable_forcing_2 = stability_ranges[0][0] + 1
    state2 = forcing_to_attractors[bistable_forcing_2][1]
    return _compute_shift_range(bistable_forcing_1, bistable_forcing_2, state1, state2)


def _compute_shift_range(forcing1: float, forcing2: float, state1: np.ndarray, state2: np.ndarray) -> ShiftRange:
    # Handle special case where the bistability range is of length 1
    if forcing1 + 1 == forcing2:
        forcing1, forcing2 = forcing1 + 0.5, forcing2 - 0.5
    #  Find the upper state and the lower state
    assert forcing1 >= forcing2
    if state1[0] < state2[0]:
        return ShiftRange(state1[0], state2[0], forcing1, forcing2)
    else:
        return ShiftRange(state2[0], state1[0], forcing2, forcing1)
