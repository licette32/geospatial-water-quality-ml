"""Entrenamiento de modelo CatBoost para regresión de calidad del agua."""

import numpy as np
import pandas as pd
from typing import Optional
import catboost as cb
from sklearn.metrics import mean_squared_error, r2_score


def train_catboost(
    X: pd.DataFrame | np.ndarray,
    y: np.ndarray,
    params: Optional[dict] = None,
    **kwargs,
) -> cb.CatBoostRegressor:
    """
    Entrena un regresor CatBoost. Parámetros por defecto en config.
    """
    default = {"iterations": 500, "learning_rate": 0.05, "depth": 8, "random_seed": 42, "verbose": 0}
    if params:
        default.update(params)
    default.update(kwargs)
    model = cb.CatBoostRegressor(**default)
    model.fit(X, y)
    return model


def evaluate_catboost(model: cb.CatBoostRegressor, X: np.ndarray, y: np.ndarray) -> dict:
    """Devuelve RMSE y R²."""
    pred = model.predict(X)
    return {"rmse": np.sqrt(mean_squared_error(y, pred)), "r2": r2_score(y, pred)}
