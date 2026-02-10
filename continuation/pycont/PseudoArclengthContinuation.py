import math
from typing import Optional

import numpy as np
from numpy.linalg import norm, solve
from numpy.random import RandomState
from scipy.optimize import newton_krylov
from scipy.sparse.linalg import LinearOperator, gmres, lgmres



def continuation(G, Gu_v, Gp, u0, p0, initial_tangent, ds_min, ds_max, ds, N_steps,
                 p_max, a_tol=1.e-10, max_it=10,
                 r_diff=1.e-8, epsilon: Optional[float] = None):
    M = u0.size
    u = np.copy(u0)  # Always the previous point on the curve
    p = np.copy(p0)  # Always the previous point on the curve
    u_path = [u]
    p_path = [p]

    # print_str = 'Step n: {0:3d}\t u: {1:4f}\t p: {2:4f}'.format(0, norm(u), p)
    # print(print_str)

    # Choose intial tangent (guess). We need to negate to find the actual search direction
    prev_tangent = -initial_tangent / norm(initial_tangent)

    # Variables for test_fn bifurcation detection -
    # Ensure no component in the direction of the tangent
    rng = RandomState()
    r = rng.normal(0.0, 1.0, M + 1)
    l = rng.normal(0.0, 1.0, M + 1)
    r = r - np.dot(r, prev_tangent) / np.dot(prev_tangent, prev_tangent) * prev_tangent
    l = l - np.dot(l, prev_tangent) / np.dot(prev_tangent, prev_tangent) * prev_tangent
    r = r / norm(r)
    l = l / norm(l)
    prev_tau_value = 0.0
    prev_tau_vector = None

    for n in range(1, N_steps + 1):
        # Determine the tangent to the curve at current point
        tangent = computeTangent(u, p, Gu_v, Gp, prev_tangent, M, a_tol)

        # Create the extended system for corrector
        N = lambda x: np.dot(tangent, x - np.append(u, p)) + ds
        F = lambda x: np.append(G(x[0:M], x[M]), N(x))
        dF_w = lambda x, w: (F(x + r_diff * w) - F(x)) / r_diff

        # Our implementation uses adaptive timetepping
        while ds > ds_min:
            # print(f'ds={ds}')
            # Predictor: Follow the tangent vector
            u_p = u + tangent[0:M] * ds
            p_p = p + tangent[M] * ds
            x_p = np.append(u_p, p_p)

            # Corrector: Newton-Raphson
            try:
                x_result = newton_krylov(F, x_p, f_tol=a_tol, maxiter=max_it, verbose=False)
                ds = min(1.2 * ds, ds_max)
                break
            except:
                # Decrease arclength if the solver needs more than max_it iterations
                ds = max(0.5 * ds, ds_min)
        else:
            # This case should never happpen under normal circumstances
            # print('Minimal Arclength Size is too large. Aborting.')
            return u_path, p_path
        u_new = x_result[0:M]
        p_new = x_result[M]

        # Do bifurcation detection in the new point
        tau_vector, tau_value = test_fn_bifurcation(dF_w, np.append(u_new, p_new), l, r, M, prev_tau_vector)
        if prev_tau_value * tau_value < 0.0:  # Bifurcation point detected
            print('Sign change detected', prev_tau_value, tau_value)
            # is_bf, x_singular = _computeBifurcationPointBisect(dF_w, np.append(u, p), np.append(u_new, p_new), l, r, M,
            #                                                    a_tol, prev_tau_vector)
            # if is_bf:
            #     return np.array(u_path), np.array(p_path), [x_singular]

        # Bookkeeping for the next step
        u = np.copy(u_new)
        p = np.copy(p_new)
        u_path.append(u)
        p_path.append(p)
        prev_tangent = np.copy(tangent)
        prev_tau_value = tau_value
        prev_tau_vector = tau_vector

        # Print the status
        print(f'p: {p} u: {norm(u)}  Step n: {n}')
        if math.floor(p) % 100 == 0:
            print(f'p: {p} u: {norm(u)}  Step n: {n}')
        if p >= p_max:
            break
        # Special case where the path starts from 0 and goes toward a bifurcation, then comes back to 0 by the same path
        if (epsilon is not None) and (p < epsilon):
            break

    return u_path, p_path

def computeTangent(u, p, Gu_v, Gp, prev_tau, M, a_tol):
	DG = LinearOperator((M, M), matvec=lambda v: Gu_v(u, p, v))
	tau = gmres(DG, -Gp(u, p), x0=prev_tau[:M], atol=a_tol)[0]
	tangent = np.append(tau, 1.0)
	tangent = tangent / norm(tangent)

	# Make sure the new tangent vector points in the same rough direction as the previous one
	if np.dot(tangent, prev_tau) < 0.0:
		tangent = -tangent
	return tangent


def test_fn_bifurcation(dF_w, x, l, r, M, y_prev, eps_reg=1.e-6):
	def matvec(w):
		el_1 = dF_w(x, w[0:M+1]) + eps_reg * w[0:M+1] + r*w[M+1]
		el_2 = np.dot(l, w[0:M+1])
		return np.append(el_1, el_2)
	sys = LinearOperator((M+2, M+2), matvec=matvec)
	rhs = np.zeros(M+2); rhs[M+1] = 1.0
	y, info = lgmres(sys, rhs, x0=y_prev, maxiter=10000)

	# Check if the l-gmres solver converged. If not, switch to a slow direct solver.
	if y_prev is None or info > 0 or np.abs(y[M+1] ) > 100:
		# print('GMRES Failed, Switching to a Direct Solver with the full Jacobian.')
		y = test_fn_bifurcation_exact(matvec, rhs)
	return y, y[M+1]

def test_fn_bifurcation_exact(matvec, rhs):
	# Construct the full matrix (yes, this is unfortunate but necessary...)
	A = np.zeros((rhs.size, rhs.size))
	for col  in range(rhs.size):
		A[:, col] = matvec(np.eye(rhs.size)[:, col])
	return solve(A, rhs)