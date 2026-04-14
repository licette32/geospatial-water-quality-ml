"""Stacking simple: OOF de base learners + meta LightGBM (opcional)."""

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.base import clone
from typing import Any

from .train_lightgbm import train_lightgbm


def fit_stacking_regressor(
    X: np.ndarray | pd.DataFrame,
    y: np.ndarray,
    base_models: list[Any],
    n_splits: int = 5,
    random_state: int = 42,
) -> tuple[list[Any], Any, np.ndarray]:
    """
    OOF de cada base learner + meta LightGBM sobre predicciones OOF.
    """
    X = np.asarray(X)
    n = len(y)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    n_base = len(base_models)
    oof = np.zeros((n, n_base))
    fitted = []

    for j, model in enumerate(base_models):
        for train_idx, val_idx in kf.split(X):
            m = clone(model)
            m.fit(X[train_idx], y[train_idx])
            oof[val_idx, j] = m.predict(X[val_idx])
        full = clone(model)
        full.fit(X, y)
        fitted.append(full)

    meta = train_lightgbm(oof, y, params={"n_estimators": 200, "max_depth": 4})
    return fitted, meta, oof


def predict_stacking(
    base_models: list[Any],
    meta: Any,
    X: np.ndarray | pd.DataFrame,
) -> np.ndarray:
    X = np.asarray(X)
    P = np.column_stack([m.predict(X) for m in base_models])
    return meta.predict(P)
