import math
from abc import ABC

from calibration.forcing_function.unidimensional_forcing_function import UnidimensionalForcingFunction

RAIN_LABEL = 'Precipitation P (mm)'

RAIN_STR = 'p'

class RainForcingFunction(UnidimensionalForcingFunction, ABC):
    """Abstract Rain forcing function that defines some attributes and methods common to all rain forcings"""

    @property
    def forcing_name(self):
        return RAIN_STR

    def plot_forcing_function(self, ax, years=None, color='cornflowerblue', linestyle='-', linewidth=None,
                              label=None,
                              marker=None, fontsize=None):
        label = 'Precipitation' if label is None else label
        marker = 'x' if marker is None else marker
        p = super().plot_forcing_function(ax, years, color, linestyle, linewidth, label, marker, fontsize)
        ax.set_ylim((0, 100 * (3 + math.floor(max(p) / 100))))
        return p

    @property
    def y_label(self) -> str:
        return RAIN_LABEL
