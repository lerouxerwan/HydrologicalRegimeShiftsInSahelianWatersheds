import math
import os
import os.path as op

import numpy as np
import pandas as pd

from continuation.get_continuation import get_continuation
from utils.utils_path.utils_path import CONTINUATION_INTERPOLATED_DATA_PATH


def get_continuation_interpolated(watershed_name: str, ensemble_ids: list[int], min_forcing: float, max_forcing: float):
    ensemble_id_to_u_path_and_p_path  = get_continuation(watershed_name, ensemble_ids, min_forcing, max_forcing)

    # Create folder if needed
    folder = op.join(CONTINUATION_INTERPOLATED_DATA_PATH, f'{int(min_forcing)}_{int(max_forcing)}', watershed_name)
    if not op.exists(folder):
        os.makedirs(folder)

    # Load or compute continuation interpolated
    for ensemble_id in ensemble_ids:
        csv_filepath = op.join(folder, f'{ensemble_id}.csv')
        if op.exists(csv_filepath):
            # print(f'Load ensemble_id={ensemble_id}')
            # Load continuation interpolated
            df = pd.read_csv(csv_filepath, index_col=0)
            u_path_interpolated, p_path_interpolated = df['u_interpolated'].values, df['p_interpolated'].values
        else:
            # print(f'Compute ensemble_id={ensemble_id}')
            # Compute continuation interpolated
            u_path, p_path = ensemble_id_to_u_path_and_p_path[ensemble_id]
            u_path_interpolated, p_path_interpolated = compute_continuation_interpolated(u_path, p_path, min_forcing, max_forcing)
            # Save continuation
            pd.DataFrame({'u_interpolated': u_path_interpolated, 'p_interpolated': p_path_interpolated}).to_csv(csv_filepath)
        p_path_interpolated = [float(p) for p in p_path_interpolated]
        ensemble_id_to_u_path_and_p_path[ensemble_id] = (u_path_interpolated, p_path_interpolated)
    return ensemble_id_to_u_path_and_p_path

def compute_continuation_interpolated(u_path, p_path, min_forcing, max_forcing):
    """Run one linear interpolation for each forcing"""
    n = len(p_path)
    floor_list = [math.floor(p) for p in p_path]
    ceil_list = [math.ceil(p) for p in p_path]
    start_index_list = [0] + [i+1 for i, c in enumerate(ceil_list[:-1]) if ceil_list[i+1] != c]
    results = []
    for start_index in start_index_list:
        forcing = ceil_list[start_index]
        if min_forcing <= forcing <= max_forcing:
            indexes = [start_index]
            i = 1
            while ceil_list[start_index + i] == forcing:
                indexes.append(start_index + i)
                i += 1
            while (start_index + i < n) and (floor_list[start_index + i] == forcing):
                indexes.append(start_index + i)
                i += 1
            interpolated_value = np.interp([forcing], p_path[indexes], u_path[indexes])[0]
            results.append((interpolated_value, forcing))
    interpolated_value_list, forcing_list = zip(*results)
    return interpolated_value_list, forcing_list





