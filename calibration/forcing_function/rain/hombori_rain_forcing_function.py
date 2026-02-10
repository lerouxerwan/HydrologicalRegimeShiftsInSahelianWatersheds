import os.path as op

import numpy as np
import pandas as pd

from calibration.forcing_function.rain.rain_forcing_function import RainForcingFunction
from utils.utils_path.utils_path import OBSERVATION_PATH, PROVIDED_DATA_PATH


class HomboriRainForcingFunction(RainForcingFunction):
    """Forcing Function for the Hombori station to reproduce the results from Wendling et al. 2019"""
    path = PROVIDED_DATA_PATH
    filename = 'test/PluiesAnnuellesHombori.txt'

    def __init__(self):
        # Load data
        # Load data from the file
        filepath = op.join(self.path, self.filename)
        df = pd.read_csv(filepath, sep="\t", header=0)
        df = df.astype(float)
        # Remove rows that contains only nan values
        # However if a row contains nan values and float values we keep it
        ind = ~(df.iloc[:, 1] < 0)
        ind &= df.iloc[:, 0]
        df = df.loc[ind]
        # Extract values and cast them
        years = [int(v) for v in df.iloc[:, 0].values]
        forcing_vector_list = [np.array([float(v)]) for v in df.iloc[:, 1].values]
        super().__init__(years, forcing_vector_list)

    @property
    def name(self):
        return "Hombori"


