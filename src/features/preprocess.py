"""Preprocesado: selección de columnas, imputación, escalado opcional."""

import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
from typing import Optional

from ..data.load_data import TARGETS


def feature_columns(
    df: pd.DataFrame,
    exclude_targets: bool = True,
    id_cols: Optional[list[str]] = None,
) -> list[str]:
    """Columnas numéricas candidatas a features."""
    id_cols = id_cols or [
        "id",
        "lon",
        "lat",
        "Latitude",
        "Longitude",
        "Sample Date",
        "sample_date",
        "sampledate",
    ]
    drop = set(id_cols)
    if exclude_targets:
        drop |= set(TARGETS)
        drop |= {
            "Total Alkalinity",
            "Electrical Conductance",
            "Dissolved Reactive Phosphorus",
        }
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    return [c for c in numeric if c not in drop]


def impute_median(X: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    medians = X.median(numeric_only=True)
    return X.fillna(medians), medians


def scale_features(
    X_train: pd.DataFrame,
    X_test: Optional[pd.DataFrame] = None,
) -> tuple[pd.DataFrame, Optional[pd.DataFrame], RobustScaler]:
    scaler = RobustScaler()
    cols = X_train.columns
    Xtr = pd.DataFrame(scaler.fit_transform(X_train), columns=cols, index=X_train.index)
    if X_test is None:
        return Xtr, None, scaler
    Xte = pd.DataFrame(scaler.transform(X_test), columns=cols, index=X_test.index)
    return Xtr, Xte, scaler
