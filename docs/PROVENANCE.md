# Source provenance

This release starts from the clean source snapshot of the Tree-Placement
repository at commit `8e67215315ff399a7cdbe0148b9ad85dd1334f18`.
`SOURCE_PROVENANCE.json` records SHA-256 hashes of its original UTherm source
files before release-specific edits. This identifies the implementation used
as a starting point; it does not assert equivalence to every historical UTherm
simulation archive.

The standalone package retains the engine, its physical tests, the experimental
coupled solver, and the land-cover lookup table. Study-specific tree placement,
data downloads, statistical analysis, private city inputs, and model outputs
are outside this library. The geometry generator moved from the study package
to `utherm.geometry`; imports were updated accordingly. The CLI now matches the API TMRT default;
GeoTIFF exports declare NaN nodata so readers mask excluded pixels correctly.
Trailing whitespace and line endings were normalized for distribution.
These release fixes do not change the numerical kernels.

The inherited engine includes raster/met validation, periodic spin-up support,
and radiant-temperature end-to-end regression coverage. Its model assumptions
are documented in `MODEL.md` and `COUPLED_ENERGY_BALANCE.md`. Test results verify
software behavior on the stated platform, not observational validation or
reproduction of an unspecified archive.

Preserve the exact release commit, dependency versions, hardware, raster and
meteorological hashes, model options, and spin-up settings when reporting results.
