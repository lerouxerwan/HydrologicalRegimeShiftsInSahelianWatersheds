from calibration.calibration import Calibration
from continuation.get_continuation import get_continuation_parallel, compute_continuation
from projects.paper_model.utils_paper_model import get_calibration


def main_get_dargol_special_case():
    watershed_name = 'Dargol_Kakassi'
    ensemble_id = 414
    # forcing = 600.
    forcing = 1.
    get_end_of_continuation_for_special_case(watershed_name, ensemble_id, forcing)

def main_get_sirba_special_case():
    watershed_name = 'Dargol_Kakassi'
    ensemble_id = 100
    forcing = 1.
    get_end_of_continuation_for_special_case(watershed_name, ensemble_id, forcing)

def get_end_of_continuation_for_special_case(watershed_name: str, ensemble_id: int, forcing: float):
    calibration = get_calibration(watershed_name)
    params = calibration.ensemble_id_to_params[ensemble_id]
    compute_continuation(calibration.dynamical_model, params, forcing, 2000.)

if __name__ == '__main__':
    # main_get_dargol_special_case()
    main_get_sirba_special_case()