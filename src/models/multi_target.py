"""Multi-target regression: RegressorChain + stacking (LGB + XGB [+ Cat])."""

from typing import Any, Optional

import numpy as np
from sklearn.multioutput import RegressorChain
from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import Ridge
import lightgbm as lgb
import xgboost as xgb

try:
    import catboost as cb
    _HAS_CAT = True
except ImportError:
    _HAS_CAT = False


def make_base_estimators(random_state: int = 42) -> list[tuple[str, Any]]:
    est = [
        ("lgb", lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, max_depth=8, random_state=random_state, verbose=-1)),
        ("xgb", xgb.XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=8, random_state=random_state)),
    ]
    if _HAS_CAT:
        est.append(("cat", cb.CatBoostRegressor(iterations=300, depth=8, learning_rate=0.05, random_seed=random_state, verbose=0)))
    return est


def fit_regressor_chain_multioutput(
    X: np.ndarray,
    Y: np.ndarray,
    order: Optional[list[int]] = None,
    random_state: int = 42,
) -> RegressorChain:
    base = lgb.LGBMRegressor(n_estimators=200, max_depth=6, random_state=random_state, verbose=-1)
    return RegressorChain(base, order=order or [0, 1, 2], random_state=random_state).fit(X, Y)


def fit_stacking_per_target(
    X: np.ndarray,
    y: np.ndarray,
    random_state: int = 42,
) -> StackingRegressor:
    estimators = make_base_estimators(random_state)
    stack = StackingRegressor(
        estimators=estimators,
        final_estimator=Ridge(alpha=1.0),
        cv=min(3, len(y) // 2) if len(y) >= 6 else 2,
        n_jobs=-1,
    )
    stack.fit(X, y)
    return stack


def fit_all_targets_stacking(
    X: np.ndarray,
    Y: np.ndarray,
    target_names: list[str],
    random_state: int = 42,
) -> dict[str, StackingRegressor]:
    return {name: fit_stacking_per_target(X, Y[:, j], random_state) for j, name in enumerate(target_names)}
