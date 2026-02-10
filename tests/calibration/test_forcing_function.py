import pytest

from calibration.forcing_function.aggregated_forcing_function import \
    MinForcingFunction, MeanForcingFunction, MaxForcingFunction
from calibration.forcing_function.concatenated_forcing_function import ConcatenatedForcingFunction
from calibration.forcing_function.constant_forcing_function import ConstantForcing
from calibration.forcing_function.rain.hombori_rain_forcing_function import \
    HomboriRainForcingFunction
from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction
from utils.utils_watershed import watershed_name_to_prefix


def test_load_rain_obs():
    forcing_functions = [HomboriRainForcingFunction()]
    for watershed_name in watershed_name_to_prefix.keys():
        forcing_functions.append(RainObsForcingFunction(watershed_name))
    for forcing_function in forcing_functions:
        _ = forcing_function.name


def test_load_rain_constant():
    ConstantForcing(nb_years=2, constant_value=0.0)
    with pytest.raises(AssertionError):
        ConstantForcing(nb_years=0, constant_value=0.0)
    with pytest.raises(AssertionError):
        ConstantForcing(nb_years=2, constant_value=0)


def test_concatenated_forcing():
    rain_forcing_function = ConstantForcing(nb_years=4, constant_value=0.0)
    rain2_forcing_function = ConstantForcing(nb_years=3, constant_value=1.0)
    concatenated_forcing_function = ConcatenatedForcingFunction([rain_forcing_function, rain2_forcing_function])
    assert len(concatenated_forcing_function.years) == 3
    assert len(concatenated_forcing_function.forcing_vector_list[0]) == 2


@pytest.fixture
def watershed_gcm_scenario_variant_id_list():
    return [['Dargol_Kakassi', 'IPSL-CM6A-LR', scenario, 'r2i1p1f1']
            for scenario in ['amip', 'historical']]


def test_aggregate_forcing_function():
    aggregate_forcing_function_types = [MinForcingFunction, MeanForcingFunction, MaxForcingFunction]
    any_forcing_function = HomboriRainForcingFunction()
    for aggregate_forcing_function_type in aggregate_forcing_function_types:
        aggregate_forcing_function_type([any_forcing_function, any_forcing_function])
