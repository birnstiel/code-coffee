import numpy as np
import numba
from timeit import default_timer as timer

@numba.njit
def estimate_pi(nMC):
    radius = 1.
    diameter = 2.*radius
    n_circle = 0
    for i in range(nMC):
        x = (np.random.random()-0.5)*diameter
        y = (np.random.random()-0.5)*diameter
        r = np.sqrt(x**2 + y**2)
        if r <= radius:
           n_circle += 1
    return 4.*n_circle/nMC

nMC = 1_000_000

for i in range(3):
    print("function call ", i+1)
    start = timer()
    pi_est = estimate_pi(nMC)
    end = timer()
    print((end - start)*1_000.0, " ms")
    #print(pi_est)

pi_est = estimate_pi(nMC)
print("L1 error: ", np.abs( pi_est - np.pi ) / np.pi)