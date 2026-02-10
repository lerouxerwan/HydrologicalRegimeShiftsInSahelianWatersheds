import os.path as op

import numpy as np
import pandas as pd

from calibration.observation_constraint.observation_constraint import ObservationConstraint
from utils.utils_path.utils_path import OBSERVATION_PATH


class OrtondeVegetationConstraint(ObservationConstraint):
    path = op.join(OBSERVATION_PATH, "vegetation")
    file_name = 'ortonde.txt'

    def __init__(self, final_year=None):
        #  Load years and list of constraint
        years, constraint_name_to_values = self.load_data()
        #   Names of the constraint
        constraint_names = ['w', 'b']
        super().__init__(years, constraint_names, constraint_name_to_values, final_year)

    @classmethod
    def load_data(cls):
        # Load data from the file
        filepath = op.join(cls.path, cls.file_name)
        df = pd.read_csv(filepath, sep=" ", header=0).iloc[:, 1:-1]
        # Remove rows that contains only nan values
        # However if a row contains nan values and float values we keep it
        ind = ~df.iloc[:, 1:].isnull().all(axis=1)
        df = df.loc[ind]
        # Extract values and cast them
        years = [int(time[:4]) for time in df['time'].values]
        constraint_name_to_values = {
            'w': np.array([float(v) for v in df['V'].values]) / 100,
            'b': np.array([float(v) for v in df['D'].values]) / 100,
        }
        return years, constraint_name_to_values

    @property
    def constraint_name_to_color(self) -> dict[str, str]:
        return {
            'w': 'darkgreen',
            'b': 'darkred'
        }

    @property
    def _name(self) -> str:
        return 'vegetation'
