# UTherm

Urban thermal comfort and microclimate simulation with PyTorch.

[![CI](https://github.com/urbx-lab/UTherm/actions/workflows/ci.yml/badge.svg)](https://github.com/urbx-lab/UTherm/actions/workflows/ci.yml)
[![License: GPL v3+](https://img.shields.io/badge/License-GPLv3%2B-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10–3.12-blue.svg)](pyproject.toml)

UTherm takes terrain, buildings, tree canopy, land cover, and weather as inputs
and writes georeferenced thermal-comfort fields. It extends the
SOLWEIG/SOLWEIG-GPU workflow with surface, roof, and canopy energy balances,
diagnostic wind fields, and spatial air-temperature methods.

The model runs on CPU and automatically uses CUDA when available. This is an
alpha research release; numerical regression tests do not establish accuracy
against observations for a new site. See [model assumptions](docs/MODEL.md).

## Features

- Mean radiant temperature (TMRT) and Universal Thermal Climate Index (UTCI).
- Shadows, sky-view factors, and shortwave/longwave radiation diagnostics.
- Optional ground, roof, and canopy energy balances with material presets.
- Diagnostic urban wind and canyon air temperature, including advection–diffusion.
- Optional coupled facet energy balance and ray-traced geometry.
- Python API and command-line interface for scripted workflows.

## Installation

Python 3.10–3.12 is supported. Use the supplied conda-forge environment to install
GDAL and its Python bindings together; installing GDAL with pip alone often
requires a matching native GDAL installation.

```bash
git clone https://github.com/urbx-lab/UTherm.git
cd UTherm
conda env create -f environment.yml
conda activate utherm
python -m pip install -e .
utherm --version
utherm doctor
```

Micromamba users can run `micromamba create -f environment.yml` instead of
`conda env create`. The environment selects Python 3.11. It contains the runtime
and test dependencies; editable installation makes the CLI available.

For NVIDIA GPUs, install a CUDA-enabled PyTorch build appropriate for your
system using the [official PyTorch instructions](https://pytorch.org/get-started/locally/),
then check `python -c "import torch; print(torch.cuda.is_available())"`.
Apple Metal/MPS is not selected by the model. Set `CUDA_VISIBLE_DEVICES=""`
before starting Python to force CPU execution on a CUDA host.

See [installation and troubleshooting](docs/INSTALLATION.md) for existing
environments, reproducible snapshots, and GPU validation.

The distribution name is `urbx-utherm`; the import name is `utherm`. Installation
from this repository is the supported route; this README does not assume a PyPI
release. The optional desktop GUI requires `python -m pip install '.[gui]'`.

## Quick start

### Python API

For your own aligned inputs:

```python
from utherm import thermal_comfort

thermal_comfort(
    base_path="/path/to/neighborhood",
    selected_date_str="2023-07-15",
    building_dsm_filename="Building_DSM.tif",
    dem_filename="DEM.tif",
    trees_filename="CDSM.tif",
    landcover_filename="landcover.tif",
    own_met_file="/path/to/neighborhood/met.txt",
    tile_size=512,
    overlap=20,
    save_tmrt=True,
)
```

Enable ground energy balance with `use_energy_balance=True`. Roof and canopy
energy balances additionally require `use_roof_eb=True` and
`use_canopy_eb=True`; request their outputs explicitly. The default radiation
workflow does not enable those optional solvers.

### Command line

```bash
utherm --base_path /path/to/neighborhood --date 2023-07-15 \
  --trees CDSM.tif --landcover landcover.tif \
  --own_metfile /path/to/neighborhood/met.txt --save_tmrt true
utherm --help
utherm-geometry --help
```

Run `python -m utherm --help` for the same CLI without its console script.
CLI options retain underscore spellings for compatibility. See
[input and output formats](docs/INPUTS.md) for raster conventions, meteorological
columns, output names, and a surface-energy-balance example.

## Inputs and outputs

| Input | Convention |
| --- | --- |
| `DEM.tif` | Bare-earth elevation, metres above datum |
| `Building_DSM.tif` | Terrain plus buildings, metres above the same datum |
| `CDSM.tif` | Tree canopy height above ground, metres; zero means no canopy |
| `landcover.tif` | Integer land-cover classes; optional for the default workflow |
| `met.txt` | Header plus UMEP/SOLWEIG text meteorology for the selected date |

Rasters must be single-band and share a projected CRS in metres, grid,
extent, and resolution. Invalid alignment and missing required inputs fail
before preprocessing. Do not fill missing terrain elevation with zero.

Outputs are GeoTIFFs in `output_folder/<tile>/`, with a band for each forcing
timestep. Band 1 corresponds to the first supplied timestep, which need not be
midnight. UTherm also creates a `processed_inputs/` working directory. Use a
fresh directory per scenario: processed inputs are reusable caches and existing
runs are not a provenance-managed experiment archive.

## Documentation

- [Installation and troubleshooting](docs/INSTALLATION.md)
- [Python API reference](docs/API.md)
- [Development and releases](docs/DEVELOPMENT.md)
- [Input, weather, and output reference](docs/INPUTS.md)
- [Model assumptions and scientific limits](docs/MODEL.md)
- [Experimental coupled energy balance](docs/COUPLED_ENERGY_BALANCE.md)
- [Source provenance](docs/PROVENANCE.md)
- [Release validation](docs/VALIDATION.md)
- [Contributing and development](CONTRIBUTING.md)
- [Release history](CHANGELOG.md)

## Development

```bash
python -m pip install -e '.[dev]'
pytest -q --cov
ruff check utherm tests examples tools
python tools/build_api_reference.py --check
python -m build
python -m twine check dist/*
```

The suite includes physical-invariant, raster-validation, and end-to-end
regression tests. It generates its own scenes and requires no city archive or
API keys. CI tests Linux on Python 3.10–3.12 and macOS on Python 3.11, enforces an 80%
line-coverage floor, and runs the installed wheel outside the source tree.
The optional GUI is excluded from coverage. For a CUDA validation run, use
`pytest --device=cuda --require-cuda`; missing hardware fails explicitly.
See the [development guide](docs/DEVELOPMENT.md) for checks and release steps.

## Citation

Use [CITATION.cff](CITATION.cff) for software citation metadata and record the
exact commit and configuration used in an experiment. There is no UTherm DOI
assigned in this repository. Credit the upstream SOLWEIG and SOLWEIG-GPU work
when describing the model lineage; attribution is preserved in [NOTICE](NOTICE)
and the source headers.

## License and support

UTherm is distributed under [GPL-3.0-or-later](LICENSE). Upstream copyright
notices are retained. Input datasets have their own licenses and are not bundled.

Report reproducible problems through [GitHub Issues](https://github.com/urbx-lab/UTherm/issues).
Include the version, environment, full command, and a small synthetic reproducer.
For vulnerabilities, follow [SECURITY.md](SECURITY.md).
