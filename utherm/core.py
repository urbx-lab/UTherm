# UTherm: GPU-accelerated urban microclimate model
# Copyright (C) 2022–2025 Harsh Kamath and Naveen Sudharsan

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# Copyright (C) 2025-2026 Sashank Silwal
# SPDX-License-Identifier: GPL-3.0-or-later
from typing import Optional

from ._validation import (
    _expand_met_for_spinup as _expand_met_for_spinup,
    _load_met_file as _load_met_file,
    _require_wind_directions as _require_wind_directions,
    _resolve_raster_path as _resolve_raster_path,
    _validate_input_rasters as _validate_input_rasters,
    _validate_model_arguments as _validate_model_arguments,
    _validate_run_arguments as _validate_run_arguments,
    _validate_tile_maps as _validate_tile_maps,
)


def thermal_comfort(
    base_path,
    selected_date_str,
    building_dsm_filename="Building_DSM.tif",
    dem_filename="DEM.tif",
    trees_filename="Trees.tif",
    landcover_filename: Optional[str] = None,
    tile_size=3600,
    overlap=20,
    use_own_met=True,
    start_time=None,
    end_time=None,
    data_source_type=None,
    data_folder=None,
    own_met_file=None,
    save_tmrt=True,
    save_svf=False,
    save_kup=False,
    save_kdown=False,
    save_lup=False,
    save_ldown=False,
    save_shadow=False,
    use_energy_balance=False,
    use_coupled_eb=False,
    coupled_geometry_path: Optional[str] = None,
    coupled_spinup_max_cycles=30,
    coupled_strict_convergence=True,
    z0=0.01,
    z_wind=None,
    ground_material_type="asphalt",
    save_qh=False,
    save_qe=False,
    use_roof_eb=False,
    roof_material_type="roof",
    use_canopy_eb=False,
    canopy_type="deciduous",
    canopy_lai=3.0,
    use_canyon_air_temp=False,
    save_tsfc=False,
    save_tsfc_roof=False,
    save_t_leaf=False,
    save_canopy_qh=False,
    save_canopy_qe=False,
    save_tair=False,
    save_tair_canyon=False,
    save_wall_temperature=False,
    use_wind_field=False,
    save_wind_speed=False,
    save_wind_direction=False,
    tair_method="conductance-blend",
    ground_wetness=None,
    canopy_gmax_fraction=None,
    spinup_days=0,
):
    """
    Main function to compute urban thermal comfort using the UTherm model.

    This function orchestrates the complete workflow:
    1. Preprocesses input rasters (tiling, validation)
    2. Processes meteorological data (ERA5, WRF, or custom)
    3. Calculates wall heights and aspects (parallel CPU)
    4. Computes shadows, radiation, and SVF (GPU-accelerated)
    5. Calculates UTCI thermal comfort index
    6. Saves outputs as georeferenced rasters

    Args:
        base_path (str): Base directory for output_folder/ and processed_inputs/; also used to resolve relative raster paths. For outputs elsewhere, set this to the desired output directory and pass complete paths for the raster arguments.
        selected_date_str (str): Simulation date in format 'YYYY-MM-DD'
        building_dsm_filename (str): Building+terrain DSM path or filename (relative to base_path). Default: 'Building_DSM.tif'. Can be a complete path if rasters live elsewhere.
        dem_filename (str): DEM path or filename (relative to base_path). Default: 'DEM.tif'
        trees_filename (str): Vegetation DSM path or filename (relative to base_path). Default: 'Trees.tif'
        landcover_filename (str, optional): Land cover raster path or filename. Default: None
        tile_size (int): Tile size in pixels. Default: 3600. Adjust based on GPU RAM.
        overlap (int): Overlap between tiles in pixels. Default: 20. Used for shadow transfer.
        use_own_met (bool): Use custom meteorological file. Default: True
        start_time (str, optional): Start datetime 'YYYY-MM-DD HH:MM:SS' (UTC for ERA5/WRF)
        end_time (str, optional): End datetime 'YYYY-MM-DD HH:MM:SS' (UTC for ERA5/WRF)
        data_source_type (str, optional): 'ERA5' or 'wrfout' if not using own met file
        data_folder (str, optional): Folder containing ERA5/WRF NetCDF files
        own_met_file (str, optional): Path to custom meteorological text file
        spinup_days (int): Number of periodic preceding forcing days used to
            initialize thermal state. Only the requested day is written.
        save_tmrt (bool): Save mean radiant temperature output. Default: True
        save_svf (bool): Save sky view factor output. Default: False
        save_kup (bool): Save upward shortwave radiation. Default: False
        save_kdown (bool): Save downward shortwave radiation. Default: False
        save_lup (bool): Save upward longwave radiation. Default: False
        save_ldown (bool): Save downward longwave radiation. Default: False
        save_shadow (bool): Save shadow maps. Default: False
        use_energy_balance (bool): Enable physics-based energy balance. Default: False
        use_coupled_eb (bool): Enable the seven-facet coupled energy balance.
            This replaces, rather than augments, use_energy_balance.
        coupled_geometry_path (str, optional): Reciprocal facet geometry bundle,
            required when use_coupled_eb=True.
        z0 (float): Roughness length (m). Default: 0.01
        z_wind (float, optional): Wind measurement height (m)
        ground_material_type (str): Ground material preset. Default: 'asphalt'

    Returns:
        None: Outputs are saved to `{base_path}/output_folder/` directory

    Output Structure:
        - {base_path}/processed_inputs/ - All preprocessing files
          - Building_DSM/ - Preprocessing tiles
          - DEM/ - Preprocessing tiles
          - Trees/ - Preprocessing tiles
          - metfiles/ - Meteorological files
          - walls/ - Wall height rasters
          - aspect/ - Wall aspect rasters
          - Outfile.nc - Processed NetCDF (if using ERA5/WRF)
        - output_folder/{tile_key}/ - One folder per tile (tile_key e.g. "0_0", "1000_0")
          - UTCI_{tile_key}.tif - Universal Thermal Climate Index (always saved)
          - TMRT_{tile_key}.tif - Mean radiant temperature (if save_tmrt=True)
          - SVF_{tile_key}.tif - Sky view factor (if save_svf=True)
          - Kup_{tile_key}.tif - Upward shortwave (if save_kup=True)
          - Kdown_{tile_key}.tif - Downward shortwave (if save_kdown=True)
          - Lup_{tile_key}.tif - Upward longwave (if save_lup=True)
          - Ldown_{tile_key}.tif - Downward longwave (if save_ldown=True)
          - Shadow_{tile_key}.tif - Shadow maps (if save_shadow=True)

    Notes:
        - Automatically uses GPU if available, falls back to CPU
        - Processes tiles in parallel for large domains
        - UTC to local time conversion handled automatically
        - Multi-band rasters: one band per hour

    Example:
        >>> from utherm import thermal_comfort
        >>> thermal_comfort(
        ...     base_path='/path/to/input',
        ...     selected_date_str='2020-08-13',
        ...     tile_size=1000,
        ...     overlap=100,
        ...     use_own_met=True,
        ...     own_met_file='/path/to/met.txt'
        ... )

    Raises:
        ValueError: If input rasters have mismatched dimensions, CRS, or pixel sizes
        FileNotFoundError: If the required input files are missing
    """

    from pathlib import Path

    base_path = str(Path(base_path).expanduser())
    building_dsm_filename = str(Path(building_dsm_filename).expanduser())
    dem_filename = str(Path(dem_filename).expanduser())
    trees_filename = str(Path(trees_filename).expanduser())
    if landcover_filename is not None:
        landcover_filename = str(Path(landcover_filename).expanduser())
    if own_met_file is not None:
        own_met_file = str(Path(own_met_file).expanduser())
    if data_folder is not None:
        data_folder = str(Path(data_folder).expanduser())
    if coupled_geometry_path is not None:
        coupled_geometry_path = str(Path(coupled_geometry_path).expanduser())

    _validate_run_arguments(selected_date_str, tile_size, overlap, spinup_days)
    if spinup_days and not use_energy_balance:
        raise ValueError(
            "spinup_days applies to the modular energy balance; the coupled solver "
            "uses convergence-based periodic spin-up"
        )
    _validate_input_rasters(
        base_path,
        building_dsm_filename,
        dem_filename,
        trees_filename,
        landcover_filename,
    )
    _validate_model_arguments(
        use_own_met=use_own_met,
        own_met_file=own_met_file,
        data_source_type=data_source_type,
        data_folder=data_folder,
        start_time=start_time,
        end_time=end_time,
        use_energy_balance=use_energy_balance,
        use_coupled_eb=use_coupled_eb,
        coupled_geometry_path=coupled_geometry_path,
        coupled_spinup_max_cycles=coupled_spinup_max_cycles,
        coupled_strict_convergence=coupled_strict_convergence,
        z0=z0,
        z_wind=z_wind,
        ground_material_type=ground_material_type,
        use_roof_eb=use_roof_eb,
        roof_material_type=roof_material_type,
        use_canopy_eb=use_canopy_eb,
        canopy_type=canopy_type,
        canopy_lai=canopy_lai,
        use_canyon_air_temp=use_canyon_air_temp,
        use_wind_field=use_wind_field,
        tair_method=tair_method,
        ground_wetness=ground_wetness,
        canopy_gmax_fraction=canopy_gmax_fraction,
        requested_outputs={
            "save_qh": save_qh,
            "save_qe": save_qe,
            "save_tsfc": save_tsfc,
            "save_tsfc_roof": save_tsfc_roof,
            "save_t_leaf": save_t_leaf,
            "save_canopy_qh": save_canopy_qh,
            "save_canopy_qe": save_canopy_qe,
            "save_tair_canyon": save_tair_canyon,
            "save_wall_temperature": save_wall_temperature,
            "save_wind_speed": save_wind_speed,
            "save_wind_direction": save_wind_direction,
        },
    )
    from .preprocessor import ppr
    from .utci_process import compute_utci, map_files_by_key
    from .walls_aspect import run_parallel_processing
    import os
    import torch

    # Create preprocessing outputs directory
    preprocess_dir = os.path.join(base_path, "processed_inputs")
    os.makedirs(preprocess_dir, exist_ok=True)

    ppr(
        base_path,
        building_dsm_filename,
        dem_filename,
        trees_filename,
        landcover_filename,
        tile_size,
        overlap,
        selected_date_str,
        use_own_met,
        start_time,
        end_time,
        data_source_type,
        data_folder,
        own_met_file,
        preprocess_dir=preprocess_dir,
    )

    base_output_path = os.path.join(base_path, "output_folder")
    inputMet = os.path.join(preprocess_dir, "metfiles")
    building_dsm_dir = os.path.join(preprocess_dir, "Building_DSM")
    tree_dir = os.path.join(preprocess_dir, "Trees")
    dem_dir = os.path.join(preprocess_dir, "DEM")
    landcover_dir = os.path.join(preprocess_dir, "Landcover") if landcover_filename is not None else None
    walls_dir = os.path.join(preprocess_dir, "walls")
    aspect_dir = os.path.join(preprocess_dir, "aspect")

    run_parallel_processing(building_dsm_dir, walls_dir, aspect_dir)

    if torch.cuda.is_available():
        print("[GPU] GPU acceleration enabled")
    print("Running UTherm ...")

    building_dsm_map = map_files_by_key(building_dsm_dir, ".tif")
    tree_map = map_files_by_key(tree_dir, ".tif")
    dem_map = map_files_by_key(dem_dir, ".tif")
    landcover_map = map_files_by_key(landcover_dir, ".tif") if landcover_dir else {}
    walls_map = map_files_by_key(walls_dir, ".tif")
    aspect_map = map_files_by_key(aspect_dir, ".tif")
    met_map = map_files_by_key(inputMet, ".txt", is_metfile=True)
    tile_maps = {
        "building DSM": building_dsm_map,
        "trees": tree_map,
        "DEM": dem_map,
        "walls": walls_map,
        "wall aspect": aspect_map,
        "meteorology": met_map,
    }
    if landcover_dir:
        tile_maps["land cover"] = landcover_map
    tile_keys = _validate_tile_maps(tile_maps)

    for key in tile_keys:
        building_dsm_path = building_dsm_map[key]
        tree_path = tree_map[key]
        dem_path = dem_map[key]
        landcover_path = landcover_map.get(key) if landcover_dir else None
        walls_path = walls_map[key]
        aspect_path = aspect_map[key]
        met_file_path = met_map[key]

        output_folder = os.path.join(base_output_path, key)
        os.makedirs(output_folder, exist_ok=True)

        met_file_data = _load_met_file(met_file_path, selected_date_str)
        if use_wind_field or tair_method == "advdiff":
            _require_wind_directions(met_file_data, met_file_path)
        if use_coupled_eb:
            output_start_index = 0
        else:
            met_file_data, output_start_index = _expand_met_for_spinup(met_file_data, selected_date_str, spinup_days)

        compute_utci(
            building_dsm_path,
            tree_path,
            dem_path,
            walls_path,
            aspect_path,
            landcover_path,
            met_file_data,
            output_folder,
            key,
            selected_date_str,
            save_tmrt=save_tmrt,
            save_svf=save_svf,
            save_kup=save_kup,
            save_kdown=save_kdown,
            save_lup=save_lup,
            save_ldown=save_ldown,
            save_shadow=save_shadow,
            use_energy_balance=use_energy_balance,
            use_coupled_eb=use_coupled_eb,
            coupled_geometry_path=coupled_geometry_path,
            coupled_spinup_max_cycles=coupled_spinup_max_cycles,
            coupled_strict_convergence=coupled_strict_convergence,
            z0=z0,
            z_wind=z_wind,
            ground_material_type=ground_material_type,
            save_qh=save_qh,
            save_qe=save_qe,
            use_roof_eb=use_roof_eb,
            roof_material_type=roof_material_type,
            use_canopy_eb=use_canopy_eb,
            canopy_type=canopy_type,
            canopy_lai=canopy_lai,
            use_canyon_air_temp=use_canyon_air_temp,
            save_tsfc=save_tsfc,
            save_tsfc_roof=save_tsfc_roof,
            save_t_leaf=save_t_leaf,
            save_canopy_qh=save_canopy_qh,
            save_canopy_qe=save_canopy_qe,
            save_tair=save_tair,
            save_tair_canyon=save_tair_canyon,
            save_wall_temperature=save_wall_temperature,
            use_wind_field=use_wind_field,
            save_wind_speed=save_wind_speed,
            save_wind_direction=save_wind_direction,
            tair_method=tair_method,
            ground_wetness=ground_wetness,
            canopy_gmax_fraction=canopy_gmax_fraction,
            output_start_index=output_start_index,
        )

        # Free GPU memory between tiles
        torch.cuda.empty_cache()
