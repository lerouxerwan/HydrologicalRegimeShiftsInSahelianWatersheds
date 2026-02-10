import numpy as np
import pytest

from bifurcation.bifurcation_data.attractor_functions import compute_forcing_to_attractors
from bifurcation.bifurcation_data.bistability_functions import compute_is_bistable
from bifurcation.bifurcation_data.stability_detection_function import compute_stability_detection
from bifurcation.bifurcation_data.stability_range_functions import compute_stability_ranges, StabilityRangeError
from calibration.dynamical_model.one_state.tiphyc_annual import DynamicalModelTipHycAnnual
from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction
from calibration.utils_calibration.solve import SolverMethod

watershed_name = 'Dargol_Kakassi'


@pytest.fixture
def dynamical_model():
    forcing_function = RainObsForcingFunction(watershed_name)
    return DynamicalModelTipHycAnnual(forcing_function)


@pytest.fixture
def solver_method():
    return SolverMethod.RK45


@pytest.mark.long
def test_special_case_stability_ranges(dynamical_model, solver_method):
    params = {'c_croiss': 0.8451058906852675, 'i_croiss': 625.6621806551991, 'c_max': 1.0, 'c_mort': 1.533422706725071,
              'i_mort': 123.2068786304384, 're': 0.0, 'mu_c': 0.0047732965945149605, 'p_ini': 55.684832487285256,
              'p_0max': 746.3882032470178, 'a': 1.5, 'b': 8.0, 'skc': 4.046077623193438, 'n_a': 1.028387282209664,
              'i_ta': 1962.473880622416, 'Ke_max': 0.9}
    min_forcing, max_forcing = 600., 2200.
    stability_detection = compute_stability_detection(dynamical_model, params, min_forcing, max_forcing)
    forcing_to_attractors = compute_forcing_to_attractors(dynamical_model, params, stability_detection, min_forcing,
                                                          max_forcing, solver_method)
    stability_ranges = compute_stability_ranges(forcing_to_attractors, stability_detection, min_forcing, max_forcing)
    assert stability_ranges[0] == (615.0, np.nan)
    np.testing.assert_almost_equal(stability_ranges[1][0][0], 0.01147388, decimal=2)
    min_forcing, max_forcing = 600., 650.
    stability_detection = compute_stability_detection(dynamical_model, params, min_forcing, max_forcing)
    stability_ranges = compute_stability_ranges(forcing_to_attractors, stability_detection, min_forcing, max_forcing)
    assert stability_ranges[0] == (615.0, np.nan)
    np.testing.assert_almost_equal(stability_ranges[1][0][0], 0.01147388, decimal=2)
    np.testing.assert_almost_equal(stability_ranges[1][1][0], np.nan)
    with pytest.raises(StabilityRangeError):
        min_forcing, max_forcing = 630., 2200.
        stability_detection = compute_stability_detection(dynamical_model, params, min_forcing, max_forcing)
        compute_stability_ranges(forcing_to_attractors, stability_detection, min_forcing, max_forcing)
    min_forcing, max_forcing = 2200., 2300.
    stability_detection = compute_stability_detection(dynamical_model, params, min_forcing, max_forcing)
    assert compute_is_bistable(stability_detection)
    np.testing.assert_almost_equal(stability_ranges[1][0][0], 0.011467007067741253, decimal=2)
    np.testing.assert_almost_equal(stability_ranges[1][1][0], np.nan, decimal=2)
