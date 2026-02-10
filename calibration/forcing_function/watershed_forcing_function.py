
from abc import abstractmethod
from typing import Union

from calibration.forcing_function.unidimensional_forcing_function import UnidimensionalForcingFunction
from simulation.annual_data.annual_data import AnnualData
from simulation.variable import Variable


class WatershedForcingFunction(UnidimensionalForcingFunction):

    def __init__(self, watershed_name: str, *args, **kwargs):
        self.watershed_name = watershed_name
        self.annual_data: AnnualData = self.annual_data_type(self.watershed_name, self.variable, *args, **kwargs)
        super().__init__(self.annual_data.years, self.annual_data.forcing_vector_list)

    @property
    @abstractmethod
    def annual_data_type(self) -> type:
        pass

    @property
    @abstractmethod
    def variable(self) -> Variable:
        pass

    @property
    def name(self) -> str:
        return self.annual_data.name

    @property
    def label(self) -> Union[None, str]:
        return self.annual_data.label

