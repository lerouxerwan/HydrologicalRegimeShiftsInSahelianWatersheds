import os.path as op

import pandas as pd

from calibration.observation_constraint.observation_constraint_utils import load_series
from simulation.annual_data.annual_data import AnnualData
from simulation.variable import Variable
from utils.utils_path.utils_path import OBSERVATION_PATH
from utils.utils_watershed import get_csv_filepath


class AnnualObs(AnnualData):
    path = op.join(OBSERVATION_PATH, "runoff")

    @property
    def _series(self) -> pd.Series:
        if self.variable is Variable.PRECIP:
            # Load data from the file
            filepath = get_csv_filepath(self.watershed_name)
            #  Load series
            return load_series(0, filepath)
        else:
            raise ValueError('unavailable data for the variable {}'.format(self.variable))

    @property
    def name(self) -> str:
        return self.watershed_name
