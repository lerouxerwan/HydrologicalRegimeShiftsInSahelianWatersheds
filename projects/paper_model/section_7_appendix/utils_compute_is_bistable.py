import numpy as np

from bifurcation.bifurcation import Bifurcation
from bifurcation.bifurcation_data.bifurcation_data import BifurcationData


def compute_percentage_bistable(bifurcation: Bifurcation, forcing: float) -> float:
    nb_bistable = 0
    for bifurcation_data in bifurcation.bifurcation_data_list:
        if compute_is_bistable_wrt_to_some_forcing(bifurcation_data, forcing):
            nb_bistable += 1
    return 100 * nb_bistable / len(bifurcation.bifurcation_data_list)


def compute_is_bistable_wrt_to_some_forcing(bifurcation_data: BifurcationData, forcing: float) -> bool:
    lower_bound, _ = bifurcation_data.stability_ranges[0]
    is_monostable = np.isnan(lower_bound) or (forcing <= lower_bound)
    is_bistable = not is_monostable
    return is_bistable
