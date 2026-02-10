import numpy as np

from bifurcation.bifurcation_data.repulsor_functions import repulsors_for_bistable_forcings
from calibration.dynamical_model.one_state.tiphyc_annual import DynamicalModelTipHycAnnual
from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction
from calibration.utils_calibration.solve import SolverMethod

watershed_name = 'Dargol_Kakassi'


def test_repulsor_specific_case():
    forcing_function = RainObsForcingFunction('Dargol_Kakassi')
    dynamical_model = DynamicalModelTipHycAnnual(forcing_function)
    params = {'c_croiss': 0.3304891247698426, 'i_croiss': 261.60497612160066, 'c_max': 1.0,
              'c_mort': 1.7066257707123536, 'i_mort': 72.21358427502985, 'mu_c': 0.0041709486631138,
              'p_ini': 116.64909602168304, 'p_0max': 607.7150479970786, 'a': 1.5, 'b': 8.0, 'skc': 2.300304811131835,
              'Ke_max': 0.9}
    forcing_to_repulsor = repulsors_for_bistable_forcings(dynamical_model, params, [830., 1024.], SolverMethod.RK45)
    assert np.round(forcing_to_repulsor[830.], 3) == 0.056
    assert np.round(forcing_to_repulsor[1024.], 3) == 0.104
