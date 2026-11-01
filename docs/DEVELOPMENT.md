# Development and releases

## Checks

```bash
python -m pip install -e '.[dev]'
ruff check utherm tests examples tools
python tools/build_api_reference.py --check
pytest -q --cov --cov-report=term-missing
python -m build
python -m twine check dist/*
```

Ruff checks syntax failures, all Pyflakes rules, and Bugbear rules across the
whole codebase. Formatting checks cover the maintained orchestration, CLI,
validation, diagnostics, export code, documentation tooling, and new tests.
Legacy numerical kernels retain their established formatting to keep physical
changes reviewable. Format the maintained files using the command in CI.

Coverage has an **80% line-coverage floor** over `utherm`, excluding only the
optional desktop GUI, which needs an interactive display. The legacy radiation,
preprocessing, energy-balance, wind, and transport modules remain in scope.
Coverage reports show untested paths; the percentage does not establish physical
correctness. Tests must check physical invariants or externally visible behavior,
not merely reproduce an implementation.

CI validates Linux on Python 3.10–3.12 and macOS on Python 3.11. Each job checks
imports and dependencies, runs tests, builds distributions, and runs the synthetic
scene from a wheel installed outside the checkout. Test reports, coverage XML,
and distributions are attached to the workflow run. Workflow actions are pinned
to commits; Dependabot proposes updates monthly.

## Module boundaries

| Module | Responsibility |
| --- | --- |
| `core.py` | Public orchestration and solver configuration |
| `_validation.py` | Inputs, alignment, weather, and cross-option requirements |
| `_outputs.py` | GeoTIFF shape checks, grid metadata, compression, time tags, and nodata |
| `cli.py`, `doctor.py` | Command-line interface and installation diagnostics |
| `energy_balance/` | Physical kernels and coupled solvers |
| `utci_process.py` | Per-timestep model integration |
| `preprocessor.py` | Raster and weather preprocessing |

`_` modules are internal. The public entry point remains `utherm.thermal_comfort`.
The generated [API defaults reference](API.md) is checked against its live
signature. Run `python tools/build_api_reference.py` after changing arguments.

## Releasing

1. Update the version in `pyproject.toml`, `utherm/__init__.py`, and `CITATION.cff`.
2. Update `CHANGELOG.md`, citation date, and validation evidence.
3. Run the checks above and inspect installed-wheel behavior outside the checkout.
4. Push the commit and wait for every CI matrix job to succeed.
5. If publishing a release, tag that reviewed commit and attach the validated
   wheel and source archive. Publish to PyPI only through a separately authorized
   release process; pushing `main` does not publish packages.

Run `pytest --device=cuda --require-cuda` on real CUDA hardware before claiming
GPU validation. Never replace missing hardware with a passing skipped test run.
