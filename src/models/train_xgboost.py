"""Entrenamiento de modelo XGBoost para regresión de calidad del agua."""

import numpy as np
import pandas as pd
from typing import Optional
import xgboost as xgb
from sklearn.metrics import mean_squared_error, r2_score


def train_xgboost(
    X: pd.DataFrame | np.ndarray,
    y: np.ndarray,
    params: Optional[dict] = None,
    **kwargs,
) -> xgb.XGBRegressor:
    """
    Entrena un regresor XGBoost. Parámetros por defecto en config.
    """
    default = {"n_estimators": 500, "learning_rate": 0.05, "max_depth": 8, "random_state": 42}
    if params:
        default.update(params)
    default.update(kwargs)
    model = xgb.XGBRegressor(**default)
    model.fit(X, y)
    return model


def evaluate_xgboost(model: xgb.XGBRegressor, X: np.ndarray, y: np.ndarray) -> dict:
    """Devuelve RMSE y R²."""
    pred = model.predict(X)
    return {"rmse": np.sqrt(mean_squared_error(y, pred)), "r2": r2_score(y, pred)}
