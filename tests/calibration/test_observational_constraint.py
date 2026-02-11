import pytest
from matplotlib import pyplot as plt

from calibration.observation_constraint.vegetation.ortonde_vegetation_constraint import \
    OrtondeVegetationConstraint
from calibration.observation_constraint.runoff.runoff_coefficient_constraint import \
    RunoffCoefficientObservationConstraint
from calibration.observation_constraint.vegetation.vegetation_and_runoff_coefficient_constraint import \
    VegetationAndRunoffCoefficientObservationConstraint
from calibration.observation_constraint.vegetation.vegetation_constraint import \
    VegetationObservationConstraint


@pytest.fixture
def watershed_name():
    return 'Dargol_Kakassi'


def test_load_watershed_constraint(watershed_name):
    observation_constraint = RunoffCoefficientObservationConstraint(watershed_name)
    observation_constraint.plot_observation_constraint(plt.gca())


def load_ortonde_constraint():
    ax = plt.gca()
    constraint = OrtondeVegetationConstraint()
    constraint.plot_observation_constraint(ax)
