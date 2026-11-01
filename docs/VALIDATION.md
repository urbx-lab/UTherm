# Release validation

Validated on 2026-11-01 using Python 3.11 on macOS arm64, CPU execution.

- Full regression suite: **271 passed** (37 upstream dependency deprecation warnings).
- Ruff undefined-name checks and Python compilation: passed.
- Wheel and source archive build: passed; `twine check` passed for both.
- Package dependency consistency (`pip check`): passed.
- Wheel includes the land-cover lookup table, module CLI, and geometry command.
- Installed wheel imported from site-packages outside the source checkout.
- Public synthetic example completed from that wheel; UTCI and TMRT each
  contained 24 georeferenced bands with finite valid cells. UTCI building cells
  were correctly masked through the GeoTIFF NaN nodata declaration.
- Source scan found no credentials or author-specific absolute runtime paths.
- Numerical Python syntax matches the source snapshot outside the documented
  CLI and output-metadata edits (ignoring docstrings and whitespace).

See `PROVENANCE.md` and `SOURCE_PROVENANCE.json` for source identity and changes.
Local CUDA execution and other Python/platform combinations were not tested.
GitHub Actions is configured for Python 3.10, 3.11, and 3.12 on Linux CPU; its
status is available in the repository's Actions tab. Passing these checks does
not replace observational validation of a real-world simulation.

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
