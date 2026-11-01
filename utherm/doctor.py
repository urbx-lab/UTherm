# Copyright (C) 2026 Sashank Silwal
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inspect installed dependencies and compute hardware without running a scene."""

import argparse
import json
import platform
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version

from . import __version__

REQUIRED_MODULES = {
    "numpy": "numpy",
    "torch": "torch",
    "scipy": "scipy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "netCDF4": "netCDF4",
    "xarray": "xarray",
    "pytz": "pytz",
    "timezonefinder": "timezonefinder",
    "tqdm": "tqdm",
    "shapely": "shapely",
    "GDAL": "osgeo.gdal",
    "rasterio": "rasterio",
}


def collect_diagnostics() -> dict:
    """Return JSON-serializable installation checks, including binary imports."""
    packages = {}
    errors = {}
    cuda = {"available": False, "devices": []}
    for package, module_name in REQUIRED_MODULES.items():
        try:
            module = import_module(module_name)
            try:
                packages[package] = version(package)
            except PackageNotFoundError:
                packages[package] = getattr(module, "__version__", "unknown")
            if package == "torch":
                cuda["available"] = module.cuda.is_available()
                if cuda["available"]:
                    cuda["devices"] = [module.cuda.get_device_name(i) for i in range(module.cuda.device_count())]
        except Exception as exc:
            # A doctor must also report binary ABI/load failures, not just missing packages.
            errors[package] = f"{type(exc).__name__}: {exc}"
    return {
        "utherm": __version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": packages,
        "cuda": cuda,
        "errors": errors,
        "ok": not errors,
    }


def main(argv=None) -> int:
    """Print diagnostics and return nonzero for missing dependencies or required CUDA."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable report")
    parser.add_argument("--require-cuda", action="store_true", help="Fail if CUDA is unavailable")
    args = parser.parse_args(argv)
    report = collect_diagnostics()
    if args.require_cuda and not report["cuda"]["available"]:
        report["errors"]["cuda"] = "CUDA is required but unavailable"
        report["ok"] = False
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"UTherm {report['utherm']} | Python {report['python']} | {report['platform']}")
        for name, value in report["packages"].items():
            print(f"  {name}: {value}")
        print("  Compute: " + (", ".join(report["cuda"]["devices"]) if report["cuda"]["available"] else "CPU"))
        for name, error in report["errors"].items():
            print(f"  ERROR {name}: {error}")
        if not report["ok"]:
            print("Install the environment in environment.yml; see docs/INSTALLATION.md.")
        print("Installation ready" if report["ok"] else "Installation needs attention")
    return 0 if report["ok"] else 1
