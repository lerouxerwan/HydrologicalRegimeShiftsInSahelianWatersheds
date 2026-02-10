The file example_calibration.py contains the following code:

```python
from calibration.calibration import Calibration
from calibration.calibration_visualisation import plot_trajectory_ensemble
from calibration.dynamical_model.one_state.tiphyc_annual import DynamicalModelTipHycAnnual
from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction
from calibration.observation_constraint.runoff.runoff_coefficient_constraint import RunoffCoefficientObservationConstraint

#  Settings (forcing_function, dynamical_model, and observations_constraint)
watershed_name = "Dargol_Kakassi"
observation_constraint = RunoffCoefficientObservationConstraint(watershed_name, 2015)
forcing_function = RainObsForcingFunction(watershed_name)
dynamical_model = DynamicalModelTipHycAnnual(forcing_function)
#  Run and plot calibration
calibration = Calibration(observation_constraint, forcing_function, dynamical_model,
                          nb_samples=100, ensemble_size=10, show=True)
plot_trajectory_ensemble(calibration)
```

which generates the following plot:

![alt text](example_calibration.png?raw=true)

