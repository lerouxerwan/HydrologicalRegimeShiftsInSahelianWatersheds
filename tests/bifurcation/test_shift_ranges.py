import numpy as np
import pytest

from bifurcation.bifurcation import Bifurcation
from bifurcation.shift_range.shift_range_functions import compute_shift_range
from calibration.calibration import Calibration
from calibration.dynamical_model.one_state.tiphyc_annual import DynamicalModelTipHycAnnual
from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction
from calibration.observation_constraint.runoff.runoff_coefficient_constraint import \
    RunoffCoefficientObservationConstraint


@pytest.mark.long
def test_ranges_specific_case():
    ensemble_size, nb_samples = (1000, 1000000)
    watershed_name = 'Dargol_Kakassi'
    final_year_for_constraint = 2015
    observation_constraint = RunoffCoefficientObservationConstraint(watershed_name, final_year_for_constraint)
    forcing_function = RainObsForcingFunction(watershed_name)
    dynamical_model = DynamicalModelTipHycAnnual(forcing_function)
    calibration = Calibration(observation_constraint, forcing_function,
                              dynamical_model,
                              nb_samples, ensemble_size, loading_calibration=True)
    bifurcation = Bifurcation(calibration)
    ensemble_id = 313
    bifurcation_data = bifurcation.ensemble_id_to_bifurcation_data[ensemble_id]
    stability_ranges = bifurcation_data.stability_ranges
    assert stability_ranges[0] == (812.0, 2000.0)
    np.testing.assert_almost_equal(stability_ranges[1][0][0], 0.02859693, decimal=2)
    np.testing.assert_almost_equal(stability_ranges[1][1][0], 0.71487596, decimal=2)
    shift_range = compute_shift_range(bifurcation_data.is_bistable, stability_ranges,
                                       bifurcation_data.forcing_to_attractors,
                                       bifurcation_data.min_forcing, bifurcation_data.max_forcing)
    assert (shift_range.forcing_lower_state, shift_range.forcing_upper_state) == (1999.0, 813.0)
    np.testing.assert_almost_equal(shift_range.lower_state_value, 0.08037702, decimal=2)
    np.testing.assert_almost_equal(shift_range.upper_state_value, 0.29680047, decimal=2)
