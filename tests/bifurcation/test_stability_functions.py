import numpy as np
import pytest

from bifurcation.bifurcation_data.attractor_functions import compute_forcing_to_attractors
from bifurcation.bifurcation_data.bifurcation_data import BifurcationData
from bifurcation.bifurcation_data.bistability_functions import compute_is_bistable
from bifurcation.bifurcation_data.repulsor_functions import compute_forcing_to_repulsor
from bifurcation.bifurcation_data.stability_detection_function import compute_stability_detection
from bifurcation.bifurcation_data.stability_range_functions import compute_stability_ranges
from calibration.dynamical_model.one_state.tiphyc_annual import DynamicalModelTipHycAnnual
from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction
from calibration.utils_calibration.solve import SolverMethod

watershed_name = 'Dargol_Kakassi'


@pytest.fixture
def dynamical_model():
    forcing_function = RainObsForcingFunction(watershed_name)
    return DynamicalModelTipHycAnnual(forcing_function)


@pytest.fixture
def forcing():
    return 500.


@pytest.fixture
def min_forcing():
    return 300.


@pytest.fixture
def max_forcing():
    return 400.


@pytest.fixture
def solver_method():
    return SolverMethod.RK45


def get_params_list():
    """Load one monostable and one bistable model"""
    return [{'c_croiss': 0.5749218667194288, 'i_croiss': 666.022427165532, 'c_max': 1.0, 'c_mort': 3.4739109380208664,
             'i_mort': 53.866255427273884, 're': 0.0, 'mu_c': 0.0039773961259999555, 'p_ini': 138.06247209769703,
             'p_0max': 617.203964196273, 'a': 1.5, 'b': 8.0, 'skc': 6.3316112279359125, 'n_a': 1.0496918216543205,
             'i_ta': 1464.082065269191, 'Ke_max': 0.9},
            {'c_croiss': 1.2253436897231211, 'i_croiss': 543.1327311487862, 'c_max': 1.0, 'c_mort': 1.4164921542573312,
             'i_mort': 137.13878744213963, 're': 0.0, 'mu_c': 0.00424562729437332, 'p_ini': 37.51515637792302,
             'p_0max': 738.5320312111666, 'a': 1.5, 'b': 8.0, 'skc': 8.951068784186447, 'n_a': 1.3644296784765872,
             'i_ta': 1680.4025447723398, 'Ke_max': 0.9}]


params_and_expect_result = list(zip(get_params_list(), [False, True]))


@pytest.mark.parametrize('params', get_params_list())
def test_bifurcation_data(dynamical_model, min_forcing, max_forcing, params, solver_method):
    BifurcationData.from_dynamical_model(dynamical_model, params, min_forcing, max_forcing, solver_method)


@pytest.mark.parametrize('params_and_expect_result', params_and_expect_result[:])
def test_stability_functions(dynamical_model, min_forcing, max_forcing, params_and_expect_result, solver_method):
    min_forcing = 260.
    params, expect_result = params_and_expect_result
    #  Test stability detection result
    stability_detection = compute_stability_detection(dynamical_model, params, min_forcing, max_forcing, solver_method)
    is_bistable = compute_is_bistable(stability_detection)
    assert is_bistable == expect_result
    if is_bistable:
        assert stability_detection == 392.
    else:
        np.testing.assert_almost_equal(stability_detection[300.][0], 0.00963327, decimal=2)
        np.testing.assert_almost_equal(stability_detection[400.][0], 0.01275249, decimal=2)
    forcing_to_attractors = compute_forcing_to_attractors(dynamical_model, params, stability_detection, min_forcing,
                                                          max_forcing, solver_method)
    #  Test stability ranges result
    stability_ranges = compute_stability_ranges(forcing_to_attractors, stability_detection, min_forcing,
                                                max_forcing)
    if is_bistable:
        stability_forcing_range, stability_state_range = (388., np.nan), (
            np.array([0.011773203412286574]), np.array([np.nan]))
    else:
        stability_forcing_range, stability_state_range = (np.nan, np.nan), (np.array([np.nan]), np.array([np.nan]))
    assert stability_ranges[0] == stability_forcing_range
    for a, b in zip(stability_state_range, stability_ranges[1]):
        np.testing.assert_almost_equal(a[0], b[0], decimal=2)
    #  Test repulsor
    forcing_to_repulsor = compute_forcing_to_repulsor(dynamical_model, params, stability_ranges,
                                                      is_bistable, max_forcing, solver_method)
    if is_bistable:
        forcings_inside_bistable_range = list(forcing_to_repulsor.keys())
        repulsors = list(forcing_to_repulsor.values())
        assert forcings_inside_bistable_range[0] == 389.
        assert forcings_inside_bistable_range[-1] == 399.
        np.testing.assert_almost_equal(repulsors[0], 0.20081269555681092, decimal=2)
        np.testing.assert_almost_equal(repulsors[-1], 0.168000195556811, decimal=2)
    else:
        assert len(forcing_to_repulsor) == 0
