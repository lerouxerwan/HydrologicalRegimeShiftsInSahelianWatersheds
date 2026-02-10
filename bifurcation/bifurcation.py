import logging
import os.path as op
from collections import OrderedDict
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Optional

import pandas as pd

from bifurcation.bifurcation_data.bifurcation_data import BifurcationData
from calibration.calibration import Calibration
from calibration.utils_calibration.sampling import sampling_to_str
from calibration.utils_calibration.solve import solver_method_to_str
from continuation.get_continuation_bifurcation_attributes import get_bifurcation_attributes
from utils.utils_log import log_info
from utils.utils_multiprocessing import parallelize
from utils.utils_path.filename_manager.bifurcation_filename_manager import BifurcationFilenameManager
from utils.utils_path.path_manager import PathManager
from utils.utils_path.utils_path import BIFURCATION_DATA_PATH, CONTINUATION_BIFURCATION_DATA_PATH


@dataclass
class Bifurcation(object):
    calibration: Calibration
    min_forcing: float = 1.  # minimum forcing used to compute bifurcation_data (attractors, ...)
    max_forcing: float = 4000.  #  maximum forcing used to compute bifurcation_data (attractors, ...)
    ensemble_ids: Optional[list[int]] = None

    def __post_init__(self):
        if self.ensemble_ids is None:
            self.ensemble_ids = self.calibration.ensemble_ids
        self.filename_manager = BifurcationFilenameManager(self.calibration.observation_constraint.name,
                                                           self.calibration.nb_samples,
                                                           self.calibration.forcing_function.name,
                                                           self.calibration.ensemble_size,
                                                           self.calibration.initial_year_for_loading,
                                                           self.calibration.nb_years_for_initial_state,
                                                           self.calibration.sampling_str,
                                                           self.calibration.solver_method_str,
                                                           self.min_forcing, self.max_forcing)
        bifurcation_data_path = CONTINUATION_BIFURCATION_DATA_PATH
        # bifurcation_data_path = BIFURCATION_DATA_PATH
        self.path_manager = PathManager(op.join(bifurcation_data_path, self.calibration.dynamical_model.name),
                                        self.filename_manager)

    @cached_property
    def ensemble_id_to_bifurcation_data(self) -> dict[int, BifurcationData]:
        return dict(zip(self.ensemble_ids, self.bifurcation_data_list))

    @cached_property
    def bifurcation_data_list(self):
        #  Load or compute/save stability data list
        if self.bifurcation_data_ensemble_has_been_saved:
            bifurcation_data_list = self._load_bifurcation_data_list()
        else:
            bifurcation_data_list = self._compute_bifurcation_data_list()
            self._save_bifurcation_data_list(bifurcation_data_list)
        return bifurcation_data_list

    @cached_property
    def monostable_ensemble_ids(self) -> list[int]:
        monostable_ensemble_ids = []
        for ensemble_id, bifurcation_data in enumerate(self.bifurcation_data_list):
            if not bifurcation_data.is_bistable:
                monostable_ensemble_ids.append(ensemble_id)
        log_info(f'{len(monostable_ensemble_ids)} monostable solutions: {monostable_ensemble_ids}')
        return monostable_ensemble_ids

    @property
    def bistable_ensemble_ids(self) -> list[int]:
        s = set(self.monostable_ensemble_ids)
        return [ensemble_id for ensemble_id in self.ensemble_ids if ensemble_id not in s]

    @property
    def monostable_errors(self):
        return [self.calibration.ensemble_id_to_error[ensemble_id] for ensemble_id in self.monostable_ensemble_ids]

    @property
    def bistable_errors(self):
        return [self.calibration.ensemble_id_to_error[ensemble_id] for ensemble_id in self.bistable_ensemble_ids]

    @property
    def bifurcation_data_ensemble_has_been_saved(self):
        return self.path_manager.has_been_saved

    def check_valid_sharing(self, other_calibration: Calibration):
        #  Check valid sharing
        filename_manager1, filename_manager2 = other_calibration.filename_manager, self.calibration.filename_manager
        assert filename_manager1 == filename_manager2, filename_manager1.get_equality_conditions(filename_manager2)

    ###########################################
    #
    #           Private methods to save and load stability data ensemble
    #
    ###########################################

    def _load_bifurcation_data_list(self) -> list[BifurcationData]:
        log_info('Loading bifurcation data list...')
        df = pd.read_csv(self.path_manager.filepath_to_load, index_col=0, dtype=str,
                         nrows=self.calibration.ensemble_size)
        assert len(df) == len(self.ensemble_ids)
        bifurcation_data_list = []
        for _, series in df.iterrows():
            bifurcation_data = BifurcationData.from_series(series, self.min_forcing, self.max_forcing)
            bifurcation_data_list.append(bifurcation_data)
        return bifurcation_data_list

    def _compute_bifurcation_data_list(self) -> list[BifurcationData]:
        # Compute bifurcation_data
        log_info(f'Compute bifurcation data for all ensemble members ({self.calibration.ensemble_size} members)')
        return parallelize(self._compute_bifurcation_data, self.ensemble_ids)

    def _save_bifurcation_data_list(self, bifurcation_data_list: list[BifurcationData]):
        stability_filepath_to_save = self.path_manager.filepath_to_save
        if op.isfile(stability_filepath_to_save):
            log_info(f'{op.basename(stability_filepath_to_save)} has already been saved')
            return None
        else:
            log_info('Save stability data list')
            #  Create folder is needed
            self.path_manager.create_folder_if_needed()
            #  Create csv file with the data
            ensemble_id_to_series = OrderedDict()
            for ensemble_id, bifurcation_data in enumerate(bifurcation_data_list):
                ensemble_id_to_series[ensemble_id] = bifurcation_data.to_series()
            df = pd.DataFrame(ensemble_id_to_series).transpose()
            df.index.name = 'ensemble_id'
            df.to_csv(stability_filepath_to_save)

    def _compute_bifurcation_data(self, ensemble_id: int) -> BifurcationData:
        """
        Compute bifurcation_data: stability detection, stability ranges, bistability, and threshold for regime shift
        """
        watershed_name = self.filename_manager.forcing_function_name
        bifurcation_attributes = get_bifurcation_attributes(watershed_name, ensemble_id, self.min_forcing, self.max_forcing)
        forcing_to_attractors, forcing_to_repulsor, stability_ranges, stability_detection = bifurcation_attributes
        bifurcation_data = BifurcationData(stability_ranges, stability_detection, self.min_forcing, self.max_forcing,
                                           forcing_to_attractors, forcing_to_repulsor)


        if ensemble_id == 0:
            log_info('Computing bifurcation_data...')
        if ensemble_id % 10 == 0:
            log_info(ensemble_id)
        return bifurcation_data
