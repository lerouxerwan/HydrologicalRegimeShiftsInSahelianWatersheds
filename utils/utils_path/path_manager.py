import os
import os.path as op
from dataclasses import dataclass
from functools import cached_property

import numpy as np

from utils.utils_path.filename_manager.attribution_filename_manager import AttributionFilenameManager
from utils.utils_path.filename_manager.bifurcation_filename_manager import BifurcationFilenameManager
from utils.utils_path.filename_manager.calibration_filename_manager import CalibrationFilenameManager
from utils.utils_path.filename_manager.dataset_filename_manager import DatasetFilenameManager
from utils.utils_path.filename_manager.filename_manager import FilenameManager
from utils.utils_path.filename_manager.utils_filename_manager import FilenameManagerToLoadError


@dataclass
class PathManager(object):
    path: str
    filename_manager: FilenameManager

    def create_folder_if_needed(self):
        #  Create folder if needed
        if not op.exists(self.folder_path):
            os.makedirs(self.folder_path)

    def remove_folder(self):
        #  Remove file then folder if it is empty
        if op.exists(self.folder_path):
            if op.isfile(self.filepath_to_save):
                os.remove(self.filepath_to_save)
            if not os.listdir(self.folder_path):
                os.rmdir(self.folder_path)

    @property
    def folder(self):
        return self.filename_manager.folder

    @property
    def folder_path(self):
        return op.join(self.path, self.folder)

    @cached_property
    def filepath_to_save(self):
        return op.join(self.path, self.filename_to_save)

    @cached_property
    def filename_to_save(self):
        return self.filename_manager.filename

    @property
    def has_been_saved(self):
        try:
            return op.isfile(self.filepath_to_load)
        except FilenameManagerToLoadError:
            return False

    @property
    def filepath_to_load(self):
        return op.join(self.path, self.filename_to_load)

    @property
    def filename_to_load(self):
        return self.filename_manager_to_load.filename

    @property
    def filename_manager_to_load(self) -> CalibrationFilenameManager:
        if not op.exists(self.path):
            raise FilenameManagerToLoadError('no match for {}'.format(self.filename_manager))
        other_managers = []
        for folder in os.listdir(self.path):
            folder_path = op.join(self.path, folder)
            for filename in os.listdir(folder_path):
                if op.isfile(op.join(folder_path, filename)):
                    other_managers.append(self.filename_manager.from_filename(folder, filename))
        if len(other_managers) == 0:
            raise FilenameManagerToLoadError('no match for {}'.format(self.filename_manager))
        other_managers = [other_manager for other_manager in other_managers if self.filename_manager == other_manager]
        if len(other_managers) == 0:
            raise FilenameManagerToLoadError('no match for {}'.format(self.filename_manager))
        if isinstance(self.filename_manager, DatasetFilenameManager):
            assert len(other_managers) == 1, other_managers
            return other_managers[0]
        # Load the forcing with the closest forcing name
        lengths_forcing_names_compatible = [len(other_manager.forcing_function_name) for other_manager in other_managers]
        max_length_forcing_names_compatible = np.max(lengths_forcing_names_compatible)
        indices_where_max_length_is_reached = [i for i, l in enumerate(lengths_forcing_names_compatible)
                                               if l == max_length_forcing_names_compatible]
        other_managers = [other_managers[i] for i in indices_where_max_length_is_reached]
        assert len(other_managers) > 0
        # Due to inheritance property, the order of "if" statements are important
        if isinstance(self.filename_manager, AttributionFilenameManager):
            #  Select the smallest gap between the initial_year and the final_year
            gaps = [other_manager.final_year - other_manager.initial_year for other_manager in other_managers]
            selected_other_manager = other_managers[np.argmin(gaps)]
        elif isinstance(self.filename_manager, (CalibrationFilenameManager, BifurcationFilenameManager)):
            #  Select the smallest ensemble size for faster loading
            ensemble_sizes = [other_manager.ensemble_size for other_manager in other_managers]
            selected_other_manager = other_managers[np.argmin(ensemble_sizes)]
        else:
            raise NotImplementedError
        return selected_other_manager
