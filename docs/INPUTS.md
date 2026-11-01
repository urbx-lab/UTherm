# Inputs and outputs

## Raster contract

Supply single-band rasters with matching shape, transform, projected CRS, extent,
and resolution. Coordinates and height values must use metres. DEM and building
DSM are absolute elevations using the same datum. Canopy values are height above
ground; a treeless pixel is zero. Where a source marks zero canopy as nodata,
UTherm preserves the valid no-canopy convention. Missing terrain is an error.

Default API filenames are `DEM.tif`, `Building_DSM.tif`, and `Trees.tif`.
Pass `trees_filename="CDSM.tif"` when using the canopy name in the examples.
Relative raster paths resolve against `base_path`; absolute raster paths are
also accepted. Use an explicit meteorological path.

Land-cover classes are:

| Value | Surface |
| --- | --- |
| 1 | Paved |
| 2 | Building |
| 3 | Evergreen tree |
| 4 | Deciduous tree |
| 5 | Grass |
| 6 | Bare soil |
| 7 | Water |

The packaged `utherm/landcoverclasses_2016a.txt` contains radiative parameters.
Use integer class IDs in the raster, rather than interpolating categories.

## Meteorological text

`own_met_file` is a whitespace-separated UMEP/SOLWEIG text file with one header
line and numeric rows. It is not a NetCDF file. The first 23 columns are the
standard UMEP layout, optionally followed by wind direction. Preserve unused
columns with the usual `-999` placeholder.

| Column (1-based) | Quantity | Units |
| --- | --- | --- |
| 1 | Year | year |
| 2 | Day of year | 1–366 |
| 3 | Local hour | 0–23 |
| 4 | Minute | 0–59 |
| 10 | Wind speed | m/s |
| 11 | Relative humidity | % |
| 12 | Air temperature | °C |
| 13 | Pressure | kPa |
| 14 | Precipitation | mm per forcing interval |
| 15 | Global horizontal shortwave | W/m² |
| 22 | Diffuse horizontal shortwave | W/m² |
| 23 | Direct normal shortwave | W/m² |
| 24 (optional) | Wind direction, required by wind/advdiff modes | degrees from north |

Rows must be chronological and belong to the selected simulation date. Supply
finite, physically meaningful values in required fields. The engine infers the location's time zone and the date-specific UTC offset
(including daylight saving time). Supply hours consistent with that offset;
convert standard-time weather records explicitly when necessary. For converted ERA5/WRF
input, `start_time` and `end_time` are UTC; see the CLI help for source options.
The synthetic example writes a complete 24-column text file.

## Output selection

UTCI is always written. `save_tmrt=True` is the Python API default and is also
explicitly enabled in the README's CLI example. Optional fields require both the
appropriate solver and their `save_*` flag.

| File prefix | Meaning | Units |
| --- | --- | --- |
| `UTCI`, `TMRT` | Thermal index and mean radiant temperature | °C |
| `Tsfc`, `TsfcRoof`, `TLeaf` | Ground, roof, leaf temperature | °C |
| `Tair`, `TairCanyon` | Air-temperature diagnostics | °C |
| `QH`, `QE` | Sensible and latent heat flux | W/m² |
| `Kup`, `Kdown`, `Lup`, `Ldown` | Radiation components | W/m² |
| `SVF` | Sky-view factor | fraction |

Each name includes its tile suffix, for example `TMRT_0_0.tif`. Floating-point outputs declare NaN nodata. Read raster
nodata masks when computing statistics; building UTCI and absent physical
facets must be excluded rather than filled with zero. Band numbering follows the supplied
forcing rows; a peak-hour subset starts at band 1 even if its first hour is noon.
Use the exact filenames produced by a run for additional solver diagnostics.

Example energy-balance configuration:

```python
from utherm import thermal_comfort

thermal_comfort(
    base_path="/path/to/fresh/scenario",
    selected_date_str="2023-07-15",
    building_dsm_filename="/path/to/inputs/Building_DSM.tif",
    dem_filename="/path/to/inputs/DEM.tif",
    trees_filename="/path/to/inputs/CDSM.tif",
    landcover_filename="/path/to/inputs/landcover.tif",
    own_met_file="/path/to/inputs/met.txt",
    use_energy_balance=True,
    use_roof_eb=True,
    use_canopy_eb=True,
    spinup_days=3,
    save_tsfc=True,
    save_tsfc_roof=True,
    save_t_leaf=True,
)
```
