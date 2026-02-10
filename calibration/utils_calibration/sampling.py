from enum import Enum


class Sampling(Enum):
    V1 = "v1"
    V2_INITIAL = "v2i"


sampling_to_str = {
    Sampling.V1: "v1",
    Sampling.V2_INITIAL: "v2i",
}
