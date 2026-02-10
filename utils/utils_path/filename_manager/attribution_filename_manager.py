from dataclasses import dataclass

from utils.utils_path.filename_manager.bifurcation_filename_manager import BifurcationFilenameManager


@dataclass
class AttributionFilenameManager(BifurcationFilenameManager):
    attribution_study_name: str
    initial_year: int
    final_year: int

    def __post_init__(self):
        super().__post_init__()
        assert isinstance(self.attribution_study_name, str)
        assert self.initial_year <= self.final_year

    def get_equality_conditions(self, other):
        conditions = super().get_equality_conditions(other)
        conditions.append(self.attribution_study_name == other.attribution_study_name)
        conditions.append(self.initial_year >= other.initial_year)
        conditions.append(self.final_year <= other.final_year)
        return conditions

    def forcing_name_condition(self, other):
        return self.forcing_function_name == other.forcing_function_name

    def initial_year_condition(self, other):
        return self.initial_year_for_loading == other.initial_year_for_loading

    def ensemble_size_condition(self, other):
        #  Enforce equality of the ensemble size so that the probabilities may be valid
        return self.ensemble_size == other.ensemble_size

    def get_skip_rows_and_nrows(self, other):
        skip_rows = self.initial_year - other.initial_year
        nrows = self.final_year - self.initial_year
        return skip_rows, nrows

    @classmethod
    def expected_number_after_split(cls):
        return super().expected_number_after_split() + 3

    @classmethod
    def _from_filename(cls, filename, l_split):
        (observation_constraint_name, nb_samples, ensemble_size, nb_years_for_initial_state,
         min_forcing, max_forcing, attribution_study_name,
         initial_year, final_year, forcing_function_name, initial_year_for_loading) = l_split
        try:
            ensemble_size = int(ensemble_size)
            nb_samples = int(nb_samples)
            nb_years_for_initial_state = int(nb_years_for_initial_state)
            min_forcing = float(min_forcing)
            max_forcing = float(max_forcing)
            initial_year = int(initial_year)
            final_year = int(final_year)
        except ValueError:
            raise ValueError("Error in the filename {}".format(filename))
        return cls(observation_constraint_name, nb_samples, forcing_function_name, ensemble_size,
                   initial_year_for_loading, nb_years_for_initial_state, min_forcing, max_forcing,
                   attribution_study_name, initial_year, final_year)

    @property
    def parameters(self):
        parameters = super().parameters
        parameters.append(self.attribution_study_name)
        parameters.append(str(self.initial_year))
        parameters.append(str(self.final_year))
        return parameters

    def __eq__(self, other):
        return all(self.get_equality_conditions(other))
