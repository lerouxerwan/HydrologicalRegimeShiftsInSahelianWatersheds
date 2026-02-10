import math
from collections import OrderedDict

import numpy as np

from bifurcation.bifurcation_data.attractor_functions import get_attractors
from bifurcation.bifurcation_data.bistability_functions import is_bistable
from calibration.dynamical_model.dynamical_model import DynamicalModel
from calibration.utils_calibration.solve import SolverMethod


def compute_stability_detection(dynamical_model: DynamicalModel, params: dict[str, float],
                                min_forcing: float, max_forcing: float, solver_method: SolverMethod):
    """
    By default, we consider that a dynamical model is bistable,
    if some bistability is detected for a forcing between min_forcing and max_forcing
    In this case, we return the value of the forcing where we find the bistability
    Otherwise, if no bistable value if found, the dynamical model is monostable,
    in this case, we return a dictionary that maps each forcing to its attractor
    """
    assert isinstance(min_forcing, float) and min_forcing.is_integer()
    assert isinstance(max_forcing, float) and max_forcing.is_integer()
    max_power = math.ceil(np.log2(int(max_forcing)))
    stop = math.pow(2, max_power)
    num = 2
    forcing_to_attractors = dict()
    for power in range(max_power):
        num += int(math.pow(2, power))
        forcings = np.linspace(0, stop, num=num)[1::2]
        for forcing in forcings:
            if min_forcing < forcing < max_forcing:
                attractors = get_attractors(dynamical_model, params, forcing, solver_method)
                if is_bistable(attractors):
                    return forcing
                else:
                    forcing_to_attractors[forcing] = attractors

    #  If only the limit forcing (min_forcing and max_forcing) are bistable,
    #  then we consider the model as monostable and we keep the lower branch.
    for forcing in [min_forcing, max_forcing]:
        attractors = get_attractors(dynamical_model, params, forcing, solver_method)
        forcing_to_attractors[forcing] = attractors[:1]

    forcings = np.arange(min_forcing, max_forcing + 1)
    assert set(forcings) == set(forcing_to_attractors.keys())
    ordered_dict_forcing_to_attractor = OrderedDict()
    for forcing in forcings:
        ordered_dict_forcing_to_attractor[float(forcing)] = forcing_to_attractors[forcing][0]
    return ordered_dict_forcing_to_attractor
