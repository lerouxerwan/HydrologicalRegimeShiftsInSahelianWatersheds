from calibration.forcing_function.rain.rain_forcing_function import RainForcingFunction
from calibration.forcing_function.watershed_forcing_function import WatershedForcingFunction
from simulation.annual_data.annual_obs import AnnualObs
from simulation.variable import Variable


class WatershedRainForcingFunction(WatershedForcingFunction, RainForcingFunction):
    """Rain forcing function that defines some attributes and methods common to all rain forcings"""

    @property
    def variable(self) -> Variable:
        return Variable.PRECIP


class RainObsForcingFunction(WatershedRainForcingFunction):
    """Forcing function of the observed annual precipitation for each watershed"""

    @property
    def annual_data_type(self) -> type:
        return AnnualObs




