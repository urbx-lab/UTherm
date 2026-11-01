# Model assumptions

UTherm combines the SOLWEIG radiative workflow with optional urban surface and
canopy energy-balance modules. Its public entry point is
`utherm.thermal_comfort`; defaults enable radiation and UTCI while leaving the
energy-balance extensions disabled.

## Selecting a configuration

Ground energy balance uses `use_energy_balance=True`. Roof and canopy extensions
require energy balance; enable each explicitly and request the corresponding
output. `use_canyon_air_temp=True` enables a reduced air-temperature diagnostic.
The `conductance-blend`, `log-profile`, and `advdiff` methods embody different
assumptions. `target` is a compatibility alias for `conductance-blend`.
Diagnostic wind and advective transport require valid wind-direction forcing.
Neither the wind model nor the air-temperature diagnostic is a resolved CFD
simulation. Site calibration and observational evaluation remain necessary.

`use_coupled_eb=True` selects the experimental coupled facet solver instead of
the standard surface-energy-balance path. It requires a compatible reciprocal
geometry bundle and convergence checks. Read `COUPLED_ENERGY_BALANCE.md` before
using it; do not combine results from different solver configurations without
identifying them.

## Initialization and boundaries

`spinup_days=N` repeats the selected day's forcing on preceding calendar days
and publishes only the requested day. It initializes numerical state rather
than reconstructing antecedent weather. The default is zero spin-up days.

Shadows, exchange factors, and transport depend on the spatial domain and tile
halo. An overlap of 20 pixels is a default, not a guarantee of convergence for
tall buildings or every sun angle. Check sensitivity to tile size, overlap,
geometry resolution, meteorological forcing, and material parameters.

## Interpretation

Predicted temperatures are simulator outputs. A passing physical-invariant or
numerical regression test cannot establish accuracy for a real neighborhood.
The synthetic example and regression references are software checks, not a
validation dataset. Canopy geometry, leaf area, moisture availability, land cover,
and meteorological representativeness can materially affect results.

The code automatically selects CUDA when available and otherwise uses CPU.
Floating-point reductions and library versions can change numerical results.
Record hardware and the complete configuration when comparing scenarios.
