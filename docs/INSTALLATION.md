# Installation and troubleshooting

## Recommended full simulation environment

Use conda or micromamba so native GDAL and its Python bindings resolve together:

```bash
git clone https://github.com/urbx-lab/UTherm.git
cd UTherm
conda env create -f environment.yml
conda activate utherm
python -m pip install -e .
utherm doctor
```

The environment selects Python 3.11. CI runs the complete suite and installed
wheel example on Linux with Python 3.10–3.12 and macOS with Python 3.11.
Windows is not part of the tested matrix; WSL with a Linux environment is the
closest supported workflow. The matrix uses CPU execution.

## Existing Python environments

The `urbx-utherm` distribution imports as `utherm`. Basic tensor solvers can be
installed with `python -m pip install .`; complete raster simulations also need
GDAL and rasterio. If native GDAL is already installed and its Python binding
matches that native version, `python -m pip install '.[geo]'` installs the
geospatial extras. Prefer the environment above for a new installation.
Do not use the package name `utherm` as a substitute for `urbx-utherm`.

`utherm doctor --json` imports each required runtime dependency and prints
versions, import errors, platform, and CUDA availability. It returns 1 if the
full simulation environment is incomplete. Attach that report to bug reports.
Doctor output records software state; it does not validate a simulation's physics.

## GPU validation

Install a CUDA-enabled PyTorch build compatible with your driver using the
[official PyTorch instructions](https://pytorch.org/get-started/locally/).
Then run:

```bash
utherm doctor --require-cuda
pytest --device=cuda --require-cuda -q
```

Both commands fail when CUDA is unavailable; a CPU-only run cannot count as
GPU validation. Tensor fixtures use the selected device, and the full pipeline
uses CUDA automatically when available. CI does not provide a GPU runner, and
this release does not claim that GPU validation was performed.

Use `CUDA_VISIBLE_DEVICES=""` before starting a process to force CPU execution.
Apple MPS is not selected by the engine. Large scenes may require smaller
`tile_size` to fit GPU memory; check sensitivity to `overlap` when changing tiles.

## Common problems

| Symptom | Action |
| --- | --- |
| `No module named osgeo` or GDAL build fails | Use `environment.yml`; pip needs an existing matching native GDAL library. |
| Binary import error or incompatible NumPy ABI | Recreate the environment rather than mixing unrelated pip and conda binary stacks. Run `utherm doctor`. |
| `utherm` command is unavailable | Activate the environment and run `python -m pip install -e .`; try `python -m utherm --help`. |
| CUDA is unavailable | Check the NVIDIA driver and installed PyTorch build with `utherm doctor --require-cuda`. |
| Meteorology date/time error | Check year, day of year, chronological hours, and the inferred location's date-specific time-zone offset. |
| Raster alignment error | Reproject/resample inputs onto one projected grid; use nearest-neighbor sampling for land-cover classes. |
| NaN values in UTCI or facet fields | Read nodata masks; building UTCI and absent physical facets are intentionally undefined. |
| Changes to inputs appear ineffective | Use a fresh `base_path` per scenario so processed caches cannot be mistaken for a new run. |

## Reproducible environments

Record the exact Git commit, input hashes, options, doctor report, and hardware.
For an exact conda package snapshot on the same platform:

```bash
conda list --explicit > conda-platform.lock
python -m pip freeze > pip-environment.txt
utherm doctor --json > environment-report.json
```

An explicit conda snapshot is platform-specific; keep the platform with the
artifact rather than presenting it as a cross-platform lock. The repository's
`environment.yml` describes compatible requirements rather than an exact lock.
