from collections import OrderedDict

import numpy as np
import pytest

from bifurcation.bifurcation_data.bifurcation_data import BifurcationData
from calibration.dynamical_model.one_state.tiphyc_annual import DynamicalModelTipHycAnnual
from calibration.forcing_function.rain.watershed_rain_forcing_function import RainObsForcingFunction
from calibration.utils_calibration.solve import SolverMethod

watershed_name = 'Dargol_Kakassi'


@pytest.fixture
def dynamical_model():
    forcing_function = RainObsForcingFunction(watershed_name)
    return DynamicalModelTipHycAnnual(forcing_function)


@pytest.fixture
def min_forcing():
    return 300.


@pytest.fixture
def max_forcing():
    return 400.


def test_bifurcation_data_equal(min_forcing, max_forcing):
    for is_bistable in [True, False][:]:
        if is_bistable:
            stability_ranges = (388., np.nan), (np.array([0.00838381]), np.array([np.nan]))
            stability_detection = 392.
        else:
            stability_ranges = (np.nan, np.nan), (np.array([np.nan]), np.array([np.nan]))
            stability_detection = OrderedDict(
                [(300.0, np.array([0.00963327])), (301.0, np.array([0.00966578])), (302.0, np.array([0.00969834])),
                 (303.0, np.array([0.00973095])), (304.0, np.array([0.00976359])), (305.0, np.array([0.00979625])),
                 (306.0, np.array([0.00982894])), (307.0, np.array([0.00986164])), (308.0, np.array([0.00989436])),
                 (309.0, np.array([0.00992711])), (310.0, np.array([0.00995989])), (311.0, np.array([0.00999269])),
                 (312.0, np.array([0.01002554])), (313.0, np.array([0.01005843])), (314.0, np.array([0.01009138])),
                 (315.0, np.array([0.01012439])), (316.0, np.array([0.01015749])), (317.0, np.array([0.01018871])),
                 (318.0, np.array([0.01021992])), (319.0, np.array([0.01025137])), (320.0, np.array([0.010283])),
                 (321.0, np.array([0.01031478])), (322.0, np.array([0.01034668])), (323.0, np.array([0.01037867])),
                 (324.0, np.array([0.01041073])), (325.0, np.array([0.01044284])), (326.0, np.array([0.010475])),
                 (327.0, np.array([0.01050719])), (328.0, np.array([0.01053941])), (329.0, np.array([0.01057166])),
                 (330.0, np.array([0.01060393])), (331.0, np.array([0.01063623])), (332.0, np.array([0.01066856])),
                 (333.0, np.array([0.01070093])), (334.0, np.array([0.01073335])), (335.0, np.array([0.01076582])),
                 (336.0, np.array([0.01079835])), (337.0, np.array([0.01083095])), (338.0, np.array([0.01086365])),
                 (339.0, np.array([0.01088985])), (340.0, np.array([0.01092009])), (341.0, np.array([0.01095334])),
                 (342.0, np.array([0.01098966])), (343.0, np.array([0.01101982])), (344.0, np.array([0.01105023])),
                 (345.0, np.array([0.01108086])), (346.0, np.array([0.01111165])), (347.0, np.array([0.01114259])),
                 (348.0, np.array([0.01117363])), (349.0, np.array([0.01120476])), (350.0, np.array([0.01123596])),
                 (351.0, np.array([0.0112672])), (352.0, np.array([0.01129848])), (353.0, np.array([0.0113298])),
                 (354.0, np.array([0.01136113])), (355.0, np.array([0.01139247])), (356.0, np.array([0.01142383])),
                 (357.0, np.array([0.0114552])), (358.0, np.array([0.01148658])), (359.0, np.array([0.01151797])),
                 (360.0, np.array([0.01154937])), (361.0, np.array([0.01158079])), (362.0, np.array([0.01161223])),
                 (363.0, np.array([0.01164369])), (364.0, np.array([0.01167519])), (365.0, np.array([0.01170672])),
                 (366.0, np.array([0.01173829])), (367.0, np.array([0.01176992])), (368.0, np.array([0.01180162])),
                 (369.0, np.array([0.01183338])), (370.0, np.array([0.01185493])), (371.0, np.array([0.01188892])),
                 (372.0, np.array([0.01192331])), (373.0, np.array([0.01195223])), (374.0, np.array([0.01198135])),
                 (375.0, np.array([0.01201062])), (376.0, np.array([0.01204003])), (377.0, np.array([0.01206954])),
                 (378.0, np.array([0.01209915])), (379.0, np.array([0.01212882])), (380.0, np.array([0.01215855])),
                 (381.0, np.array([0.01218832])), (382.0, np.array([0.01221813])), (383.0, np.array([0.01224794])),
                 (384.0, np.array([0.01227777])), (385.0, np.array([0.0123076])), (386.0, np.array([0.01233743])),
                 (387.0, np.array([0.01236724])), (388.0, np.array([0.01239704])), (389.0, np.array([0.01242682])),
                 (390.0, np.array([0.01245657])), (391.0, np.array([0.0124863])), (392.0, np.array([0.01251601])),
                 (393.0, np.array([0.01254568])), (394.0, np.array([0.01257532])), (395.0, np.array([0.01260493])),
                 (396.0, np.array([0.01263451])), (397.0, np.array([0.01266405])), (398.0, np.array([0.01269357])),
                 (399.0, np.array([0.01272305])), (400.0, np.array([0.01275249]))])
        bifurcation_data1 = BifurcationData(stability_ranges, stability_detection, min_forcing, max_forcing)
        assert bifurcation_data1 == bifurcation_data1
        bifurcation_data2 = BifurcationData(stability_ranges, stability_detection, min_forcing + 1, max_forcing)
        assert bifurcation_data1 != bifurcation_data2

def test_read_write_specific_bug():
    forcing_function = RainObsForcingFunction('Gorouol_Alcongui')
    dynamical_model = DynamicalModelTipHycAnnual(forcing_function)
    params = {'c_croiss': 0.4902329330447865, 'i_croiss': 557.9974777248075, 'c_max': 1.0, 'c_mort': 0.5021776518592721,
              'i_mort': 176.8519081194406, 'mu_c': 0.0047718667951692, 'p_ini': 23.02137604955668,
              'p_0max': 630.7350737760418, 'a': 1.5, 'b': 8.0, 'skc': 8.164632507455183, 'Ke_max': 0.9}
    min_forcing = 430.
    max_forcing = 440.
    bifurcation_data = BifurcationData.from_dynamical_model(dynamical_model, params,
                                                            min_forcing, max_forcing, SolverMethod.RK45)
    s = bifurcation_data.to_series()
    bifurcation_data2 = BifurcationData.from_series(s, min_forcing, max_forcing)
    assert bifurcation_data == bifurcation_data2
