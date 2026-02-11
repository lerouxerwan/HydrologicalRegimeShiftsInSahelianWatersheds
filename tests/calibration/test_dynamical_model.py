import pytest
from matplotlib import pyplot as plt

from calibration.dynamical_model.one_state.tiphyc_annual import DynamicalModelTipHycAnnual
from calibration.dynamical_model.two_states.wendling_2019 import DynamicalModelWendling2019
from calibration.forcing_function.rain.rain_forcing_function import RAIN_STR
from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction
from calibration.observation_constraint.runoff.runoff_coefficient_constraint import \
    RunoffCoefficientObservationConstraint
from calibration.utils_calibration.load_sample_v1 import load_sample_parameters

watershed_name = 'Dargol_Kakassi'


@pytest.fixture
def forcing_function():
    return RainObsForcingFunction(watershed_name)


@pytest.fixture
def times():
    return [2000.0, 2001.0]


@pytest.fixture()
def forcings():
    return {RAIN_STR: 500.0}


def get_params(dynamical_model):
    params_vector_list = load_sample_parameters(dynamical_model, nb_samples=1)
    return dynamical_model.get_params(params_vector_list[0])


def get_states(dynamical_model):
    return dynamical_model.extremal_initial_states


def test_load_and_plot_model(forcing_function, times):
    ax = plt.gca()
    for model_type in [DynamicalModelWendling2019, DynamicalModelTipHycAnnual]:
        dynamical_model = model_type(forcing_function)
        state_vectors = get_states(dynamical_model)
        params = get_params(dynamical_model)
        assert len(times) == len(state_vectors)
        states_list = [dynamical_model.create_states(state_vector) for state_vector in state_vectors]
        dynamical_model.plot_dynamical_model(ax, times, params, states_list)


def test_get_variable(forcing_function, forcings):
    model_type_to_variable_names = {
        DynamicalModelWendling2019: [],
        DynamicalModelTipHycAnnual: [],
    }
    for model_type, variable_names in model_type_to_variable_names.items():
        dynamical_model = model_type(forcing_function)
        params = get_params(dynamical_model)
        state = get_states(dynamical_model)[0]
        for variable_name in variable_names:
            dynamical_model.get_variable(variable_name, forcings, state, params)


def test_get_state_wendling_2022(forcing_function, forcings):
    dynamical_model = DynamicalModelTipHycAnnual(forcing_function)
    params = get_params(dynamical_model)
    observation_constraint = RunoffCoefficientObservationConstraint(watershed_name)
    dynamical_model.get_state(forcings, 1957, params, observation_constraint)


