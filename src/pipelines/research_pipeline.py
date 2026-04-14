"""
Research pipeline — explicit stages for reproducibility and portfolio use.

Stages:
  1. load_data
  2. feature_engineering (temporal + scientific interactions; hydrology passthrough)
  3. spatial_clustering
  4. spatial_cross_validation + stacking training
  5. SHAP explainability
  6. save_results (metrics, models, figures)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import json
import numpy as np
import pandas as pd
import yaml
import joblib
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import StandardScaler

from ..data.load_data import load_water_quality_data, TARGETS
from ..features.preprocess import feature_columns, impute_median
from ..features.scientific_interactions import add_scientific_interactions
from ..features.temporal_features import add_temporal_features
from ..validation.spatial_cv import SpatialGroupKFold, spatial_cluster_groups
from ..models.multi_target import fit_stacking_per_target


def load_config(path: str | Path) -> dict:
    with open(Path(path), encoding="utf-8") as f:
        return yaml.safe_load(f)


@dataclass
class PipelineResult:
    config: dict
    metrics: dict[str, dict[str, float]] = field(default_factory=dict)
    oof_predictions: dict[str, np.ndarray] = field(default_factory=dict)
    cluster_ids: Optional[np.ndarray] = None
    figure_paths: list[str] = field(default_factory=list)
    artifact_dir: Optional[Path] = None


def stage_load_data(raw_csv: Path) -> pd.DataFrame:
    return load_water_quality_data(raw_csv)


def stage_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    out = add_temporal_features(df)
    out = add_scientific_interactions(out)
    return out


def stage_spatial_clustering(
    df: pd.DataFrame,
    n_clusters: int,
    random_state: int,
) -> tuple[pd.DataFrame, np.ndarray]:
    lat = df["lat"] if "lat" in df.columns else df["Latitude"]
    lon = df["lon"] if "lon" in df.columns else df["Longitude"]
    groups = spatial_cluster_groups(lat.values, lon.values, n_clusters, random_state)
    out = df.copy()
    out["spatial_group_id"] = groups
    return out, groups


def stage_spatial_cv_stacking(
    df: pd.DataFrame,
    target: str,
    n_splits: int,
    n_clusters: int,
    random_state: int,
) -> tuple[np.ndarray, dict[str, float], list]:
    """OOF predictions + metrics; returns (oof, metrics, list of (scaler, model) per fold — last fold saved)."""
    lat = df["lat"] if "lat" in df.columns else df["Latitude"]
    lon = df["lon"] if "lon" in df.columns else df["Longitude"]
    cols = feature_columns(df, exclude_targets=True)
    X = df[cols].copy()
    X, medians = impute_median(X)
    y = df[target].values
    sgkf = SpatialGroupKFold(n_splits=n_splits, n_clusters=n_clusters, random_state=random_state)
    oof = np.zeros(len(y))
    last_scaler, last_model = None, None
    for tr, te in sgkf.split(np.zeros((len(y), 1)), lat=lat.values, lon=lon.values):
        sc = StandardScaler().fit(X.iloc[tr])
        Xtr, Xte = sc.transform(X.iloc[tr]), sc.transform(X.iloc[te])
        m = fit_stacking_per_target(Xtr, y[tr], random_state=random_state)
        oof[te] = m.predict(Xte)
        last_scaler, last_model = sc, m
    metrics = {
        "r2_oof": float(r2_score(y, oof)),
        "rmse_oof": float(np.sqrt(mean_squared_error(y, oof))),
        "n_samples": int(len(y)),
    }
    return oof, metrics, [(last_scaler, last_model, cols, medians)]


def stage_shap(
    model,
    X_sample: pd.DataFrame,
    out_dir: Path,
    target_name: str,
    max_samples: int = 2000,
) -> list[str]:
    paths = []
    try:
        import matplotlib.pyplot as plt
        import shap
        import lightgbm as lgb
    except ImportError:
        return paths
    out_dir.mkdir(parents=True, exist_ok=True)
    Xs = X_sample.astype(float)
    if len(Xs) > max_samples:
        Xs = Xs.sample(max_samples, random_state=42)
    # Surrogate LGB for SHAP (stacking meta is not tree-native)
    sur = lgb.LGBMRegressor(n_estimators=150, max_depth=6, verbose=-1, random_state=42)
    sur.fit(Xs, np.zeros(len(Xs)))
    y_hat = model.predict(Xs.values if hasattr(Xs, "values") else Xs)
    sur.fit(Xs, y_hat)
    explainer = shap.TreeExplainer(sur)
    sv = explainer.shap_values(Xs)
    if isinstance(sv, list):
        sv = sv[0]
    plt.figure(figsize=(10, 8))
    shap.summary_plot(sv, Xs, plot_type="bar", max_display=20, show=False)
    plt.title(f"SHAP — {target_name}")
    plt.tight_layout()
    p = out_dir / f"shap_summary_{target_name}.png"
    plt.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    paths.append(str(p))
    return paths


def stage_save_results(
    artifact_dir: Path,
    target: str,
    scaler: StandardScaler,
    model,
    feature_cols: list,
    medians: pd.Series,
    metrics: dict,
):
    artifact_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump({"scaler": scaler, "model": model, "feature_cols": feature_cols, "medians": medians}, artifact_dir / f"bundle_{target}.joblib")
    with open(artifact_dir / f"metrics_{target}.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


def _resolve_data_path(root: Path, raw_dir: str, csv_name: str) -> Path:
    """Config CSV path; if missing, try common alternatives in same dir."""
    raw_dir_path = root / raw_dir
    candidates = [csv_name, "water_quality_dataset_v1.csv", "water_quality.csv"]
    for name in candidates:
        p = raw_dir_path / name
        if p.exists():
            return p
    raise FileNotFoundError(
        f"No CSV en {raw_dir_path}. Prueba con: {', '.join(candidates)}"
    )


def run_full_pipeline(config_path: str | Path) -> PipelineResult:
    cfg = load_config(config_path)
    root = Path(config_path).resolve().parent.parent
    raw_dir = cfg["paths"]["raw_data"]
    raw = _resolve_data_path(root, raw_dir, cfg["data"]["water_quality_csv"])
    out_root = root / cfg["paths"].get("outputs", "outputs")
    fig_dir = out_root / "figures"
    art_dir = out_root / "artifacts"
    n_splits = cfg["validation"]["spatial"]["n_splits"]
    n_clust = cfg["validation"]["spatial"]["n_spatial_clusters"]
    rs = cfg.get("project", {}).get("random_state", 42)

    # 1. Load
    df = stage_load_data(raw)
    # 2. Features
    df = stage_feature_engineering(df)
    # 3. Clusters
    df, groups = stage_spatial_clustering(df, n_clust, rs)

    result = PipelineResult(config=cfg, cluster_ids=groups, artifact_dir=art_dir)
    targets = [t for t in cfg["project"]["targets"] if t in df.columns]

    # Maps: clusters
    try:
        import matplotlib.pyplot as plt
        from ..visualization.maps import plot_spatial_clusters, plot_sampling_points

        lat = df["lat"] if "lat" in df.columns else df["Latitude"]
        lon = df["lon"] if "lon" in df.columns else df["Longitude"]
        _, ax = plot_spatial_clusters(lon.values, lat.values, groups, out_path=fig_dir / "spatial_clusters.png")
        plt.close("all")
        result.figure_paths.append(str(fig_dir / "spatial_clusters.png"))
        _, ax = plot_sampling_points(lon.values, lat.values, title="Sampling sites", out_path=fig_dir / "sampling_points.png")
        plt.close("all")
        result.figure_paths.append(str(fig_dir / "sampling_points.png"))
    except Exception:
        pass

    cols = feature_columns(df, exclude_targets=True)
    X_full, _ = impute_median(df[cols].copy())

    for target in targets:
        oof, metrics, bundle = stage_spatial_cv_stacking(df, target, n_splits, n_clust, rs)
        result.metrics[target] = metrics
        result.oof_predictions[target] = oof
        sc, m, fcols, med = bundle[0]
        stage_save_results(art_dir, target, sc, m, fcols, med, metrics)
        shap_paths = stage_shap(m, X_full[fcols], fig_dir, target)
        result.figure_paths.extend(shap_paths)

    with open(out_root / "metrics_all.json", "w", encoding="utf-8") as f:
        json.dump(result.metrics, f, indent=2)

    return result


def run_all(config_path: str | Path = "config/config.yaml") -> dict:
    """Backward-compatible: metrics only."""
    r = run_full_pipeline(config_path)
    return r.metrics
