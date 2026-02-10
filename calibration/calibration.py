import os.path as op
from collections import OrderedDict
from dataclasses import dataclass
from functools import cached_property
from operator import itemgetter

import numpy as np
import pandas as pd

from calibration.dynamical_model.dynamical_model import DynamicalModel
from calibration.forcing_function.forcing_function import ForcingFunction
from calibration.observation_constraint.vegetation.ortonde_vegetation_constraint import ObservationConstraint
from calibration.utils_calibration.convert import get_year_from_time, load_times, get_time_from_year
from calibration.utils_calibration.load_sample import sampling_to_load_function
from calibration.utils_calibration.sampling import Sampling, sampling_to_str
from calibration.utils_calibration.solve import SolverIvp, SolverMethod, solver_method_to_str
from utils.utils_log import log_info
from utils.utils_multiprocessing import parallelize
from utils.utils_path.filename_manager.calibration_filename_manager import CalibrationFilenameManager
from utils.utils_path.path_manager import PathManager
from utils.utils_path.utils_path import CALIBRATION_DATA_PATH


@dataclass
class Calibration(object):
    """Calibration of a dynamical model for a given observational constraint and forcing function"""
    observation_constraint: ObservationConstraint  #  constraint for the calibration
    forcing_function: ForcingFunction  #  forcing of the dynamical model
    dynamical_model: DynamicalModel
    nb_samples: int  #  Number of parameters sampled for the calibration
    ensemble_size: int = 100  #  Number of parameters selected during calibration
    show: bool = False  #  whether plots should be displayed directly or saved to file
    loading_calibration: bool = False
    initial_year_for_loading: int = None  #  initial year from which we start solving the trajectory
    nb_years_for_initial_state: int = 1
    sampling: Sampling = Sampling.V1
    solver_method: SolverMethod = SolverMethod.RK45

    def __post_init__(self):
        #   Default value for the initial year for loading
        if self.initial_year_for_loading is None:
            self.initial_year_for_loading = self._initial_year_without_loading
        #  Load managers for the filename and the path
        self.filename_manager, self.path_manager = self.create_managers()
        # Check if the filepath already exists or not
        if op.isfile(self.path_manager.filepath_to_save):
            self.loading_calibration = True
        #  Load solve data once
        _ = self.solve_data
        #   Check types
        assert isinstance(self.ensemble_size, int)
        assert isinstance(self.nb_samples, int)
        assert 0 < self.ensemble_size <= self.nb_samples
        assert isinstance(self.initial_year_for_loading, int)
        assert self.initial_year_for_loading <= self.final_year
        #  Save calibration
        if not self.loading_calibration_with_same_forcing:
            self.save_calibration()

    def create_managers(self):
        filename_manager = CalibrationFilenameManager(self.observation_constraint.name, self.nb_samples,
                                                      self.forcing_function.name, self.ensemble_size,
                                                      self.initial_year_for_loading, self.nb_years_for_initial_state,
                                                      self.sampling_str, self.solver_method_str)
        path_manager = PathManager(op.join(CALIBRATION_DATA_PATH, self.dynamical_model.name),
                                   filename_manager)
        return filename_manager, path_manager

    @property
    def sampling_str(self) -> str:
        return sampling_to_str[self.sampling]

    @property
    def solver_method_str(self):
        return solver_method_to_str[self.solver_method]

    @property
    def initial_year(self) -> int:
        if self.loading_calibration:
            _, _, _, loaded_times = self._loaded_calibration
            initial_year_loaded_calibration = get_year_from_time(loaded_times[0])
            return max(initial_year_loaded_calibration, self.forcing_function.initial_year)
        else:
            return self._initial_year_without_loading

    @property
    def _initial_year_without_loading(self):
        #  We select as initial_year the minimal year with both available forcing and available constraint
        return min(set(self.forcing_function.years).intersection(set(self.observation_constraint.years)))

    @property
    def final_year(self) -> int:
        return self.forcing_function.final_year

    @cached_property
    def times(self) -> np.ndarray[float]:
        return load_times(self.initial_year, self.final_year)

    @cached_property
    def years(self) -> list[int]:
        return list(range(self.initial_year, self.final_year + 1))

    @cached_property
    def time_to_index(self) -> dict[float, int]:
        return {time: i for i, time in enumerate(self.times)}

    def get_index_time(self, year: int) -> int:
        return self.time_to_index[get_time_from_year(year)]

    @cached_property
    def solve_data(self) -> tuple[list[dict[str, float]], list[np.ndarray], list[float]]:
        """
        Function that generates params, states, and error.
        Three main cases:
            -If self.loading_calibration is False, we sample parameters, solve state trajectories, compute error
            -If self.loading_calibration is True, we load parameters, and we either:
                -solve state trajectories, compute error (if self.loading_same_calibration is False)
                -load state trajectories, load error (if self.loading_same_calibration is True)
        """
        #  Load calibration and sample parameters
        if self.loading_calibration:
            params_vector_list, state_vectors_list, error_list, _ = self._loaded_calibration
        else:
            load_function = sampling_to_load_function[self.sampling]
            params_vector_list = load_function(self.dynamical_model, self.nb_samples, self.initial_year,
                                               self.get_forcings(self.initial_year), self.observation_constraint,
                                               self.sampling, self.solver_method)
            state_vectors_list, error_list = None, None
        #   Load params dictionary
        params_list = [self.dynamical_model.get_params(params_vector) for params_vector in params_vector_list]
        assert len(params_list) >= self.ensemble_size, \
            f'{self.path_manager.filename_to_load} only contains {len(params_list)} members'
        #  Solve states trajectories
        #  The dimension of states_list is: number of samples x number of time steps x number of states
        #   Load the final year to keep for loaded trajectory
        if self.loading_calibration:
            if self.loading_calibration_with_same_forcing:
                #  If we are loading the same calibration, we return the states_list and error_list
                return params_list, state_vectors_list, error_list
            else:
                #  Solve only the end trajectory (from the year self.final_year_for_loading + 1)
                state_vectors_list = parallelize(self.solve_end_trajectory, list(zip(params_list, state_vectors_list)))
                #  Replace errors by nan values, as we do not need to compute error when we load from other calibration
                error_list = [np.nan for _ in range(len(error_list))]
                return params_list, state_vectors_list, error_list
        else:
            #  Solve the full trajectory (parallelize here because this is called when we have lots of samples)
            state_vectors_list = parallelize(self.solve_full_trajectory, enumerate(params_list))
            #  Compute the error
            error_list = parallelize(self.compute_composite_rmse, list(zip(state_vectors_list, params_list)))
            # Sort the results, compute the ensemble sample ids (that correspond to the sample with the lowest error)
            sample_id_to_error = dict(list(enumerate(error_list)))
            sorted_sample_ids = [k for k, v in sorted(sample_id_to_error.items(), key=itemgetter(1))]
            ensemble_sample_ids = sorted_sample_ids[:self.ensemble_size]
            #  Order the solutions according to their error (the first correspond to the lowest error)
            ensemble_params_list = [params_list[i] for i in ensemble_sample_ids]
            ensemble_state_vectors_list = [state_vectors_list[i] for i in ensemble_sample_ids]
            ensemble_error_list = [error_list[i] for i in ensemble_sample_ids]
            return ensemble_params_list, ensemble_state_vectors_list, ensemble_error_list

    def solve_full_trajectory(self, sample_id_and_params: tuple[int, dict[str, float]]):
        """Solve the full trajectory, and print the progress at some specific steps"""
        sample_id, params = sample_id_and_params
        #  Print the progress at some specific steps
        nb_prints = 100 if self.ensemble_size == 1000000 else 10
        if (self.nb_samples >= 100) and (sample_id % (self.nb_samples // nb_prints) == 0):
            percent = (sample_id * 100 / nb_prints) // (self.nb_samples // nb_prints)
            log_info(f'solved ~{int(percent)}% of {self.nb_samples} samples')
        return SolverIvp.solve(self.dynamical_model, self.compute_initial_state(params), self.times, params, self.solver_method)

    def compute_initial_state(self, params) -> np.ndarray:
        """Compute the initial state"""
        years = [self.initial_year + i for i in range(self.nb_years_for_initial_state)]
        return self.dynamical_model.get_initial_state(years, params, self.observation_constraint)

    def solve_end_trajectory(self, params_and_state_vector: tuple[dict[str, float], np.ndarray]) -> np.ndarray:
        """
        Solve and return only the end of the trajectory (solve a trajectory with initial state in the middle of the trajectory).
        For instance, if final_year_for_loading = 1969, then the initial state is the value at time = 1970.0
        Warning: the forcing function must be defined for any year >= final_year_for_loading:
        Indeed at the first iteration the solver will require once the value of the forcing for the final_year_for_loading,
        then the value of the forcing for final_year + 1, i.e. 1970 in the example, to solve for 1970.0 < time <= 1971.0
        """
        params, state_vectors = params_and_state_vector
        #  Find the index of state vector that correspond to the initial_year_for_loading
        _, _, _, loaded_times = self._loaded_calibration
        initial_index = loaded_times.index(get_time_from_year(self.initial_year_for_loading))
        initial_state_vector = state_vectors[initial_index]
        #  Solve the trajectory
        return SolverIvp.solve(self.dynamical_model, initial_state_vector, self.times, params, self.solver_method)

    def compute_composite_rmse(self, state_vectors_and_params: tuple[np.ndarray, dict[str, float]]) -> float:
        state_vectors, params = state_vectors_and_params
        sum_of_squared_errors = 0
        nb_obs = 0
        #  Loop on the constraints
        for constraint_name in self.observation_constraint.constraint_names:
            for time, state_vector in zip(self.times, state_vectors):
                year = get_year_from_time(time)
                if year in self.observation_constraint.year_to_index:
                    constraint_value = self.observation_constraint.get_constraint_value(constraint_name, year)
                    if not np.isnan(constraint_value):
                        model_value = self.dynamical_model.get_variable(constraint_name, self.get_forcings(year),
                                                                        self.dynamical_model.create_states(
                                                                            state_vector), params)
                        assert isinstance(model_value, float)
                        sum_of_squared_errors += (model_value - constraint_value) ** 2
                        nb_obs += 1
        assert nb_obs > 0
        return np.sqrt(sum_of_squared_errors / nb_obs)

    def get_forcings(self, year: int) -> dict[str, float]:
        return self.forcing_function.get_forcings(get_time_from_year(year))

    ###########################################
    #
    #           Ensemble functions
    #
    ###########################################

    @property
    def ensemble_ids(self) -> list[int]:
        return list(range(self.ensemble_size))

    @cached_property
    def ensemble_id_to_params(self) -> dict[int, dict[str, float]]:
        return dict(list(enumerate(self.solve_data[0])))

    @cached_property
    def ensemble_id_to_state_vectors(self) -> dict[int, np.ndarray]:
        return dict(list(enumerate(self.solve_data[1])))

    @cached_property
    def ensemble_id_to_states_list(self) -> dict[int, list[dict[str, float]]]:
        return {ensemble_id: [self.dynamical_model.create_states(state_vector) for state_vector in state_vectors]
                for ensemble_id, state_vectors in self.ensemble_id_to_state_vectors.items()}

    @cached_property
    def ensemble_id_to_error(self) -> dict[int, float]:
        return dict(list(enumerate(self.solve_data[2])))

    def get_model_variable(self, year: int, variable_name: str, ensemble_id: int) -> float:
        params = self.ensemble_id_to_params[ensemble_id]
        states = self.ensemble_id_to_states_list[ensemble_id][self.get_index_time(year)]
        return self.dynamical_model.get_variable(variable_name, self.get_forcings(year), states, params)

    def get_variable(self, variable_name: str, ensemble_id: int, forcing_value: float,
                     state_vector: np.ndarray) -> float:
        forcings = self.forcing_function.create_forcings(np.array([forcing_value]))
        states = self.dynamical_model.create_states(state_vector)
        params = self.ensemble_id_to_params[ensemble_id]
        return self.dynamical_model.get_variable(variable_name, forcings, states, params)

    def get_all_variables(self, variable_name: str, initial_year: int, final_year: int):
        times = [get_time_from_year(year) for year in range(initial_year, final_year + 1)]
        indices_to_keep = [j for j, time in enumerate(self.times) if
                           initial_year <= get_year_from_time(time) <= final_year]
        all_variables = []
        for ensemble_id in self.ensemble_ids:
            params = self.ensemble_id_to_params[ensemble_id]
            states_list = self.ensemble_id_to_states_list[ensemble_id]
            states_list = [states_list[j] for j in indices_to_keep]
            forcings_list = self.forcing_function.get_forcings_list(times)
            assert len(forcings_list) == len(states_list)
            variables = [self.dynamical_model.get_variable(variable_name, forcings, states, params)
                         for forcings, states in zip(forcings_list, states_list)]
            all_variables.append(variables)
        return all_variables

    ###########################################
    #
    #           Save and load calibration
    #
    ###########################################
    @property
    def loading_calibration_with_same_forcing(self) -> bool:
        if self.loading_calibration:
            return (self.filename_manager.forcing_function_name
                    == self.path_manager.filename_manager_to_load.forcing_function_name)
        else:
            return False

    def save_calibration(self) -> None:
        model_filepath_to_save = self.path_manager.filepath_to_save
        if op.isfile(model_filepath_to_save):
            log_info('This experiment has already been saved before')
        else:
            log_info('Saving calibration')
            #  Create folder is needed
            self.path_manager.create_folder_if_needed()
            #  Save params
            params_list, state_vectors_list, error_list = self.solve_data
            parameter_name_to_values = {}
            for parameter_name in self.dynamical_model.parameter_names:
                parameter_name_to_values[parameter_name] = [params[parameter_name] for params in params_list]
            df = pd.DataFrame.from_dict(parameter_name_to_values)
            df = df.loc[:, self.dynamical_model.parameter_names]
            #  Save error
            df['Error'] = error_list
            # Save trajectory
            d = OrderedDict()
            for i, time in enumerate(self.times):
                for j, state_name in enumerate(self.dynamical_model.state_names):
                    d[state_name + str(time)] = [state_vectors[i][j] for state_vectors in state_vectors_list]
            df_states = pd.DataFrame.from_dict(d)
            df_states.index = df.index
            df = pd.concat([df, df_states], axis=1)
            df.to_csv(model_filepath_to_save, index=False)
            assert op.isfile(model_filepath_to_save)

    @cached_property
    def _loaded_calibration(self) -> tuple[list[dict[str, float]], list[np.ndarray], list[float], list[float]]:
        return self.load_calibration()

    def load_calibration(self) -> tuple[list[dict[str, float]], list[np.ndarray], list[float], list[float]]:
        model_filepath_to_load = self.path_manager.filepath_to_load
        log_info(f'Loading from {op.basename(model_filepath_to_load)} with settings {self.filename_manager.folder}')
        assert op.isfile(model_filepath_to_load), model_filepath_to_load
        df = pd.read_csv(model_filepath_to_load, nrows=self.ensemble_size)
        assert len(df) == self.ensemble_size
        params_vector = df.loc[:, self.dynamical_model.parameter_names].values
        #  Load error
        error_list = df['Error'].to_list()
        index_error_column = list(df.columns).index('Error')
        assert index_error_column == len(self.dynamical_model.parameter_names), \
            'Problem in the number of columns. Maybe more or less parameters than desired are in the file'
        #  Load state trajectory
        nb_columns_for_params_and_error = len(self.dynamical_model.parameter_names) + 1
        df = df.iloc[:, nb_columns_for_params_and_error:]
        state_vectors_list = np.array_split(df.values, len(df.columns) // self.dynamical_model.nb_states, axis=1)
        state_vectors_list = list(np.moveaxis(np.array(state_vectors_list), 0, -1))
        state_vectors_list = [a.transpose() for a in state_vectors_list]
        #  Load time list
        times = [float(c.split(self.dynamical_model.state_names[0])[1]) for c in
                 df.columns[::self.dynamical_model.nb_states]]
        assert len(params_vector) == len(state_vectors_list) == len(error_list)
        return params_vector, state_vectors_list, error_list, times

    @property
    def name(self) -> str:
        if self.loading_calibration:
            return self.dynamical_model.name + ' forced by ' + self.forcing_function.name \
                + ' using\nparameters from {}'.format(self.path_manager.filename_to_load)
        else:
            return self.dynamical_model.name + ' forced by ' + self.forcing_function.name \
                + ' using\nthe constraint {}'.format(self.observation_constraint.name)
