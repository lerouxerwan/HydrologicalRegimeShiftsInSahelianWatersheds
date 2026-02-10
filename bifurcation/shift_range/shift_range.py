from dataclasses import dataclass

import numpy as np


@dataclass
class ShiftRange(object):
    lower_state_value: float
    upper_state_value: float
    forcing_lower_state: float
    forcing_upper_state: float

    def __post_init__(self):
        assert self.lower_state_value < self.upper_state_value

    @property
    def middle_state_value(self):
        return 0.5 * (self.lower_state_value + self.upper_state_value)

    @property
    def branches_are_crossing(self) -> bool:
        return self.forcing_lower_state <= self.forcing_upper_state

    @property
    def original_data_structure(self):
        return ((self.forcing_lower_state, self.forcing_upper_state),
                (np.array([self.lower_state_value]), np.array([self.upper_state_value])))

    @property
    def array_data(self):
        return np.array([self.lower_state_value, self.upper_state_value, self.forcing_lower_state, self.forcing_upper_state])


