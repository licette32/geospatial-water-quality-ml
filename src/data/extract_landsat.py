"""Extracción de bandas Landsat en puntos (lon, lat) desde rasters."""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

try:
    import rasterio
    from rasterio.sample import sample_gen
except ImportError:
    rasterio = None


def extract_landsat_at_points(
    points_df: pd.DataFrame,
    raster_dir: str | Path,
    band_names: Optional[list[str]] = None,
    lon_col: str = "lon",
    lat_col: str = "lat",
) -> pd.DataFrame:
    """
    Extrae valores de bandas Landsat en las coordenadas de points_df.

    raster_dir puede contener un .tif por banda o un multiband.
    band_names: ej. ['B2','B3','B4','B5','B6','B7']
    """
    if rasterio is None:
        raise ImportError("rasterio es requerido para extract_landsat_at_points")

    raster_dir = Path(raster_dir)
    band_names = band_names or ["B2", "B3", "B4", "B5", "B6", "B7"]
    coords = list(zip(points_df[lon_col], points_df[lat_col]))

    out = points_df.copy()
    for band in band_names:
        band_path = raster_dir / f"{band}.tif"
        if not band_path.exists():
            band_path = raster_dir / f"landsat_{band}.tif"
        if not band_path.exists():
            out[band] = np.nan
            continue
        with rasterio.open(band_path) as src:
            vals = [v[0] for v in sample_gen(src, coords)]
        out[band] = vals

    return out
