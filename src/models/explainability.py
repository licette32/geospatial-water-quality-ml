"""SHAP-based interpretability for tree ensembles."""

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    import shap
except ImportError:
    shap = None


def shap_summary_bar(
    model,
    X: pd.DataFrame,
    feature_names: Optional[list] = None,
    max_display: int = 20,
    out_path: Optional[str | Path] = None,
    title: str = "SHAP — mean |impact| on predictions",
):
    """Bar plot of mean absolute SHAP values (global importance)."""
    if shap is None:
        raise ImportError("pip install shap")
    X = X.astype(float)
    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(X)
    if isinstance(sv, list):
        sv = sv[0]
    plt.figure(figsize=(10, 8))
    shap.summary_plot(sv, X, plot_type="bar", max_display=max_display, show=False)
    plt.title(title)
    plt.tight_layout()
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=150, bbox_inches="tight")
    return plt.gcf()


def shap_dependence_climate(
    model,
    X: pd.DataFrame,
    climate_feature: str,
    out_path: Optional[str | Path] = None,
):
    """How a climate-related feature drives predictions (marginal effect)."""
    if shap is None:
        raise ImportError("pip install shap")
    if climate_feature not in X.columns:
        raise ValueError(f"Column {climate_feature} not in X")
    explainer = shap.TreeExplainer(model)
    sv = explainer.shap_values(X.astype(float))
    if isinstance(sv, list):
        sv = sv[0]
    i = list(X.columns).index(climate_feature)
    plt.figure(figsize=(8, 5))
    shap.dependence_plot(i, sv, X, show=False)
    plt.tight_layout()
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=150, bbox_inches="tight")
    return plt.gcf()
