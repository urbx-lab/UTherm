# Changelog

## 0.1.0 — 2026-11-01

Initial standalone UTherm source release under `urbx-lab/UTherm`.

- Extracted the microclimate engine and its regression suite from the existing
  tree-placement software; retained GPL notices and model attribution.
- Added standard package metadata, portable environment, CLI entry points,
  synthetic example, input reference, and continuous integration.
- Moved the coupled geometry command into `utherm.geometry` so the library no
  longer depends on the study orchestration package.

See `docs/PROVENANCE.md` for the source snapshot and scope of numerical validation.
- Aligned the CLI TMRT output default with the Python API and added
  `python -m utherm` support with CLI regression coverage.
- Declared NaN nodata in floating-point GeoTIFF outputs so GIS readers
  correctly mask excluded UTCI and facet cells in statistics.
