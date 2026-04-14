"""Entrenamiento de modelo LightGBM para regresión de calidad del agua."""

import numpy as np
import pandas as pd
from typing import Optional
import lightgbm as lgb
from sklearn.metrics import mean_squared_error, r2_score


def train_lightgbm(
    X: pd.DataFrame | np.ndarray,
    y: np.ndarray,
    params: Optional[dict] = None,
    **kwargs,
) -> lgb.LGBMRegressor:
    """
    Entrena un regresor LightGBM. Parámetros por defecto en config.
    """
    default = {"n_estimators": 500, "learning_rate": 0.05, "max_depth": 8, "random_state": 42}
    if params:
        default.update(params)
    default.update(kwargs)
    model = lgb.LGBMRegressor(**default)
    model.fit(X, y)
    return model


def evaluate_lightgbm(model: lgb.LGBMRegressor, X: np.ndarray, y: np.ndarray) -> dict:
    """Devuelve RMSE y R²."""
    pred = model.predict(X)
    return {"rmse": np.sqrt(mean_squared_error(y, pred)), "r2": r2_score(y, pred)}
