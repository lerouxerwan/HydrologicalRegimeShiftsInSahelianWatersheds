import numpy as np
import pytest
from matplotlib import pyplot as plt

from calibration.calibration import Calibration
from calibration.calibration_visualisation import _plot_trajectory_ensemble
from calibration.dynamical_model.one_state.tiphyc_annual import DynamicalModelTipHycAnnual
from calibration.dynamical_model.two_states.wendling_2019 import DynamicalModelWendling2019
from calibration.forcing_function.rain.hombori_rain_forcing_function import \
    HomboriRainForcingFunction
from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction, \
    RainSimuForcingDebiased
from calibration.observation_constraint.vegetation.ortonde_vegetation_constraint import OrtondeVegetationConstraint
from calibration.observation_constraint.runoff.runoff_coefficient_constraint import \
    RunoffCoefficientObservationConstraint
from simulation.debiasing_function.annual.cdft_annual import CdftAnnual1


def test_calibration_wendling_2019():
    forcing_function = HomboriRainForcingFunction()
    observation_constraint = OrtondeVegetationConstraint()
    dynamical_model_type = DynamicalModelWendling2019
    run_calibration_functions(forcing_function, observation_constraint, dynamical_model_type)


@pytest.fixture
def watershed_name():
    return 'Dargol_Kakassi'

def test_calibration_tiphyc_annual(watershed_name):
    forcing_function = RainObsForcingFunction(watershed_name)
    observation_constraint = RunoffCoefficientObservationConstraint(watershed_name)
    dynamical_model_type = DynamicalModelTipHycAnnual
    run_calibration_functions(forcing_function, observation_constraint, dynamical_model_type)


nb_samples = 4
ensemble_size = 2


def run_calibration_functions(forcing_function, observation_constraint, dynamical_model_type):
    dynamical_model = dynamical_model_type(forcing_function)
    calibration = Calibration(observation_constraint, forcing_function,
                              dynamical_model,
                              nb_samples, ensemble_size)
    _plot_trajectory_ensemble(calibration, plt.gca())
    assert len(calibration.solve_data[0]) == ensemble_size
    calibration.save_calibration()
    calibration.load_calibration()
    #  Instantiate a calibration with an ensemble size larger than the sample size
    with pytest.raises(AssertionError):
        _ = Calibration(observation_constraint, forcing_function,
                        dynamical_model,
                        nb_samples - 1, nb_samples)
    # Try to load a calibration with a larger ensemble size
    with pytest.raises(AssertionError):
        _ = Calibration(observation_constraint, forcing_function,
                        dynamical_model,
                        nb_samples, ensemble_size + 1, loading_calibration=True)
    # Try to load a calibration with a smaller sample size
    with pytest.raises(AssertionError):
        _ = Calibration(observation_constraint, forcing_function,
                        dynamical_model,
                        nb_samples - 1, ensemble_size, loading_calibration=True)
    # Try to load a calibration with a larger sample size
    with pytest.raises(AssertionError):
        _ = Calibration(observation_constraint, forcing_function,
                        dynamical_model,
                        nb_samples + 1, ensemble_size, loading_calibration=True)
    # Try to load a calibration with a larger ensemble size
    with pytest.raises(AssertionError):
        _ = Calibration(observation_constraint, forcing_function,
                        dynamical_model,
                        nb_samples, ensemble_size + 1, loading_calibration=True)
    #  Try to load a calibration with a smaller ensemble size
    calibration_small = Calibration(observation_constraint, forcing_function,
                                    dynamical_model,
                                    nb_samples, ensemble_size - 1, loading_calibration=True)
    assert len(calibration_small.solve_data[0]) == ensemble_size - 1
    assert_equal_values(calibration, calibration_small)
    #  Remove data
    calibration.path_manager.remove_folder()
    calibration_small.path_manager.remove_folder()


def assert_not_equal_state(calibration1: Calibration, calibration2: Calibration, year):
    assert calibration1.initial_year == calibration2.initial_year
    index = calibration1.get_index_time(year)
    ensemble_size = min(calibration1.ensemble_size, calibration2.ensemble_size)
    for ensemble_id in range(ensemble_size):
        state_vector1 = calibration1.ensemble_id_to_state_vectors[ensemble_id][index]
        state_vector2 = calibration2.ensemble_id_to_state_vectors[ensemble_id][index]
        np.testing.assert_raises(AssertionError, np.testing.assert_array_equal, state_vector1, state_vector2)


def assert_equal_values(calibration1: Calibration, calibration2: Calibration, equal_error=True, final_year=None):
    assert calibration1.initial_year == calibration2.initial_year
    if final_year is None:
        last_idx = len(calibration1.forcing_function.years)
    else:
        last_idx = calibration1.get_index_time(final_year)
    for ensemble_id in min(calibration2.ensemble_ids, calibration1.ensemble_ids):
        #  Compare states
        state_vectors1 = calibration2.ensemble_id_to_state_vectors[ensemble_id][:last_idx]
        state_vectors2 = calibration1.ensemble_id_to_state_vectors[ensemble_id][:last_idx]
        np.testing.assert_almost_equal(state_vectors1, state_vectors2)
        #  Compare params
        params1 = calibration2.ensemble_id_to_params[ensemble_id]
        params2 = calibration1.ensemble_id_to_params[ensemble_id]
        for key, value in params1.items():
            np.testing.assert_almost_equal(value, params2[key])
        # Compare errors
        error2 = calibration2.ensemble_id_to_error[ensemble_id]
        error1 = calibration1.ensemble_id_to_error[ensemble_id]
        if equal_error:
            np.testing.assert_almost_equal(error2, error1)


def test_load_calibration_and_apply_other_forcing():
    watershed_name = 'Dargol_Kakassi'
    forcing_function = RainObsForcingFunction(watershed_name)
    observation_constraint = RunoffCoefficientObservationConstraint(watershed_name)
    dynamical_model_type = DynamicalModelTipHycAnnual
    calibration = Calibration(observation_constraint, forcing_function,
                              dynamical_model_type(forcing_function),
                              nb_samples, ensemble_size)
    calibration.save_calibration()
    #  Load other calibration but solve states with another forcing
    other_forcing_function = RainSimuForcingDebiased('Dargol_Kakassi','IPSL-CM6A-LR', 'historical', 'r2i1p1f1',
                                                     CdftAnnual1)
    other_calibration = Calibration(observation_constraint, other_forcing_function,
                                    dynamical_model_type(other_forcing_function),
                                    nb_samples, ensemble_size, loading_calibration=True)
    with pytest.raises(AssertionError):
        assert_equal_values(calibration, other_calibration, equal_error=False)
    # Load with the forcing after the year 1991
    _ = Calibration(observation_constraint, other_forcing_function,
                    dynamical_model_type(other_forcing_function),
                    nb_samples, ensemble_size, loading_calibration=True,
                    initial_year_for_loading=1990)
    assert len(calibration.times) > len(other_calibration.times)
    for year in [2000, 2007, 2014]:
        assert_not_equal_state(calibration, other_calibration, year=year)
    #  Remove file
    calibration.path_manager.remove_folder()
    other_calibration.path_manager.remove_folder()
#
