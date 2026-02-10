from abc import abstractmethod
from collections.abc import Iterable
from typing import Union

import numpy as np

from calibration.forcing_function.forcing_function import ForcingFunction
from calibration.utils_calibration.convert import load_times, get_times_from_years


class UnidimensionalForcingFunction(ForcingFunction):

    def __init__(self, years: list[int], forcing_vector_list: list[np.ndarray]):
        super().__init__(years, forcing_vector_list, [self.forcing_name])

    @property
    def forcing_name(self):
        return 'default forcing name'

    def plot_forcing_function(self, ax, years=None, color='cornflowerblue', linestyle='-',
                              linewidth=None, label=None, marker=None, fontsize=None):
        if years is None:
            years = self.years
        p = [f[self.forcing_name] for f in self.get_forcings_list(get_times_from_years(years))]
        ax.plot(years, p, color, label=label, linestyle=linestyle, linewidth=linewidth, marker=marker)
        ax.set_ylabel(self.y_label, fontsize=fontsize)
        return p

    @property
    def label(self) -> Union[None, str]:
        return None


    @property
    @abstractmethod
    def y_label(self) -> str:
        pass
