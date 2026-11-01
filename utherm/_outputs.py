# Copyright (C) 2026 Sashank Silwal
# SPDX-License-Identifier: GPL-3.0-or-later
"""Consistent georeferenced export for simulation fields."""

from pathlib import Path
from collections.abc import Sequence

import numpy as np
from osgeo import gdal


def write_geotiff(path: str | Path, values, reference, timestamps: Sequence[str] | None = None) -> None:
    """Write a 2-D field or time/row/column cube using the reference raster grid.

    Undefined cells retain NaN nodata. Validate shapes before touching the output
    so a malformed field cannot silently overwrite a previous result.
    """
    array = np.asarray(values)
    if array.ndim == 2:
        array = array[None, ...]
    if array.ndim != 3 or array.shape[0] == 0:
        raise ValueError("output must be a nonempty (bands, rows, columns) cube or 2-D field")
    if array.shape[1:] != (reference.RasterYSize, reference.RasterXSize):
        raise ValueError("output dimensions must match the reference raster")
    if timestamps is not None and len(timestamps) != array.shape[0]:
        raise ValueError("one timestamp is required for each output band")
    dataset = gdal.GetDriverByName("GTiff").Create(
        str(path),
        reference.RasterXSize,
        reference.RasterYSize,
        array.shape[0],
        gdal.GDT_Float32,
        options=["COMPRESS=DEFLATE", "PREDICTOR=3", "BIGTIFF=IF_SAFER"],
    )
    if dataset is None:
        raise OSError(f"could not create GeoTIFF: {path}")
    try:
        dataset.SetGeoTransform(reference.GetGeoTransform())
        dataset.SetProjection(reference.GetProjection())
        for index, values in enumerate(array):
            band = dataset.GetRasterBand(index + 1)
            band.SetNoDataValue(float("nan"))
            band.WriteArray(values)
            if timestamps is not None:
                band.SetMetadata({"Time": timestamps[index]})
            band.FlushCache()
        dataset.FlushCache()
    finally:
        dataset = None
