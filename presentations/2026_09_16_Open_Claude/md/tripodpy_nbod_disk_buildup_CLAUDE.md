# tripodpy_nbod_disk_buildup

## Overview

This variant of the tripodpy–GENGA simulation builds a protoplanetary disk from scratch via
cloud collapse (disk buildup), rather than starting from a pre-existing disk. It does not
couple to the GENGA N-body integrator (`nbod=False`). Compare to the `metal_acc` variant
which assumes a pre-existing disk and runs N-body planet growth.

Key differences from `metal_acc`:

| Feature | `metal_acc` | `disk_buildup` |
|---|---|---|
| N-body (GENGA) | Yes | No |
| Pressure bump | Yes | No |
| Cloud infall | No | Yes (`buildup=True`) |
| Initial disk | 1–10% Mstar | ~0 (built from infall) |
| Star mass | 1 Msun | 0.33 Msun |
| Chemistry | 3 species | Water only (`chem_water.txt`) |
| Temperature | Passive irradiation | Viscous + irradiation + cloud (DD18) |
| Stellar mass | Fixed | Grows via infall + disk accretion |

Top-level run script: `nbod_tripodpy.py`

---

## Disk Buildup Feature

### Physics Model

Cloud infall follows Hueso & Guillot (2005), itself based on:
- Shu (1977) inside-out collapse
- Ulrich (1976) rotation model
- Dullemond et al. (2006a,b) implementation

The disk grows entirely from infalling cloud material (initial disk mass `Mdisk_Mstar_ratio=1e-8`
— essentially empty). The infall shuts off at `tmax = Minfall/Mdot` when the cloud is exhausted.

### Key Parameters (`nbod_tripodpy.py`)

```python
param_buildup(sim,
    Mcloud=c.M_sun,          # total cloud mass
    Omega_c=7e-15,           # cloud rotation rate [rad/s]
    Tcloud=10.,              # cloud temperature [K]
    Nr_dust_cutoff=...,      # index: zero dust inside this cell (sub-centrifugal region)
    temp_flg=1,              # 1 = DD18 viscous+irradiation temperature
    dt_temp_update=c.year,   # temperature update interval
    delta_d=1e-5)            # dust diffusivity (all three delta channels)
```

Grid: 512 cells, `rmin=0.1 au`, `rmax=100 au`, `alpha=1e-3`, `vFrag=100 cm/s`, star `0.33 Msun`.

### Key Files

| File | Role |
|---|---|
| `src_py/buildup/infall.py` | All infall physics: centrifugal radius, source terms, inner cutoff |
| `src_py/buildup/temperature.py` | DD18 viscous + irradiation temperature solver (Brent per cell) |
| `src_py/buildup/rossmean_dsharp_a10_q3.5` | Rosseland mean opacity table used by DD18 |
| `src_py/ext_sources.py` | Wires infall `S_ext_infall` terms into the dustpy update cycle |
| `src_py/setup.py` | `initialize_resume()` calls `buildup_setup()` after all other modules |

### Core Updater Functions (`infall.py`)

**`r_cen_update()` (line 122)** — centrifugal radius grows as `t³`:
```python
r_cen = 1/16 * G³ * Omega_c² * cs_c⁻⁸ * Mdot³ * (t + t0)³
```
Freezes at `tmax`. `t0` is the pre-simulation infall time before `r_cen` reached `rmin`.

**`Sigma_dot_infall_update()` (line 129)** — Ulrich (1976) surface density source inside `r_cen`:
```python
Sigma_dot[r <= r_cen] = Mdot/(8π r_cen²) * (r/r_cen)^{-1.5} * (1 - sqrt(r/r_cen))^{-0.5}
```
Routes to `sim.ext_sources.components.<name>.gas/dust.S_ext_infall` per species.

**`dust_inner_cutoff()` (line 171)** — diastole hook, runs after every grid timestep:
Hardsets `comp.dust.Sigma[:Nr_dust_cutoff, :] = 1e-11` for all dust species. Guards the
innermost cells where the centrifugal radius has not yet arrived.

**`temp_DD_update()` (`temperature.py`)** — replaces the default passive-irradiation
temperature with `T_tot = (T_visc⁴ + T_irr⁴ + Tcloud⁴)^{0.25}`, solving for `T_visc`
via Brent's method per cell using the DSHARP Rosseland mean opacity.

### Infall Wiring (`ext_sources.py`)

`S_ext_infall` fields are created independently of the proxy-grid component abundances
(lines 49–50, 65–66). In `S_ext_gas_comp()` (line 82) and `S_ext_dust_comp()` (line 87):
```python
S_ext = S_ext_proxy_grid * abundance + S_ext_infall   # infall added unconditionally
```
This means infall is deposited even in cells that are at floor values.

### Stellar Mass Growth

Two updaters track stellar mass:
- `Mstar_dot_infall`: fraction of cloud infall going directly to the star (before disk)
- `Mstar_dot_inflow`: mass flux through the inner disk boundary

Both integrated with explicit Euler, appended to `sim.integrator.instructions` in `buildup_setup()`.

---

## Known Numerical Issue: Wave-Like Dust Density Peak in the Outer Disk

### Symptom

A wave-like feature / spurious peak in `Sigma_dust` appears in the outer disk, visible at
`t ~ 8×10^5 yr`.

### Key Constraint: Cloud Exhaustion Before Outer Boundary

With the default parameters (`Mcloud=1 M_sun`, `Omega_c=7e-15`, `Tcloud=10 K`):
- `tmax ≈ 5.38×10^5 yr` — cloud is fully consumed well before the wave epoch
- `r_cen` freezes at **~28.8 au** at `tmax`; it never approaches the 100 au outer boundary

The outer disk (>50 au) receives essentially no infall and stays at floor density throughout.
Any wave feature at `t ~ 8×10^5 yr` is **post-infall evolution** of dust deposited near
`r_cen ≈ 30 au` during the active phase.

### Root Cause: Outer Grid Boundary Too Close (rmax=100 au)

**Confirmed by four completed runs** (`tests/data_orig/`, `data_cellav/`, `data_floormask/`,
`data_1000au/`). Key results at t=8×10^5 yr:

- orig = cellav = floormask **exactly** in the inner disk and outer-disk wave position →
  infall singularity and floor-cell interaction have **no effect on the wave**
- The 1000-au run shows the wave at **~150–180 au** instead of ~90–95 au

**Mechanism**: The gas disk (Rc=30 au, α=1e-3) spreads viscously outward after infall stops
at tmax=5.38×10^5 yr. By t=8×10^5 yr the viscous spreading front reaches ~180 au. Dust rides
this front outward. In the 100-au runs the front hits the outer grid wall at ~95 au, where
gas (and dust) pile up, creating the artificial wave. With rmax=1000 au the front moves freely
and no wall-bounce feature forms.

**Fix**: Use `rmax ≥ 300 au` (the gas spreading front reaches ~180 au at the end of the
1-Myr run). The 1000-au run (`tests/run_1000au.py`) uses 700 cells (rmin=0.1 au, rmax=1000 au)
and reproduces the correct behaviour. Note: initial sigma must be floored to ≥1e-10 g/cm²
in outer cells to avoid a singular sparse-LU matrix on the first timestep (see the
`sim.gas.Sigma = np.maximum(...)` block in `run_1000au.py`).

### Infall Singularity: Still Present, But Not the Wave Cause

The factor `(1 - sqrt(r/r_cen))^{-0.5}` in `infall.py:134` can spike **100–400×** when a
grid-cell centre falls close to `r_cen` (analytically confirmed). This does not cause the
outer-disk wave, but it is still an inaccuracy in the infall profile near r_cen ≈ 30 au.
The cell-averaged fix in `tests/run_cellav.py` removes it cleanly if desired.

### Completed Tests (`tests/`)

| Script | What it showed |
|---|---|
| `run_orig.py` | Baseline — wave at ~90 au |
| `run_cellav.py` | Cell-avg infall — **identical** to orig; singularity is not the cause |
| `run_floormask.py` | Floor mask — **identical** to orig; floor cells are not the cause |
| `run_1000au.py` | rmax=1000 au — wave displaced to ~180 au; **confirms boundary cause** |

Re-run comparison: `python3 tests/plot_compare.py --snap 400 --rmax 200`
