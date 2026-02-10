from collections import OrderedDict
from typing import Union

import numpy as np


def is_bistable(attractors: list[np.ndarray]) -> bool:
    return len(attractors) == 2


def compute_is_bistable(stability_detection: Union[float, dict[float, np.ndarray]]) -> bool:
    if isinstance(stability_detection, float):
        return True
    else:
        assert isinstance(stability_detection, OrderedDict)
        return False
