import os.path as op

import pytest

from bifurcation.bifurcation import Bifurcation
from calibration.calibration import Calibration
from calibration.dynamical_model.one_state.tiphyc_annual import DynamicalModelTipHycAnnual
from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction
from calibration.observation_constraint.runoff.runoff_coefficient_constraint import \
    RunoffCoefficientObservationConstraint


def test_io_utils():
    calibration_of_reference = load_calibration_test_io(2)
    # Delete the csv if it already exists
    bifurcation = Bifurcation(calibration_of_reference, min_forcing=100., max_forcing=200.)
    filepath = bifurcation.path_manager.filepath_to_save
    if op.isfile(filepath):
        bifurcation.path_manager.remove_folder()
    assert not bifurcation.bifurcation_data_ensemble_has_been_saved
    # Create the csv
    _ = bifurcation.ensemble_id_to_bifurcation_data
    bifurcation_data_list_of_reference = bifurcation.bifurcation_data_list
    bifurcation._save_bifurcation_data_list(bifurcation_data_list_of_reference)
    assert bifurcation.bifurcation_data_ensemble_has_been_saved
    assert bifurcation_data_list_of_reference is not None
    # Load the csv with the same calibration
    bifurcation_data_list_loaded = bifurcation._load_bifurcation_data_list()
    assert all([s1 == s2 for s1, s2 in zip(bifurcation_data_list_of_reference, bifurcation_data_list_loaded)])
    calibration_of_reference.path_manager.remove_folder()
    # Load the csv with a calibration with a smaller ensemble size
    calibration = load_calibration_test_io(1)
    bifurcation.check_valid_sharing(calibration)
    calibration.path_manager.remove_folder()
    # Try to load the csv with a calibration with a larger ensemble size
    calibration = load_calibration_test_io(3)
    with pytest.raises(AssertionError):
        bifurcation.check_valid_sharing(calibration)
    calibration.path_manager.remove_folder()
    # Remove the csv
    bifurcation.path_manager.remove_folder()
    calibration.path_manager.remove_folder()


def load_calibration_test_io(ensemble_size):
    watershed_name = 'Dargol_Kakassi'
    forcing_function = RainObsForcingFunction(watershed_name)
    observation_constraint = RunoffCoefficientObservationConstraint(watershed_name)
    return Calibration(observation_constraint, forcing_function,
                       DynamicalModelTipHycAnnual(forcing_function),
                       3, ensemble_size)
