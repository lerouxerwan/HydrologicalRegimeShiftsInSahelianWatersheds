from calibration.utils_calibration.load_sample_v1 import load_sample_parameters
from calibration.utils_calibration.load_sample_v2 import load_params_vector_list_sample_v2
from calibration.utils_calibration.sampling import Sampling

sampling_to_load_function = {
    Sampling.V1: load_sample_parameters,
    Sampling.V2_INITIAL: load_params_vector_list_sample_v2,
}