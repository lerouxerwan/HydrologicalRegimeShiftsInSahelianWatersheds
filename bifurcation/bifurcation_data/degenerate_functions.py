from bifurcation.bifurcation_data.attractor_functions import get_lower_attractor
from calibration.dynamical_model.dynamical_model import DynamicalModel
from calibration.utils_calibration.solve import SolverMethod
from tests.bifurcation.test_stability_ranges import solver_method


def compute_is_degenerate(dynamical_model: DynamicalModel, params: dict[str, float], solver_method: SolverMethod) -> bool:
    attractor = get_lower_attractor(dynamical_model, params, 2000., solver_method)
    return attractor[0] < 0.1
