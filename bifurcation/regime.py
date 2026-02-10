from collections import Counter
from enum import Enum

import numpy as np

from bifurcation.bifurcation import Bifurcation
from bifurcation.bifurcation_data.bifurcation_data import BifurcationData
from calibration.calibration import Calibration


class Regime(Enum):
    """Runoff coefficient regimes"""
    lower = 0
    upper = 1
    unknown = 2

regime_to_name = {
    area: f'"{s}  runoff coefficient regime"'
    for s, area in zip(['Low', 'High'], [Regime.lower, Regime.upper])
}


class RegimeDef(Enum):
    threshold = 0
    basin_attraction = 1

regime_def_to_name = {
    RegimeDef.threshold: "regime_defined_with_threshold",
    RegimeDef.basin_attraction: "regime_defined_with_basin_attraction",
}



def compute_regime(bifurcation: Bifurcation, calibration: Calibration, ensemble_id: int, year: int,
                   regime_def: RegimeDef = RegimeDef.threshold) -> Regime:
    bifurcation_data = bifurcation.ensemble_id_to_bifurcation_data[ensemble_id]
    state_value = calibration.get_model_variable(year, calibration.dynamical_model.unique_state_name, ensemble_id)
    forcing = calibration.forcing_function.year_to_forcing[year]
    if bifurcation_data.is_bistable:
        if regime_def is RegimeDef.threshold:
            return compute_bistable_regime_with_threshold(bifurcation_data, state_value, forcing)
        elif regime_def is RegimeDef.basin_attraction:
            return compute_bistable_regime_with_basin_attraction(bifurcation_data, state_value, forcing)
        else:
            raise ValueError(regime_def)
    else:
        return Regime.unknown


def compute_bistable_regime_with_threshold(bifurcation_data: BifurcationData, state_value: float, forcing: float) -> Regime:
    if state_value < bifurcation_data.shift_range.middle_state_value:
        #  Upper regime (that corresponds to the lower area for the state value)
        return Regime.upper
    else:
        #  Lower regime (that corresponds to the upper area for the state value)
        return Regime.lower


def compute_bistable_regime_with_basin_attraction(bifurcation_data: BifurcationData, state_value: float, forcing: float) -> Regime:
    stability_forcing_range = bifurcation_data.stability_ranges[0]
    lower_bound, upper_bound = stability_forcing_range
    if forcing <= lower_bound:
        #  Upper regime (that corresponds to the lower area for the state value)
        return Regime.upper
    elif forcing >= upper_bound:
        #  Lower regime (that corresponds to the upper area for the state value)
        return Regime.lower
    else:
        # In the bistability range, we rely on repulsors to assess the regime
        forcing_list_with_repulsor = list(sorted(bifurcation_data.forcing_to_repulsor.keys()))
        index_closest = np.argmin([np.abs(forcing - forcing_with_repulsor) for forcing_with_repulsor in forcing_list_with_repulsor])
        repulsor = bifurcation_data.forcing_to_repulsor[forcing_list_with_repulsor[index_closest]]

        # if index_closest == 0:
        # forcing_just_below, forcing_just_above = float(math.floor(forcing)), float(math.ceil(forcing))
        #
        # if forcing_just_below <= :
        #     repulsor = bifurcation_data.forcing_to_repulsor[forcing_just_above]
        # elif forcing_just_above not in bifurcation_data.forcing_to_repulsor:
        #     repulsor = bifurcation_data.forcing_to_repulsor[forcing_just_below]
        # else:
        #     forcing_just_below, forcing_just_above = float(math.floor(forcing)), float(math.ceil(forcing))
        #
        #     # If the two repulsors (lower and upper) exists, then we do some linear interpolation
        #     # lower_weight=1 if forcing=lower_forcing, lower_weight=0 if forcing=upper_forcing
        #     weight_just_below = 1 - (forcing - forcing_just_below)
        #     weight_just_above = 1 - weight_just_below
        #     repulsor = bifurcation_data.forcing_to_repulsor[forcing_just_below] * weight_just_below
        #     repulsor += bifurcation_data.forcing_to_repulsor[forcing_just_above] * weight_just_above
        # Classify the state_value with respect to the repulsor
        if state_value < repulsor:
            #  Upper regime (that corresponds to the lower area for the state value)
            return Regime.upper
        else:
            #  Lower regime (that corresponds to the upper area for the state value)
            return Regime.lower


def compute_regimes(bifurcation: Bifurcation, calibration: Calibration, year: int,
                    regime_def: RegimeDef = RegimeDef.threshold) -> list[Regime]:
    return [compute_regime(bifurcation, calibration, ensemble_id, year, regime_def) for ensemble_id in calibration.ensemble_ids]


def compute_regime_counter(bifurcation: Bifurcation, calibration: Calibration, year: int, regime_def: RegimeDef = RegimeDef.threshold) -> Counter:
    return Counter(compute_regimes(bifurcation, calibration, year, regime_def))


def compute_percentage_regime(bifurcation: Bifurcation, calibration: Calibration, year: int, regime: Regime, regime_def: RegimeDef = RegimeDef.threshold) -> float:
    c = compute_regime_counter(bifurcation, calibration, year, regime_def)
    return 100 * c[regime] / calibration.ensemble_size
