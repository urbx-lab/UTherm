# Validation evidence

Validated on 2026-11-01 using Python 3.11 on macOS arm64, CPU execution.

- Full regression suite: **302 passed**.
- Scientific-engine line coverage: **81.72%**, above the 80% gate. Only the
  optional interactive GUI is excluded; legacy scientific modules stay in scope.
- Syntax, Pyflakes, Bugbear, maintained-file formatting, and generated API checks passed.
- Wheel and source archive builds passed; `twine check` passed for both.
- Dependency consistency (`pip check`) and full binary-import diagnostics passed.
- Installed-wheel checks run outside the checkout, including the synthetic scene.
- Public-path tests cover radiation, modular and coupled energy balance, advective
  air temperature, wind, roof/canopy fluxes, and georeferenced diagnostic exports.
- Export tests verify grid, nodata, compression, timestamps, and rejection of
  invalid arrays before an existing output can be overwritten.
- Regression checks cover spatial wind-speed preservation with scalar direction,
  missing wind observations, directional transport, diffusion, and bounded relaxation.
- Missing-CUDA checks correctly fail in both doctor and the GPU-required test route.

See `PROVENANCE.md` and `SOURCE_PROVENANCE.json` for source identity and changes.
Local CUDA execution was not performed. CI runs Linux Python 3.10–3.12 and
macOS Python 3.11 on CPU; each job uploads coverage, test reports, and packages.
Use the [Actions page](https://github.com/urbx-lab/UTherm/actions/workflows/ci.yml)
for results tied to an exact commit. Numerical tests do not replace observational
validation of a real-world simulation.

## Local dependency versions

| Package | Version |
| --- | --- |
| torch | 2.14.1 |
| numpy | 1.26.4 |
| scipy | 1.17.1 |
| pandas | 3.0.6 |
| rasterio | 1.4.4 |
| netCDF4 | 1.7.4 |
| timezonefinder | 6.6.2 |
| pytest | 9.2.0 |
| GDAL | 3.12.3 |
