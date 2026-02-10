import math
from functools import cache
from typing import Iterable

import numpy as np

""""
To summarize the convertion/conceptual difference between year and time:
    -year (int) has an 'intuitive' definition: what is the year of some measurement ? (for the forcing or constraint)
    -time (float) correspond to the solver definition, and what we will be always used in the plot.
    For the solver, we consider that a constraint/forcing for the year year=Y is valid between time=Y.000001 to time=Y+1
    For instance, if we initialize our initial state with an observation constraint for the year 1955, 
    it means that the initial time for the solver is time=1956 and we fix the state equal to the constraint.
    For the RMSE computation, we compare all the states for the year=Y with the constraint, i.e. in the case where 
    the time_step < 1.0 (by default it is equal to 1.0) then all the states between time=Y.0000000001 to time=Y+1 
    are compared with the constraint of year Y; and all these states are obtained using the forcing for the year Y.
For instance, when we create a plot, if we want to:
1-plot some forcing until 1970.0 included, use the following times: load_times(initial_year, 1969, 0.1) 
2-draw a vertical line at 1970.0: draw a line at the point time=1970
3-plot another forcing that start at 1970.0, use the following time: load_times(1969, final_year, 0.1)
"""


@cache
def get_time_from_year(year: int) -> float:
    assert isinstance(year, int)
    return float(year + 1)


def get_times_from_years(years: Iterable[int]) -> list[float]:
    return [get_time_from_year(year) for year in years]


def get_year_from_time(time: float) -> int:
    assert isinstance(time, float)
    return int(time - 1) if float(math.floor(time)) == time else math.floor(time)


def load_times(initial_year: int, final_year: int, time_step: float = 1.0) -> np.ndarray:
    """
    :param initial_year: initial year to start solving (int)
    :param final_year: initial year to end solving (int)
    :param time_step: represents a percentage of years (float)
    :return: a np.ndarray containing time between initial_year and final_year separated by a time_step
    """
    assert isinstance(initial_year, int)
    assert isinstance(final_year, int)
    assert 0.0 < time_step <= 1.0
    nb_steps = int((final_year - initial_year) / time_step + 1)
    initial_time, final_time = get_time_from_year(initial_year), get_time_from_year(final_year)
    return np.linspace(initial_time, final_time, nb_steps)
