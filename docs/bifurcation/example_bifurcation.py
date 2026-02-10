from bifurcation.bifurcation import Bifurcation
from bifurcation.bifurcation_visualisation import plot_bifurcation_diagram
from calibration.calibration import Calibration
from calibration.dynamical_model.one_state.tiphyc_annual import DynamicalModelTipHycAnnual
from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction
from calibration.observation_constraint.runoff.runoff_coefficient_constraint import \
    RunoffCoefficientObservationConstraint

# Settings (forcing_function, dynamical_model, and observations_constraint)
watershed_name = 'Dargol_Kakassi'
observation_constraint = RunoffCoefficientObservationConstraint(watershed_name, 2015)
forcing_function = RainObsForcingFunction(watershed_name)
dynamical_model = DynamicalModelTipHycAnnual(forcing_function)
# Load calibration and bifurcation
calibration = Calibration(observation_constraint, forcing_function,
                          dynamical_model, nb_samples=1000000, ensemble_size=2, loading_calibration=True, show=True)
bifurcation = Bifurcation(calibration)
# Plot bifurcation diagram for a specific ensemble member
plot_bifurcation_diagram(bifurcation, ensemble_id=1, variable_name='c', min_forcing=1., max_forcing=1000.)

