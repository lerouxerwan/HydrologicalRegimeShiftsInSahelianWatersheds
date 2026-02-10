from collections import OrderedDict
from dataclasses import dataclass, field
from functools import cached_property
from typing import Union

import numpy as np
import pandas as pd

from bifurcation.bifurcation_data.attractor_functions import compute_forcing_to_attractors
from bifurcation.bifurcation_data.bistability_functions import compute_is_bistable
from bifurcation.bifurcation_data.repulsor_functions import compute_empty_forcing_to_repulsor
from bifurcation.bifurcation_data.stability_detection_function import compute_stability_detection
from bifurcation.bifurcation_data.stability_range_functions import compute_stability_ranges
from bifurcation.shift_range.shift_range import ShiftRange
from bifurcation.shift_range.shift_range_functions import compute_shift_range
from calibration.dynamical_model.dynamical_model import DynamicalModel
from calibration.utils_calibration.solve import SolverMethod


@dataclass
class BifurcationData(object):
    """Class to store bifurcation data (attractors, repulsors...)"""
    stability_ranges: tuple[tuple[float, float], tuple[np.ndarray, np.ndarray]]
    stability_detection: Union[float, dict[float, np.ndarray]]
    min_forcing: float
    max_forcing: float
    forcing_to_attractors: dict[float, list[np.ndarray]] = field(default_factory=dict)
    forcing_to_repulsor: dict[float, float] = field(default_factory=dict)

    def __post_init__(self):
        #  Check data
        self.check_type()

    @cached_property
    def shift_range(self) -> ShiftRange:
        return compute_shift_range(self.is_bistable, self.stability_ranges, self.forcing_to_attractors,
                                   self.min_forcing, self.max_forcing)

    @cached_property
    def is_bistable(self) -> bool:
        return compute_is_bistable(self.stability_detection)

    @classmethod
    def from_dynamical_model(cls, dynamical_model: DynamicalModel, params: dict[str, float], min_forcing: float,
                             max_forcing: float, solver_method: SolverMethod):
        #  Run stability detection and bistable
        stability_detection = compute_stability_detection(dynamical_model, params, min_forcing, max_forcing, solver_method)
        forcing_to_attractors = compute_forcing_to_attractors(dynamical_model, params,
                                                              stability_detection, min_forcing, max_forcing, solver_method)
        stability_ranges = compute_stability_ranges(forcing_to_attractors, stability_detection, min_forcing,
                                                    max_forcing)
        # By default, we do not compute the repulsor anymore, instead we save np.nan values
        forcing_to_repulsor = compute_empty_forcing_to_repulsor(stability_ranges, max_forcing)
        # is_bistable = compute_is_bistable(stability_detection)
        # forcing_to_repulsor = compute_forcing_to_repulsor(dynamical_model, params, stability_ranges,
        #                                                   is_bistable, max_forcing)
        return cls(stability_ranges, stability_detection, min_forcing, max_forcing,
                   forcing_to_attractors, forcing_to_repulsor)

    def to_series(self) -> pd.Series:
        #  First columns the ranges
        columns = ['ranges {}'.format(i) for i in range(4)]
        data = list(self.stability_ranges[0]) + [a[0] for a in self.stability_ranges[1]]
        #  Add one value for the detection
        data += [np.nan] if isinstance(self.stability_detection, dict) else [self.stability_detection]
        columns += ['detection']
        #  Add forcing_to_attractors
        length_between_all_forcings = int(self.max_forcing - self.min_forcing + 1)
        if self.forcing_to_attractors:
            attractors_data = []
            for item in self.forcing_to_attractors.items():
                attractors_values = '-'.join(str(a[0]) for a in item[1])
                attractors_data.append(str(item[0]) + '-' + attractors_values)
        else:
            attractors_data = [np.nan] * length_between_all_forcings
        data += attractors_data
        columns += ['attractors {}'.format(i) for i in range(length_between_all_forcings)]
        #  Add repulsors
        if self.forcing_to_repulsor:
            repulsor_data = []
            for forcing in np.arange(self.min_forcing, self.max_forcing + 1):
                if forcing in self.forcing_to_repulsor:
                    repulsor_value = self.forcing_to_repulsor[forcing]
                    repulsor_data.append(str(forcing) + '-' + str(repulsor_value))
                else:
                    repulsor_data.append(np.nan)
        else:
            repulsor_data = [np.nan] * length_between_all_forcings
        data += repulsor_data
        columns += ['repulsor {}'.format(i) for i in range(length_between_all_forcings)]
        return pd.Series(index=columns, data=data)

    @classmethod
    def from_series(cls, series: pd.Series, min_forcing: float, max_forcing: float):
        #  Start of the series
        start_series = series.iloc[:5].values
        forcing_ranges = (float(start_series[0]), float(start_series[1]))
        state_ranges = (np.array([float(start_series[2])]), np.array([float(start_series[3])]))
        stability_ranges = (forcing_ranges, state_ranges)
        stability_detection = float(start_series[4])
        #  Load forcing_to_attractor
        forcing_to_attractors = dict()
        ind = series.index.str.contains('attractors')
        for v in series.loc[ind].values:
            if isinstance(v, str) and ('-' in v):
                forcing, *states = v.split('-')
                forcing_to_attractors[float(forcing)] = [np.array([float(state)]) for state in states]
        # Load repulsor
        forcing_to_repulsor = OrderedDict()
        ind = series.index.str.contains('repulsor')
        for v in series.loc[ind].values:
            if isinstance(v, str):
                if '-' in v:
                    forcing, repulsor = v.split('-')
                    forcing_to_repulsor[float(forcing)] = float(repulsor)
        # Create an OrderedDict for stability detection if needed
        if np.isnan(stability_detection):
            forcing_list = sorted(list(forcing_to_attractors.keys()))
            stability_detection = OrderedDict()
            for forcing in forcing_list:
                stability_detection[forcing] = forcing_to_attractors[forcing][0]
        return cls(stability_ranges, stability_detection, min_forcing, max_forcing, forcing_to_attractors,
                   forcing_to_repulsor)

    def check_type(self):
        assert isinstance(self.stability_detection, (float, dict))
        if isinstance(self.stability_detection, dict):
            for key, value in self.stability_detection.items():
                assert isinstance(key, float)
                assert isinstance(value, np.ndarray), "{} is of type {}".format(value, type(value))
                assert isinstance(value[0], float)
        for key, values in self.forcing_to_attractors.items():
            assert isinstance(key, float)
            assert isinstance(values, list)
            for value in values:
                assert isinstance(value, np.ndarray)
                assert isinstance(value[0], float)
        for key, value in self.forcing_to_repulsor.items():
            assert isinstance(key, float)
            assert isinstance(value, float)
        assert isinstance(self.is_bistable, bool)
        assert isinstance(self.stability_ranges, tuple)
        assert isinstance(self.stability_ranges[0], tuple)
        assert all([isinstance(f, float) for f in self.stability_ranges[0]])
        assert isinstance(self.stability_ranges[1], tuple)
        assert all([isinstance(f, np.ndarray) for f in self.stability_ranges[1]])
        assert all([len(f) == 1 for f in self.stability_ranges[1]])

    def __eq__(self, other):
        try:
            #  Assert min_forcing and max_forcing are the same
            assert self.min_forcing == other.min_forcing
            assert self.max_forcing == other.max_forcing
            #  Assert that stability detection attributes are equal
            if isinstance(self.stability_detection, float):
                np.testing.assert_almost_equal(self.stability_detection, other.stability_detection)
            else:
                for key, value in self.stability_detection.items():
                    other_value = other.stability_detection[key]
                    np.testing.assert_almost_equal(other_value, value)
            #  Assert that the forcing_to_attractor attributes are equal
            for key, attractors in self.forcing_to_attractors.items():
                other_attractors = other.forcing_to_attractors[key]
                assert len(attractors) == len(other_attractors)
                for attractor, other_attractor in zip(attractors, other_attractors):
                    np.testing.assert_almost_equal(attractor, other_attractor)
            #  Assert that the repulsor attributes are equal
            #  We do not apply this comparison anymore, since we do not compute repulsors
            # for key, repulsor in self.forcing_to_repulsor.items():
            #     other_repulsor = other.forcing_to_repulsor[key]
            #     assert repulsor == other_repulsor
            #  Assert that the stability_ranges are equal
            np.testing.assert_almost_equal(self.stability_ranges[0], other.stability_ranges[0])
            np.testing.assert_almost_equal(np.array(self.stability_ranges[1]), np.array(other.stability_ranges[1]))
        except AssertionError:
            return False
        return True