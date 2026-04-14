"""Temporal features: month, season, rolling precipitation (see module docstring in repo)."""

import numpy as np
import pandas as pd
from typing import Optional

DATE_ALIASES = ("sample_date", "Sample Date", "sampledate", "date")


def _find_date_col(df: pd.DataFrame) -> Optional[str]:
    for c in DATE_ALIASES:
        if c in df.columns:
            return c
    return None


def _find_precip_col(df: pd.DataFrame) -> Optional[str]:
    for c in df.columns:
        cl = c.lower()
        if cl in ("precipitation", "precip", "ppt", "total_precipitation_sum", "pr"):
            return c
    return None


def add_temporal_features(
    df: pd.DataFrame,
    date_col: Optional[str] = None,
    precip_col: Optional[str] = None,
    rolling_windows: tuple[int, ...] = (7, 30),
    inplace: bool = False,
) -> pd.DataFrame:
    out = df if inplace else df.copy()
    dc = date_col or _find_date_col(out)
    if dc is None:
        return out

    out["_dt"] = pd.to_datetime(out[dc], errors="coerce")
    out["feat_month"] = out["_dt"].dt.month.fillna(0).astype(int)
    m = out["_dt"].dt.month.fillna(1).astype(int)

    def season(month: int) -> int:
        if month in (12, 1, 2):
            return 1
        if month in (3, 4, 5):
            return 2
        if month in (6, 7, 8):
            return 3
        return 4

    out["feat_season"] = m.map(season)

    pc = precip_col or _find_precip_col(out)
    if pc is not None:
        order = np.argsort(out["_dt"].values)
        s = out.iloc[order].reset_index(drop=True)
        p = pd.to_numeric(s[pc], errors="coerce")
        for w in rolling_windows:
            col = f"precip_roll_{w}d"
            rolled = p.rolling(window=w, min_periods=1).mean()
            out[col] = np.nan
            out.loc[out.index[order], col] = rolled.values

    out.drop(columns=["_dt"], errors="ignore", inplace=True)
    return out
