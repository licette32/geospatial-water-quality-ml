"""Carga de datos de calidad del agua desde CSV/GeoDataFrame."""

import pandas as pd
from pathlib import Path
from typing import Optional

# Targets del proyecto
TARGETS = [
    "total_alkalinity",
    "electrical_conductance",
    "dissolved_reactive_phosphorus",
]


def load_water_quality_data(
    path: str | Path,
    geometry_col: Optional[str] = "geometry",
) -> pd.DataFrame:
    """
    Carga datos de calidad del agua desde CSV o shapefile.

    Espera columnas: id, lat, lon (o geometry), y los targets definidos.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró: {path}")

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
        # Normalize common column names (Latitude/Longitude, target names)
        if "Latitude" in df.columns and "lat" not in df.columns:
            df["lat"] = df["Latitude"]
        if "Longitude" in df.columns and "lon" not in df.columns:
            df["lon"] = df["Longitude"]
        target_column_aliases = {
            "Total Alkalinity": "total_alkalinity",
            "Electrical Conductance": "electrical_conductance",
            "Dissolved Reactive Phosphorus": "dissolved_reactive_phosphorus",
        }
        for old, new in target_column_aliases.items():
            if old in df.columns and new not in df.columns:
                df[new] = df[old]
    else:
        import geopandas as gpd
        gdf = gpd.read_file(path)
        df = pd.DataFrame(gdf.drop(columns=geometry_col, errors="ignore"))
        if geometry_col in gdf.columns:
            df["lon"] = gdf.geometry.x
            df["lat"] = gdf.geometry.y

    return df


def get_target_columns(df: pd.DataFrame) -> list[str]:
    """Devuelve las columnas target presentes en el DataFrame."""
    return [t for t in TARGETS if t in df.columns]
