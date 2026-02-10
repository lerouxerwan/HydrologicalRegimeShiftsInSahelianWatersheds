from typing import Union

from calibration.observation_constraint.observation_constraint import ObservationConstraint
from calibration.observation_constraint.observation_constraint_utils import load_csv_with_constraint
from utils.utils_watershed import get_csv_filepath


class RunoffCoefficientObservationConstraint(ObservationConstraint):

    def __init__(self, watershed_name: str, final_year: Union[None, int] = None):
        #  Load filepath
        filepath = get_csv_filepath(watershed_name)
        #  Load years and list of constraint
        years, constraint_name_to_values = load_csv_with_constraint(3, 'Ke', filepath)
        #   Names of the constraint
        constraint_names = ['Ke']
        super().__init__(years, constraint_names, constraint_name_to_values, final_year)
        self.watershed_name = watershed_name

    @property
    def constraint_name_to_color(self) -> dict[str, str]:
        return {'Ke': 'blueviolet'}

    @property
    def _name(self) -> str:
        return 'runoff'


if __name__ == '__main__':
    print(RunoffCoefficientObservationConstraint('Dargol_Kakassi'))
