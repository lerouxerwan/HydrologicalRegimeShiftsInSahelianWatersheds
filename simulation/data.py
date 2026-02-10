from abc import ABC, abstractmethod
from dataclasses import dataclass

from simulation.variable import Variable


@dataclass
class Data(ABC):
    """Abstract class to load data for a specific watershed and a specific variable (precipitation, temperature, ...)"""
    watershed_name: str
    variable: Variable

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def years(self) -> list[int]:
        pass

