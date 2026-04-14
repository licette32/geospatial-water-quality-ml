"""Extracción de variables climáticas en puntos (lon, lat) desde rasters."""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

try:
    import rasterio
    from rasterio.sample import sample_gen
except ImportError:
    rasterio = None


def extract_climate_at_points(
    points_df: pd.DataFrame,
    raster_dir: str | Path,
    variables: Optional[list[str]] = None,
    lon_col: str = "lon",
    lat_col: str = "lat",
) -> pd.DataFrame:
    """
    Extrae variables climáticas (precipitación, temperatura, etc.) en coordenadas.
    """
    if rasterio is None:
        raise ImportError("rasterio es requerido para extract_climate_at_points")

    raster_dir = Path(raster_dir)
    variables = variables or ["precipitation", "temperature", "evapotranspiration"]
    coords = list(zip(points_df[lon_col], points_df[lat_col]))

    out = points_df.copy()
    for var in variables:
        path = raster_dir / f"{var}.tif"
        if not path.exists():
            out[var] = np.nan
            continue
        with rasterio.open(path) as src:
            vals = [v[0] for v in sample_gen(src, coords)]
        out[var] = vals

    return out
