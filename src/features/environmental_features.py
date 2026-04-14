"""Construcción de features ambientales para el modelo."""

import pandas as pd
import numpy as np
from typing import Optional

from .spectral_indices import compute_spectral_indices


def build_environmental_features(
    df: pd.DataFrame,
    include_spectral: bool = True,
    drop_geometry: bool = True,
) -> pd.DataFrame:
    """
    Construye el conjunto de features para el modelo:
    bandas Landsat, índices espectrales y variables climáticas.
    """
    out = df.copy()

    if include_spectral:
        out = compute_spectral_indices(out)

    # Columnas que no son features (identificadores/geometría/targets)
    non_feature = {"id", "geometry", "total_alkalinity", "electrical_conductance", "dissolved_reactive_phosphorus"}
    if drop_geometry and "geometry" in out.columns:
        out = out.drop(columns=["geometry"], errors="ignore")

    # Rellenar NaN con la mediana por columna (solo numéricas)
    numeric = out.select_dtypes(include=[np.number]).columns
    for c in numeric:
        if c not in non_feature and out[c].isna().any():
            out[c] = out[c].fillna(out[c].median())

    return out
