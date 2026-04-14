"""Ensemble de modelos LightGBM, XGBoost y CatBoost."""

import numpy as np
from typing import Any

from .train_lightgbm import train_lightgbm
from .train_xgboost import train_xgboost
from .train_catboost import train_catboost


def build_ensemble(
    X: np.ndarray,
    y: np.ndarray,
    weights: tuple[float, float, float] = (1.0 / 3, 1.0 / 3, 1.0 / 3),
) -> tuple[list[Any], tuple[float, float, float]]:
    """
    Entrena los tres modelos y devuelve (lista de modelos, pesos).
    weights: (lgb, xgb, cat).
    """
    w = np.array(weights)
    w = w / w.sum()
    models = [
        train_lightgbm(X, y),
        train_xgboost(X, y),
        train_catboost(X, y),
    ]
    return models, tuple(w.tolist())


def predict_ensemble(
    models: list[Any],
    X: np.ndarray,
    weights: tuple[float, ...] = (1.0 / 3, 1.0 / 3, 1.0 / 3),
) -> np.ndarray:
    """Predicción ponderada del ensemble."""
    preds = np.column_stack([m.predict(X) for m in models])
    w = np.array(weights)
    w = w / w.sum()
    return (preds * w).sum(axis=1)
