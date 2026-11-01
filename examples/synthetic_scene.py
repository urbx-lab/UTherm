#!/usr/bin/env python3
# Copyright (C) 2025-2026 Sashank Silwal
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate a synthetic neighborhood and run a full UTherm radiation simulation."""
import argparse
import os
from pathlib import Path

import numpy as np
import rasterio

from utherm import thermal_comfort

N = 120
RES = 1.0
ORIGIN_X, ORIGIN_Y = 660000.0, 4000000.0
EPSG = 32611
DATE = "2023-07-06"


def _write(path, array, dtype):
    profile = dict(
        driver="GTiff", height=N, width=N, count=1, dtype=dtype,
        crs=rasterio.crs.CRS.from_epsg(EPSG),
        transform=rasterio.transform.from_origin(ORIGIN_X, ORIGIN_Y, RES, RES),
    )
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(array.astype(dtype), 1)


def _build_scene(base):
    """Deterministic scene: ground plane, four blocks, a row of trees, mixed land cover."""
    dem = np.full((N, N), 600.0, dtype="float32")

    dsm = dem.copy()
    for r0, c0 in ((20, 20), (20, 70), (70, 20), (70, 70)):
        dsm[r0:r0 + 26, c0:c0 + 26] += 12.0          # 12 m blocks

    cdsm = np.zeros((N, N), dtype="float32")
    cdsm[55:62, 10:110:6] = 8.0                       # street trees, 8 m crowns

    landcover = np.full((N, N), 1, dtype="int32")     # 1 = paved
    landcover[cdsm > 0] = 5                           # 5 = grass under canopy
    landcover[50:52, :] = 6                           # 6 = bare soil strip
    for r0, c0 in ((20, 20), (20, 70), (70, 20), (70, 70)):
        landcover[r0:r0 + 26, c0:c0 + 26] = 2         # 2 = buildings

    _write(os.path.join(base, "DEM.tif"), dem, "float32")
    _write(os.path.join(base, "Building_DSM.tif"), dsm, "float32")
    _write(os.path.join(base, "CDSM.tif"), cdsm, "float32")
    _write(os.path.join(base, "landcover.tif"), landcover, "int32")


def _write_met(path):
    """24 hours of clear-sky July forcing in UMEP format."""
    header = ("iy id it imin Q* QH QE Qs Qf Wind RH Td press rain Kdn snow "
              "ldown fcld wuh xsmd lai_hr Kdiff Kdir Wd")
    rows = []
    for hour in range(24):
        # smooth diurnal cycles; sun up 06:00-19:00
        day = np.clip(np.sin(np.pi * (hour - 6) / 13.0), 0.0, None)
        kdn = 1000.0 * day
        ta = 24.0 + 13.0 * np.clip(np.sin(np.pi * (hour - 5) / 15.0), 0.0, None)
        rh = 30.0 - 18.0 * day
        rows.append(
            f"2023 187 {hour} 0 -999 -999 -999 -999 -999 2.5 {rh:.4f} {ta:.4f} "
            f"95.0 0.0 {kdn:.4f} -999 340.0 -999 -999 -999 -999 "
            f"{0.25 * kdn:.4f} {0.75 * kdn:.4f} 200.0"
        )
    with open(path, "w") as fh:
        fh.write(header + "\n" + "\n".join(rows) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    base = args.output.expanduser().resolve()
    base.mkdir(parents=True, exist_ok=False)
    _build_scene(str(base))
    _write_met(str(base / "met.txt"))
    thermal_comfort(
        base_path=str(base), selected_date_str=DATE,
        own_met_file=str(base / "met.txt"), trees_filename="CDSM.tif",
        landcover_filename="landcover.tif", tile_size=256, overlap=20,
        save_tmrt=True,
    )
    print(f"Outputs: {base / 'output_folder'}")


if __name__ == "__main__":
    main()
