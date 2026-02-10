import sys
import time

from bifurcation.bifurcation import Bifurcation
from calibration.utils_calibration.sampling import Sampling
from calibration.utils_calibration.solve import SolverMethod
from projects.paper_model.utils_paper_model import get_calibration, sahel_watershed_names
from tests.bifurcation.test_stability_ranges import solver_method
from utils.utils_log import log_info


def main(fast, loading_calibration, watershed_name: str, sampling=Sampling.V1, solver_method=SolverMethod.RK45):
    step1 = time.time()
    calibration = get_calibration(watershed_name, fast=fast, loading=loading_calibration,
                                  sampling=sampling, solver_method=solver_method)
    step2 = time.time()
    print(f'Duration calibration={step2 - step1}s')
    _ = Bifurcation(calibration).bifurcation_data_list
    step3 = time.time()
    print(f'Duration bifurcation={step3 - step2}s')


def main_calibration():
    if len(sys.argv) > 1:
        # Settings to run on online server
        fast = False
        load_from_file = False
        assert len(sys.argv) == 4
        indices = [int(s) for s in sys.argv[1:]]
        sampling, solver_method, watershed_name = get_arguments(indices)
    else:
        # Settings to run on local computer
        fast = False
        load_from_file = False
        watershed_name = sahel_watershed_names[0]
        sampling = Sampling.V2_INITIAL
        solver_method = SolverMethod.LSODA
    main(fast, load_from_file, watershed_name, sampling, solver_method)


def get_arguments(indices):
    i1, i2, i3 = indices
    watershed_name = sahel_watershed_names[i1]
    sampling = [Sampling.V1, Sampling.V2_INITIAL][i2]
    solver_method = [SolverMethod.RK45, SolverMethod.LSODA][i3]
    return sampling, solver_method, watershed_name


if __name__ == '__main__':
    main_calibration()
