import os.path as op

from calibration.observation_constraint.observation_constraint import ObservationConstraint
from calibration.observation_constraint.observation_constraint_utils import \
    watershed_name_to_filename_for_satellite_vegetation, load_csv_with_constraint
from utils.utils_path.utils_path import OBSERVATION_PATH


class VegetationObservationConstraint(ObservationConstraint):
    path = op.join(OBSERVATION_PATH, "vegetation")

    def __init__(self, watershed_name, final_year=None):
        #   Load filepath
        filename = watershed_name_to_filename_for_satellite_vegetation[watershed_name]
        filepath = op.join(OBSERVATION_PATH, "vegetation", filename)
        #   Names of the constraint
        constraint_names = ['V']
        #  Load years and list of constraint
        years, constraint_name_to_values = load_csv_with_constraint(-1, constraint_names[0], filepath)
        super().__init__(years, constraint_names, constraint_name_to_values, final_year)

    @property
    def constraint_name_to_color(self) -> dict[str, str]:
        return {'V': 'g'}

    @property
    def _name(self) -> str:
        return 'vegetation'


if __name__ == '__main__':
    constraint = VegetationObservationConstraint('Dargol_Kakassi')
