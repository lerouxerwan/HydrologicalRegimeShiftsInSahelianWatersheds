import pytest

from simulation.annual_data.annual_obs import AnnualObs
from simulation.variable import Variable
from tests.simulation.utils_test_simulation import check_simulation_data


@pytest.fixture
def watershed_name() -> str:
    return 'Dargol_Kakassi'


def test_annual_obs(watershed_name: str):
    check_simulation_data(AnnualObs(watershed_name, Variable.PRECIP), [2015])
    with pytest.raises(ValueError):
        check_simulation_data(AnnualObs(watershed_name, Variable.TEMP), [2015])














