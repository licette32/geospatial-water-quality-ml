"""Índices espectrales a partir de bandas Landsat (B2–B7)."""

import numpy as np
import pandas as pd
from typing import Optional


def _safe_ratio(num: np.ndarray, den: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    return np.where(np.abs(den) < eps, np.nan, num / (den + eps))


def compute_spectral_indices(
    df: pd.DataFrame,
    band_map: Optional[dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Añade NDVI, NDWI, MNDWI, NDBI, BSI.
    Espera B2 (blue), B3 (green), B4 (red), B5 (nir), B6 (swir1), B7 (swir2).
    """
    out = df.copy()
    blue = np.asarray(out.get("B2", out.get("blue", np.full(len(out), np.nan))), dtype=float)
    green = np.asarray(out.get("B3", out.get("green", np.full(len(out), np.nan))), dtype=float)
    red = np.asarray(out.get("B4", out.get("red", np.full(len(out), np.nan))), dtype=float)
    nir = np.asarray(out.get("B5", out.get("nir", np.full(len(out), np.nan))), dtype=float)
    swir1 = np.asarray(out.get("B6", out.get("swir1", np.full(len(out), np.nan))), dtype=float)
    swir2 = np.asarray(out.get("B7", out.get("swir2", np.full(len(out), np.nan))), dtype=float)

    out["NDVI"] = _safe_ratio(nir - red, nir + red)
    out["NDWI"] = _safe_ratio(green - nir, green + nir)
    out["MNDWI"] = _safe_ratio(green - swir1, green + swir1)
    out["NDBI"] = _safe_ratio(swir1 - nir, swir1 + nir)
    num_bsi = (swir1 + red) - (nir + blue)
    den_bsi = (swir1 + red) + (nir + blue)
    out["BSI"] = _safe_ratio(num_bsi, den_bsi)
    return out
