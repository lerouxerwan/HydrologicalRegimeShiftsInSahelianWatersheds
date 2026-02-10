import os
import os.path as op
from collections import OrderedDict
from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from calibration.dynamical_model.dynamical_model import DynamicalModel
from calibration.forcing_function.rain.rain_forcing_function import RAIN_STR
from continuation.pycont.continuation import pseudoArclengthContinuationOneDirection
from projects.paper_model.utils_paper_model import get_calibration
from utils.utils_multiprocessing import parallelize
from utils.utils_path.utils_path import CONTINUATION_DATA_PATH


def get_continuation(watershed_name: str, ensemble_ids: list[int], min_forcing: float, max_forcing: float):
    folder = op.join(CONTINUATION_DATA_PATH, f'{int(min_forcing)}_{int(max_forcing)}', watershed_name)
    if not op.exists(folder):
        os.makedirs(folder)
    calibration = None
    ensemble_id_to_u_path_and_p_path = OrderedDict()
    for ensemble_id in ensemble_ids:
        csv_filepath = op.join(folder, f'{ensemble_id}.csv')
        if op.exists(csv_filepath):
            # print(f'Load ensemble_id={ensemble_id}')
            # Load continuation
            df = pd.read_csv(csv_filepath, index_col=0)
            u_path, p_path = df['u'].values, df['p'].values
        else:
            # print(f'Compute ensemble_id={ensemble_id}')
            # Compute continuation
            if calibration is None:
                calibration = get_calibration(watershed_name)
            params = calibration.ensemble_id_to_params[ensemble_id]
            u_path, p_path = compute_continuation(calibration.dynamical_model, params, min_forcing, max_forcing)
            u_path, p_path = np.array(u_path), np.array(p_path)
            # Save continuation
            pd.DataFrame({'u': u_path, 'p': p_path}).to_csv(csv_filepath)
        ensemble_id_to_u_path_and_p_path[ensemble_id] = (u_path, p_path)
    return ensemble_id_to_u_path_and_p_path


def get_continuation_parallel(watershed_name: str, ensemble_ids: list[int], min_forcing: float, max_forcing: float,
                              parallel: bool=True):
    return Continuation(watershed_name, ensemble_ids, min_forcing, max_forcing, parallel).compute_all()

@dataclass
class Continuation:
    watershed_name: str
    ensemble_ids: list[int]
    min_forcing: float
    max_forcing: float
    parallel: bool

    def __post_init__(self):
        self.folder = op.join(CONTINUATION_DATA_PATH, f'{int(self.min_forcing)}_{int(self.max_forcing)}', self.watershed_name)
        if not op.exists(self.folder):
            os.makedirs(self.folder)
        self.calibration = get_calibration(self.watershed_name)


    def compute_all(self):
        paths = parallelize(self.compute_one, self.ensemble_ids, parallel=self.parallel)
        return dict(zip(self.ensemble_ids, paths))

    def compute_one(self, ensemble_id):
        csv_filepath = op.join(self.folder, f'{ensemble_id}.csv')
        if op.exists(csv_filepath):
            print(f'Load ensemble_id={ensemble_id}')
            # Load continuation
            df = pd.read_csv(csv_filepath, index_col=0)
            u_path, p_path = df['u'].values, df['p'].values
        else:
            print(f'Compute ensemble_id={ensemble_id}')
            params = self.calibration.ensemble_id_to_params[ensemble_id]
            u_path, p_path = compute_continuation(self.calibration.dynamical_model, params, self.min_forcing, self.max_forcing)
            u_path, p_path = np.array(u_path), np.array(p_path)
            # Save continuation
            pd.DataFrame({'u': u_path, 'p': p_path}).to_csv(csv_filepath)
        return u_path, p_path



def compute_continuation(dynamical_model: DynamicalModel, params: dict[str, float],
                         min_forcing: float, max_forcing: float):
    # Create a custom 'derivative' function
    def derivative(states: np.ndarray[float], forcing: float):
        states = dict(zip(dynamical_model.state_names, states))
        return np.array([dynamical_model.derivative(states, {RAIN_STR: forcing}, params)])
    return _compute_continuation(derivative, min_forcing, max_forcing)


def _compute_continuation(derivative: Callable, min_forcing: float, max_forcing: float):
    # Run continuation to obtain u_path (path of states) and p_path (path of the corresponding forcing)
    # Loop while the max_forcing is not reached
    initial_value = 0.01
    u_path, p_path = [initial_value], [max(0.1, min_forcing - 1)]
    while p_path[-1] < max_forcing:
        u0, p0 = u_path[-1], p_path[-1]
        u_path, p_path = u_path[:-1], p_path[:-1]
        epsilon = 1e-5
        new_u_path, new_p_path = pseudoArclengthContinuationOneDirection(derivative, u0, p0,
                                                                 ds_min=0.0000001, ds_max=1., ds_0=0.2,
                                                                 N=10000, p_max=max_forcing,
                                                                         epsilon=epsilon)
        # Handle special case
        if new_p_path[-1] < epsilon:
            index_max_p = np.argmax(new_p_path)
            index_to_cut = index_max_p - 100 # Cut the trajectory several steps before it reaches its max p
            new_u_path = new_u_path[:index_to_cut] + [np.array([initial_value])]
            new_p_path = new_p_path[:index_to_cut+1]

        u_path.extend(list(np.array(new_u_path).flatten()))
        p_path.extend(list(np.array(new_p_path).flatten()))
    return u_path, p_path



