import numpy as np

from continuation.example.tiphyc_annual_model import derivative
from continuation.pycont.continuation import pseudoArclengthContinuationOneDirection


# Define the derivative of the tiphyc model
def G(u, p):
    return derivative(u, p)

# Initial guess
u0 = np.array([0.15])
p0 = 750.0

u0 = np.array([0.01])
p0 = 0.01

# u0 = np.array([0.7])
# p0 = 1990

# Run continuation
print(u0, p0)
u_path, p_path = pseudoArclengthContinuationOneDirection(
    G,
    u0, p0,
    ds_min=0.0000001,
    ds_max=1.,
    ds_0=0.2,
    # N=100000,
    N=10,
)
u_path = u_path.flatten()


print(u_path)
print(p_path)