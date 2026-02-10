import numpy as np

RAIN_STR = 'p'






# We set the params of the best ensemble member for the Dargol watershed
"""
c_croiss	i_croiss	c_max	c_mort	i_mort	
0.3928831056683607	377.9395570739971	1.0	0.950224996601153	132.30814805665025	
mu_c	p_ini	p_0max	a	b	skc	Ke_max
0.0038717892594712184	87.98423934692423	684.0019745904201	1.5	8.0	3.1046630132406943	0.9
"""

def derivative(states, forcing: float) :
    # print(f'States: {states}, forcing: {forcing}')
    #  Cast c_t in the good range of values and store it in the states dictionary
    c_t = max(min(states[0], 1), 0)
    states[0] = c_t
    #  Compute the intermediate values
    ke_l = compute_ke_l(states, forcing)
    i_l = compute_i(ke_l, forcing)
    #  Compute the derivative
    first_term = 0.3928831056683607	 * i_l / (i_l + 377.9395570739971) * c_t * (1 - c_t / 1.0)
    second_term = c_t * 0.950224996601153 * 132.30814805665025	 / (i_l + 132.30814805665025	)
    third_term = 0.0038717892594712184* (1 - c_t)
    dcdt = first_term - second_term + third_term
    return np.array([dcdt])

def compute_ke(states, forcing: float) -> float:
    ke_l = compute_ke_l(states, forcing)
    return ke_l / 	3.1046630132406943

def compute_ke_l(states, forcing: float) -> float:
    p_0 = 87.98423934692423 + states[0] * (684.0019745904201 - 87.98423934692423)
    #  At the local scale
    ratio = (forcing ** 1.5) / (forcing ** 1.5 + p_0 ** 1.5)
    return (ratio ** 8.) * 0.9

def compute_i(ke: float, forcing: float) -> float:
    return forcing * (1 - ke)
