import os.path as op
from dataclasses import dataclass

from utils.utils_path.filename_manager.filename_manager import FilenameManager
from utils.utils_path.filename_manager.utils_filename_manager import SEPARATOR


@dataclass
class CalibrationFilenameManager(FilenameManager):
    """Object to help handling filenames of saved objects (model, bifurcation_data)"""
    observation_constraint_name: str
    nb_samples: int
    forcing_function_name: str
    ensemble_size: int
    initial_year_for_loading: int
    nb_years_for_initial_state: int
    sampling_str: str
    solver_method_str: str

    def __post_init__(self):
        #  Check types
        assert isinstance(self.ensemble_size, int)
        assert isinstance(self.nb_samples, int)
        assert isinstance(self.initial_year_for_loading, int)
        assert isinstance(self.nb_years_for_initial_state, int)
        assert isinstance(self.sampling_str, str)
        assert isinstance(self.solver_method_str, str)
        assert SEPARATOR not in self.observation_constraint_name, self.observation_constraint_name

    def __eq__(self, other):
        return all(self.get_equality_conditions(other))

    def get_equality_conditions(self, other):
        conditions = \
            [self.forcing_name_condition(other),
             self.observation_constraint_name == other.observation_constraint_name,
             self.nb_samples == other.nb_samples,
             self.ensemble_size_condition(other),
             self.initial_year_condition(other),
             self.nb_years_for_initial_state == other.nb_years_for_initial_state,
             self.sampling_str == other.sampling_str,
             self.solver_method_str == other.solver_method_str,
             ]
        return conditions

    def forcing_name_condition(self, other):
        return self.forcing_function_name.startswith(other.forcing_function_name)

    def initial_year_condition(self, other):
        #  Initial_year_for_loading conditions
        if self.forcing_function_name == other.forcing_function_name:
            return self.initial_year_for_loading == other.initial_year_for_loading
        if not self.forcing_function_name.startswith(other.forcing_function_name):
            return False
        #  Forcing function is a suffix of other.forcing_function_name
        return self.initial_year_for_loading >= other.initial_year_for_loading

    def ensemble_size_condition(self, other):
        return self.ensemble_size <= other.ensemble_size

    @classmethod
    def expected_number_after_split(cls):
        return 8

    @classmethod
    def from_filename(cls, folder, filename):
        filename = '.'.join(filename.split('.')[:-1])
        initial_year_for_loading = int(filename[-4:])
        forcing_function_name = filename[:-5]
        l_split = folder.split(SEPARATOR) + [forcing_function_name] + [initial_year_for_loading]
        assert len(l_split) == cls.expected_number_after_split(), (
            'filename {} in {} does not have a standard name'.format(filename, folder))
        return cls._from_filename(filename, l_split)

    @classmethod
    def _from_filename(cls, filename, l_split):
        (observation_constraint_name, nb_samples, ensemble_size, nb_years_for_initial_state, sampling_str, solver_method_str,
         forcing_function_name, initial_year_for_loading) = l_split
        try:
            ensemble_size = int(ensemble_size)
            nb_samples = int(nb_samples)
            nb_years_for_initial_state = int(nb_years_for_initial_state)
        except ValueError:
            raise ValueError("Error in the filename {}".format(filename))
        return cls(observation_constraint_name, nb_samples, forcing_function_name, ensemble_size,
                   initial_year_for_loading, nb_years_for_initial_state, sampling_str, solver_method_str)

    @property
    def parameters(self):
        return [self.observation_constraint_name, str(self.nb_samples), str(self.ensemble_size),
                str(self.nb_years_for_initial_state), self.sampling_str, self.solver_method_str]

    @property
    def filename(self):
        return op.join(self.folder,
                       self.forcing_function_name + SEPARATOR + str(self.initial_year_for_loading) + '.csv')
