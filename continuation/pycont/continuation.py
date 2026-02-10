from typing import Optional

import numpy as np
from numpy.linalg import norm

from continuation.pycont.PseudoArclengthContinuation import continuation, computeTangent
from utils.utils_run import random_seed


def pseudoArclengthContinuationOneDirection(G, u0, p0, ds_min, ds_max, ds_0, N, p_max, tolerance=1.e-10,
                                            epsilon: Optional[float] = None):
    assert isinstance(u0, float), type(u0)
    assert isinstance(p0, float), type(p0)
    # Create gradient functions
    r_diff = 1.e-8
    Gu_v = lambda u, p, v: (G(u + r_diff * v, p) - G(u, p)) / r_diff
    Gp = lambda u, p: (G(u, p + r_diff) - G(u, p)) / r_diff

    # Compute the initial tangent to the curve
    u0 = np.array([u0])
    M = u0.size
    np.random.seed(random_seed)
    rng = np.random.RandomState()
    random_tangent = rng.normal(0.0, 1.0, M+1)
    tangent = computeTangent(u0, p0, Gu_v, Gp, random_tangent/norm(random_tangent), M, tolerance)

    # Do continuation in both directions of the tangent
    ds = ds_0
    if tangent[0] > 0:
        sign = 1
    else:
        sign = -1
    return continuation(G, Gu_v, Gp, u0, p0, sign * tangent, ds_min, ds_max, ds, N, p_max,
                                  a_tol=tolerance, max_it=10, epsilon=epsilon)


