"""Check the public raster contract independently of the simulation kernels."""

import numpy as np
import pytest
import rasterio
from osgeo import gdal, osr

from utherm._outputs import write_geotiff


@pytest.fixture
def reference():
    dataset = gdal.GetDriverByName("MEM").Create("", 3, 2, 1, gdal.GDT_Float32)
    dataset.SetGeoTransform((500000, 1, 0, 4500000, 0, -1))
    crs = osr.SpatialReference()
    crs.ImportFromEPSG(32616)
    dataset.SetProjection(crs.ExportToWkt())
    return dataset


def test_export_preserves_grid_timestamps_and_missing_cells(reference, tmp_path):
    values = np.arange(12, dtype=float).reshape(2, 2, 3)
    values[:, 0, 1] = np.nan
    timestamps = ["2023-07-15T12:00:00", "2023-07-15T13:00:00"]
    path = tmp_path / "field.tif"
    write_geotiff(path, values, reference, timestamps)
    with rasterio.open(path) as source:
        assert source.crs.to_epsg() == 32616
        assert source.transform.to_gdal() == reference.GetGeoTransform()
        assert source.count == 2
        assert source.tags(2)["Time"] == timestamps[1]
        assert source.compression.name == "deflate"
        actual = source.read(masked=True)
        assert np.array_equal(np.ma.getmaskarray(actual), np.isnan(values))
        np.testing.assert_equal(actual.filled(np.nan), values.astype(np.float32))


@pytest.mark.parametrize(
    "values,timestamps",
    [
        (np.zeros((1, 3, 3)), None),
        (np.zeros((0, 2, 3)), None),
        (np.zeros((2, 2, 3)), ["2023-07-15T12:00:00"]),
    ],
)
def test_invalid_export_cannot_overwrite_previous_file(reference, tmp_path, values, timestamps):
    path = tmp_path / "existing.tif"
    path.write_bytes(b"previous result")
    with pytest.raises(ValueError):
        write_geotiff(path, values, reference, timestamps)
    assert path.read_bytes() == b"previous result"


def test_static_export_has_one_band_without_fabricated_time(reference, tmp_path):
    path = tmp_path / "static.tif"
    write_geotiff(path, np.ones((2, 3)), reference)
    with rasterio.open(path) as source:
        assert source.count == 1
        assert "Time" not in source.tags(1)
