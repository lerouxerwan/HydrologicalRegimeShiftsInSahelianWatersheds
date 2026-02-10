import numpy as np

from bifurcation.bifurcation import Bifurcation
from projects.paper_model.utils_paper_model import sahel_watershed_names, get_calibration
from utils.utils_log import log_info


def average_rank_monostable_ensemble_members(fast: bool):
    for watershed_name in sahel_watershed_names:
        calibration = get_calibration(watershed_name, fast)
        bifurcation = Bifurcation(calibration, max_forcing=4000.)
        if bifurcation.monostable_ensemble_ids:
            print(watershed_name, bifurcation.monostable_ensemble_ids)
            min_rank = np.min(bifurcation.monostable_ensemble_ids) + 1
            mean_rank = np.mean(bifurcation.monostable_ensemble_ids) + 1
            max_rank = np.max(bifurcation.monostable_ensemble_ids) + 1
            log_info(f'Average (Min, %ax) rank for monostable parameterization of {watershed_name}: '
                     f'{mean_rank} ({min_rank}, {max_rank})')
            log_info(f'Average monostable errors= {np.mean(bifurcation.monostable_errors)}')
            log_info(f'Average bistable errors= {np.mean(bifurcation.bistable_errors)}')

if __name__ == '__main__':
    average_rank_monostable_ensemble_members(fast=False)