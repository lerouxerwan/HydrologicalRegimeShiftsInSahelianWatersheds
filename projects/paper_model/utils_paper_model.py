from calibration.calibration import Calibration
from calibration.dynamical_model.one_state.tiphyc_annual import DynamicalModelTipHycAnnual
from calibration.dynamical_model.one_state.tiphyc_annual_without_s import DynamicalModelTipHycAnnualWithoutS
from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction
from calibration.observation_constraint.runoff.runoff_coefficient_constraint import \
    RunoffCoefficientObservationConstraint
from calibration.utils_calibration.sampling import Sampling
from calibration.utils_calibration.solve import SolverMethod

sahel_watershed_names = ['Gorouol_Alcongui', 'Dargol_Kakassi', 'Sirba_GarbeKourou', 'Nakanbe_Wayen']

year_before = 1965
year_after = 2014
years_regime_shift = list(range(year_before, year_after + 1))

dynamical_model_type = [DynamicalModelTipHycAnnual, DynamicalModelTipHycAnnualWithoutS][0]


def get_ylabel(i: int) -> str:
    suffix = 'ensemble member\nin the "High runoff coefficient regime" (%)' if i == 0 else f'regime shift with respect to {year_before} (%)'
    return 'Percentage of ' + suffix


def get_obs_forcing_function(watershed_name: str):
    return RainObsForcingFunction(watershed_name)


def get_calibration(watershed_name: str, fast: bool = False, loading: bool = True, 
                    sampling: Sampling = Sampling.V2_INITIAL, solver_method: SolverMethod = SolverMethod.LSODA) -> Calibration:
    ensemble_size, nb_samples = (10, 1000000) if fast else (1000, 1000000)
    observation_constraint = RunoffCoefficientObservationConstraint(watershed_name, 2015)
    forcing_function = get_obs_forcing_function(watershed_name)
    dynamical_model = dynamical_model_type(forcing_function)
    return Calibration(observation_constraint, forcing_function,
                       dynamical_model, nb_samples, ensemble_size,
                       nb_years_for_initial_state=5, loading_calibration=loading,
                       sampling=sampling, solver_method=solver_method)
