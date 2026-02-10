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
    ax = plt.gca()
    for observation_constraint_type in [VegetationObservationConstraint,
                                         VegetationAndRunoffCoefficientObservationConstraint,
                                         RunoffCoefficientObservationConstraint]:
        observation_constraint = observation_constraint_type(watershed_name)
        observation_constraint.plot_observation_constraint(ax)


def load_ortonde_constraint():
    ax = plt.gca()
    constraint = OrtondeVegetationConstraint()
    constraint.plot_observation_constraint(ax)
