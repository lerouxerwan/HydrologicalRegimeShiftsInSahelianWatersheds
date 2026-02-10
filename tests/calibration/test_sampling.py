from random import choice

import numpy as np
import pytest

from calibration.dynamical_model.one_state.tiphyc_annual import DynamicalModelTipHycAnnual
from calibration.dynamical_model.two_states.wendling_2019 import DynamicalModelWendling2019
from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction
from calibration.observation_constraint.runoff.runoff_coefficient_constraint import RunoffCoefficientObservationConstraint
from bifurcation.bifurcation_data.degenerate_functions import compute_is_degenerate
from calibration.utils_calibration.load_sample_v1 import load_sample_parameters
from calibration.utils_calibration.convert import get_time_from_year
from calibration.utils_calibration.solve import SolverMethod


def test_random_seed_for_sampling():
    forcing_function = RainObsForcingFunction('Dargol_Kakassi')
    dynamical_model = DynamicalModelWendling2019(forcing_function)
    params_vector_list = load_sample_parameters(dynamical_model, nb_samples=10)
    params_concatenated = np.concatenate(params_vector_list, axis=0)
    assert np.sum(params_concatenated) == 6003.539852250736
    dynamical_model = DynamicalModelTipHycAnnual(forcing_function)
    params_vector_list = load_sample_parameters(dynamical_model, nb_samples=10)
    params_concatenated = np.concatenate(params_vector_list, axis=0)
    assert np.sum(params_concatenated) == 12891.081795895905


@pytest.fixture
def solver_method():
    return SolverMethod.RK45

    
def test_initial_state_for_tiphyc_annual(solver_method: SolverMethod):
    watershed_name = choice(['Dargol_Kakassi', 'Sirba_GarbeKourou', 'Gorouol_Alcongui', 'Tapoa_CampementW',
                           'Nakanbe_Wayen', 'Sota_Couberi', 'Pendjari_Porga', 'Oueme_Beterou'])
    nb_samples = 10
    forcing_function = RainObsForcingFunction(watershed_name)
    observation_constraint = RunoffCoefficientObservationConstraint(watershed_name)
    dynamical_model = DynamicalModelTipHycAnnual(forcing_function)
    initial_year = min(set(forcing_function.years).intersection(set(observation_constraint.years)))
    initial_forcings = forcing_function.get_forcings(get_time_from_year(initial_year))
    params_vector_list = load_sample_parameters(dynamical_model, nb_samples, initial_year, initial_forcings,
                                                observation_constraint)
    params_list = [dynamical_model.get_params(params_vector) for params_vector in params_vector_list]
    #  Count the number of initial state with nan
    count = 0
    for params in params_list:
        initial_state = dynamical_model.get_state(initial_forcings, initial_year, params, observation_constraint)
        if np.isnan(initial_state).all():
            count += 1
    assert count == 0
    #  Count the number of degenerate cases
    count = 0
    for params in params_list:
        is_degenerate = compute_is_degenerate(dynamical_model, params, solver_method)
        if is_degenerate:
            count += 1
    assert count == 0
