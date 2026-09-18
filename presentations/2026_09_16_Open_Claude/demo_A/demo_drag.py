#!/usr/bin/env python3
"""Dust grains relaxing to the gas velocity under drag, explicit Euler.

    dv/dt = -(v - v_gas) / t_stop

Six grain sizes are integrated at once, all starting at v = 1, all sharing one
timestep. The output goes bad.

Usage: python3 demo_drag.py   ->  demo_drag_out.npz
"""
import numpy as np

v_gas, nsteps = 0.0, 600
t_stop = np.array([0.05, 0.1, 0.2, 0.5, 1.0, 2.0])   # stopping time per grain size
dt = 0.3
v = np.ones_like(t_stop)                             # every grain starts at v = 1

hist = []
for n in range(nsteps):
    v = v - dt * (v - v_gas) / t_stop
    hist.append(v.copy())

np.savez("demo_drag_out.npz", v=np.array(hist), t_stop=t_stop, dt=dt, v_gas=v_gas)
print(f"wrote demo_drag_out.npz  ({nsteps} steps)   final max|v| = {np.nanmax(np.abs(v)):.3e}")
