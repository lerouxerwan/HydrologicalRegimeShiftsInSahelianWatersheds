from dataclasses import dataclass

from utils.utils_path.filename_manager.calibration_filename_manager import CalibrationFilenameManager


@dataclass
class BifurcationFilenameManager(CalibrationFilenameManager):
    min_forcing: float
    max_forcing: float

    def __post_init__(self):
        super().__post_init__()
        assert isinstance(self.min_forcing, float)
        assert isinstance(self.max_forcing, float)

    def get_equality_conditions(self, other):
        conditions = super().get_equality_conditions(other)
        conditions.extend([self.min_forcing == other.min_forcing,
                           self.max_forcing == other.max_forcing])
        return conditions

    @classmethod
    def expected_number_after_split(cls):
        return super().expected_number_after_split() + 2

    @classmethod
    def _from_filename(cls, filename, l_split):
        (observation_constraint_name, nb_samples, ensemble_size, nb_years_for_initial_state, sampling_str, solver_method_str,
         min_forcing, max_forcing, forcing_function_name, initial_year_for_loading) = l_split
        try:
            ensemble_size = int(ensemble_size)
            nb_years_for_initial_state = int(nb_years_for_initial_state)
            nb_samples = int(nb_samples)
            min_forcing = float(min_forcing)
            max_forcing = float(max_forcing)
        except ValueError:
            raise ValueError("Error in the filename {}".format(filename))
        return cls(observation_constraint_name, nb_samples, forcing_function_name, ensemble_size,
                   initial_year_for_loading, nb_years_for_initial_state, sampling_str, solver_method_str, min_forcing, max_forcing)

    @property
    def parameters(self):
        parameters = super().parameters
        parameters.append(str(int(self.min_forcing)))
        parameters.append(str(int(self.max_forcing)))
        return parameters

    def __eq__(self, other):
        return all(self.get_equality_conditions(other))
