from typing import Generator

import pandas as pd
from scipy.stats._qmc import LatinHypercube

from calibration.dynamical_model.dynamical_model import DynamicalModel
from utils.utils_run import random_seed


def params_sampled(dynamical_model: DynamicalModel, nb_samples: int) -> Generator[dict[str, float], None, None]:
    df_parameters = get_df_parameters_sampled(dynamical_model, nb_samples)
    for _, series in df_parameters.iterrows():
        yield series.to_dict()


def get_df_parameters_sampled(dynamical_model: DynamicalModel, nb_samples: int) -> pd.DataFrame:
    df_parameters = _get_df_random_parameters_sampled(dynamical_model, nb_samples)
    #   Add constant columns
    for parameter_name, value in dynamical_model.parameter_name_to_value.items():
        df_parameters[parameter_name] = value
    #  Reorder the columns in the same order as parameter_names
    df_parameters = df_parameters.loc[:, dynamical_model.parameter_names]
    return df_parameters


def _get_df_random_parameters_sampled(dynamical_model: DynamicalModel, nb_samples: int) -> pd.DataFrame:
    latin_hypercube = LatinHypercube(len(dynamical_model.parameter_name_to_range), seed=random_seed)
    #  We sample 2 times more than necessary to ensure that we have enough samples to respect potential constraints
    samples = latin_hypercube.random(nb_samples * 2)
    df_random_parameters = pd.DataFrame(data=samples, columns=list(dynamical_model.parameter_name_to_range.keys()))
    #  Sampling ranges
    scale_and_shift = [(b - a, a) for a, b in dynamical_model.parameter_name_to_range.values()]
    # Scale and shift the samples to the appropriate range
    for i, (scale, shift) in enumerate(scale_and_shift):
        df_random_parameters.iloc[:, i] *= scale
        df_random_parameters.iloc[:, i] += shift
    return df_random_parameters
