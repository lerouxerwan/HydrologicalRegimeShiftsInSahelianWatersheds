from collections import OrderedDict

import numpy as np

from bifurcation.bifurcation_data.stability_range_functions import compute_stability_ranges
from continuation.get_continuation_interpolated import get_continuation_interpolated


def get_bifurcation_attributes(watershed_name: str, ensemble_id: int, min_forcing: float, max_forcing: float):
    interpolated_value_list, forcing_list = get_continuation_interpolated(watershed_name, [ensemble_id],
                                                                          min_forcing, max_forcing)[ensemble_id]
    forcing_list = [float(forcing) for forcing in forcing_list]
    interpolated_value_list = [np.array([value]) for value in interpolated_value_list]
    forcing_to_attractors = OrderedDict()
    for forcing in forcing_list:
        forcing_to_attractors[forcing] = []
    forcing_to_repulsor = OrderedDict()
    previous_forcing = 0
    for forcing, stable_state_value in zip(forcing_list, interpolated_value_list):
        if previous_forcing < forcing:
            forcing_to_attractors[forcing].append(stable_state_value)
        else:
            forcing_to_repulsor[forcing] = stable_state_value[0]
        previous_forcing = forcing
    # Compute stability detection (for a monostable we return a dictionary mapping forcing to attractor, for bistable we return the first bistable forcing)
    stability_detection = OrderedDict()
    for forcing, attractors in forcing_to_attractors.items():
        if len(attractors) == 1:
            stability_detection[forcing] = attractors[0]
        else:
            stability_detection = forcing
            break
    # Compute stability ranges
    stability_ranges = compute_stability_ranges(forcing_to_attractors, stability_detection, min_forcing, max_forcing)

    return forcing_to_attractors, forcing_to_repulsor, stability_ranges, stability_detection

