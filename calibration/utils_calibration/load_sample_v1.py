import numpy as np
import pandas as pd
from pandarallel import pandarallel
from scipy.stats.qmc import LatinHypercube

from bifurcation.bifurcation_data.degenerate_functions import compute_is_degenerate
from calibration.dynamical_model.dynamical_model import DynamicalModel
from calibration.dynamical_model.one_state.tiphyc_annual import DynamicalModelTipHycAnnual
from calibration.dynamical_model.two_states.wendling_2019 import DynamicalModelWendling2019
from calibration.forcing_function.forcing_function import ForcingFunction
from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction
from calibration.observation_constraint.observation_constraint import ObservationConstraint
from calibration.utils_calibration.sampling import Sampling
from calibration.utils_calibration.solve import SolverMethod
from utils.utils_log import log_info
from utils.utils_multiprocessing import NB_CORES
from utils.utils_run import random_seed


def load_sample_parameters(dynamical_model: DynamicalModel, nb_samples: int, initial_year: int = None,
                           initial_forcings: dict[str, float] = None,
                           observation_constraint: ObservationConstraint = None,
                           sampling: Sampling = Sampling.V1,
                           solver_method: SolverMethod = SolverMethod.RK45) -> np.ndarray:
    """Sample parameters using a LatinHypercube
    Eliminate samples that do not fulfill the desired constraint, e.g. a valid value for the initial state
    :return: A matrix where each row correspond to a vector of parameters"""
    assert sampling is Sampling.V1
    assert isinstance(nb_samples, int) and nb_samples > 0
    log_info(f'Sample {nb_samples} parameters')
    #  Insert the columns for the random parameters
    if len(dynamical_model.parameter_name_to_range) == 0:
        # Only constant columns
        df = pd.DataFrame()
        for (parameter_name, value) in enumerate(dynamical_model.parameter_name_to_value.items()):
            df[parameter_name] = [value] * nb_samples
    else:
        samples_found = False
        df = None
        nb_iterations = 0
        max_nb_iterations = 10
        while (not samples_found) and (nb_iterations < max_nb_iterations):
            log_info(f'start iteration {nb_iterations + 1} / {max_nb_iterations} for sampling')
            df = get_df_random_parameters(dynamical_model, nb_samples)
            #   Add constant columns
            for parameter_name, value in dynamical_model.parameter_name_to_value.items():
                df[parameter_name] = value
            #  Eliminate the samples that do not meet the desired constraints
            ind = check_constraints_on_sampled_parameters(dynamical_model, df, initial_year,
                                                          initial_forcings, observation_constraint, solver_method)
            df = df.loc[ind]
            #  Check that we have enough samples
            samples_found = len(df) >= nb_samples
            nb_iterations += 1
        if not samples_found:
            raise RuntimeError('We did not find samples that meet the constraint')

    #  Keep only nb_samples
    df = df.iloc[:nb_samples]
    #  Reorder the columns in the same order as parameter_names
    df = df.loc[:, dynamical_model.parameter_names]
    assert list(df.columns) == dynamical_model.parameter_names
    assert not df.isnull().any(axis=1).any(axis=0)
    log_info('Terminate sampling')
    return df.values


def get_multiplicative_factor(forcing_function: ForcingFunction, nb_samples: int) -> int:
    sahel_watershed_names = {'Dargol_Kakassi', 'Sirba_GarbeKourou', 'Gorouol_Alcongui', 'Nakanbe_Wayen'}
    if (nb_samples == 1000000) and isinstance(forcing_function, RainObsForcingFunction):
        if forcing_function.watershed_name in sahel_watershed_names:
            # a factor equals to 2 is enough for the Sahel watersheds
            multiplicative_factor = 2
        else:
            # a large multiplicative factor was needed for Pendjari (5 at least) and for Oueme Beterou
            multiplicative_factor = 2
    else:
        multiplicative_factor = 10
    return multiplicative_factor


def get_df_random_parameters(dynamical_model: DynamicalModel, nb_samples: int) -> pd.DataFrame:
    latin_hypercube = LatinHypercube(len(dynamical_model.parameter_name_to_range), seed=random_seed)
    #  We sample more than necessary to ensure that we have enough samples to respect potential constraints
    multiplicative_factor = get_multiplicative_factor(dynamical_model.forcing_function, nb_samples)
    log_info(f'Multiplicative factor for sampling {multiplicative_factor}')
    samples = latin_hypercube.random(nb_samples * multiplicative_factor)
    df_random_parameters = pd.DataFrame(data=samples, columns=list(dynamical_model.parameter_name_to_range.keys()))
    #  Sampling ranges
    scale_and_shift = [(b - a, a) for a, b in dynamical_model.parameter_name_to_range.values()]
    # Scale and shift the samples to the appropriate range
    for i, (scale, shift) in enumerate(scale_and_shift):
        df_random_parameters.iloc[:, i] *= scale
        df_random_parameters.iloc[:, i] += shift
    return df_random_parameters


def check_constraints_on_sampled_parameters(dynamical_model: DynamicalModel, df: pd.DataFrame, initial_year: int,
                                            initial_forcings: dict[str, float],
                                            observation_constraint: ObservationConstraint,
                                            solver_method: SolverMethod) -> pd.Series:
    """Assess that the sampled parameters meet some constraints.
    By default, this function does not impose any observation_constraint.
    :return: ind: An pandas Series where the index are the same as df,
    and the values are boolean stating if the observation_constraint is respected."""
    # Activate pandarallel
    pandarallel.initialize(nb_workers=NB_CORES)
    # Compute specific constraints
    specific_ind = specific_constraint_on_samples_parameters(dynamical_model, df, solver_method)
    # Compute common constraints
    common_ind = common_constraint_on_sample_parameters(dynamical_model, df, initial_forcings, initial_year,
                                                        observation_constraint)
    # Return the combination of the specific and general constraint
    return common_ind & specific_ind


def common_constraint_on_sample_parameters(dynamical_model: DynamicalModel, df: pd.DataFrame,
                                           initial_forcings: dict[str, float], initial_year: int,
                                           observation_constraint: ObservationConstraint) -> pd.Series:
    if (initial_year is None) and (initial_forcings is None) and (observation_constraint is None):
        common_ind = pd.Series(index=df.index, data=True)
    else:
        def initial_state_is_without_nan(params_series):
            params = params_series.to_dict()
            for parameter_name in dynamical_model.parameter_names:
                assert parameter_name in params
            initial_state = dynamical_model.get_state(initial_forcings, initial_year, params, observation_constraint)
            return not np.isnan(initial_state).any()

        common_ind = df.parallel_apply(initial_state_is_without_nan, axis=1)
    return common_ind


def specific_constraint_on_samples_parameters(dynamical_model: DynamicalModel, df: pd.DataFrame, solver_method: SolverMethod) -> pd.Series:
    """Assess that the sampled parameters meet some constraints.
    By default, this function does not impose any observation_constraint.
    :return: ind: An pandas Series where the index are the same as df,
    and the values are boolean stating if the observation_constraint is respected."""
    if isinstance(dynamical_model, DynamicalModelWendling2019):
        #  They assume that r_r <= r_g
        # (growth rate recolonization of bare areas is slower than growth rate in herbaceous areas
        ind_respect_the_assumption = df.loc[:, 'r_r'] <= df.loc[:, 'r_g']
        df = df.loc[ind_respect_the_assumption]
        #  They assume that zero is out of the sampling range for 'r_g', 'r_r', 'r_d'
        ind_strictly_positive_r_values = ~(df.loc[:, ['r_g', 'r_r', 'r_d']] == 0).any(axis=1)
        return ind_strictly_positive_r_values & ind_respect_the_assumption
    elif isinstance(dynamical_model, DynamicalModelTipHycAnnual):
        def is_not_degenerate(params_series):
            params = params_series.to_dict()
            return not compute_is_degenerate(dynamical_model, params, solver_method)

        return df.parallel_apply(is_not_degenerate, axis=1)
    else:
        return pd.Series(index=df.index, data=True)
