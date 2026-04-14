"""
Geospatial visualization: points, clusters, predictions, and grid maps.
"""

from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np
import matplotlib.pyplot as plt


def plot_sampling_points(
    lon: np.ndarray,
    lat: np.ndarray,
    values: Optional[np.ndarray] = None,
    cmap: str = "viridis",
    title: str = "Sampling locations",
    out_path: Optional[str | Path] = None,
    figsize: tuple = (8, 7),
):
    fig, ax = plt.subplots(figsize=figsize)
    if values is not None:
        sc = ax.scatter(lon, lat, c=values, cmap=cmap, s=12, alpha=0.75, edgecolors="none")
        plt.colorbar(sc, ax=ax, shrink=0.8)
    else:
        ax.scatter(lon, lat, s=10, alpha=0.6, c="steelblue")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(title)
    ax.set_aspect("equal", adjustable="box")
    plt.tight_layout()
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
    return fig, ax


def plot_spatial_clusters(
    lon: np.ndarray,
    lat: np.ndarray,
    cluster_ids: np.ndarray,
    title: str = "Spatial clusters (CV groups)",
    out_path: Optional[str | Path] = None,
    figsize: tuple = (8, 7),
):
    fig, ax = plt.subplots(figsize=figsize)
    sc = ax.scatter(lon, lat, c=cluster_ids, cmap="tab20", s=14, alpha=0.85, edgecolors="k", linewidths=0.2)
    plt.colorbar(sc, ax=ax, label="Cluster id", shrink=0.8)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(title)
    ax.set_aspect("equal", adjustable="box")
    plt.tight_layout()
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
    return fig, ax


def plot_prediction_map(
    lon: np.ndarray,
    lat: np.ndarray,
    y_true: Optional[np.ndarray],
    y_pred: np.ndarray,
    target_name: str = "target",
    out_path: Optional[str | Path] = None,
    figsize: tuple = (14, 6),
):
    ncols = 2 if y_true is not None else 1
    fig, axes = plt.subplots(1, ncols, figsize=figsize)
    if ncols == 1:
        axes = np.array([axes])
    if y_true is not None:
        sc0 = axes[0].scatter(lon, lat, c=y_true, cmap="viridis", s=12, alpha=0.8)
        plt.colorbar(sc0, ax=axes[0], shrink=0.8)
        axes[0].set_title(f"Observed {target_name}")
        sc1 = axes[1].scatter(lon, lat, c=y_pred, cmap="viridis", s=12, alpha=0.8)
        plt.colorbar(sc1, ax=axes[1], shrink=0.8)
        axes[1].set_title(f"Predicted {target_name}")
    else:
        sc = axes[0].scatter(lon, lat, c=y_pred, cmap="plasma", s=12, alpha=0.8)
        plt.colorbar(sc, ax=axes[0], shrink=0.8)
        axes[0].set_title(f"Predicted {target_name}")
    for ax in axes.flat:
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_aspect("equal", adjustable="box")
    plt.tight_layout()
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
    return fig, axes


def build_prediction_grid(
    lon_min: float,
    lon_max: float,
    lat_min: float,
    lat_max: float,
    n_lon: int = 40,
    n_lat: int = 40,
) -> tuple[np.ndarray, np.ndarray]:
    """Regular lon/lat grid for mapping (WGS84)."""
    lon = np.linspace(lon_min, lon_max, n_lon)
    lat = np.linspace(lat_min, lat_max, n_lat)
    LON, LAT = np.meshgrid(lon, lat)
    return LON.ravel(), LAT.ravel()


def predict_on_grid(
    predict_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
    lon_min: float,
    lon_max: float,
    lat_min: float,
    lat_max: float,
    n_lon: int = 50,
    n_lat: int = 50,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    predict_fn(lon_vec, lat_vec) -> predictions (same length).
    Returns LON, LAT meshes and Z predictions on grid for pcolormesh/contourf.
    """
    lon = np.linspace(lon_min, lon_max, n_lon)
    lat = np.linspace(lat_min, lat_max, n_lat)
    LON, LAT = np.meshgrid(lon, lat)
    pred = predict_fn(LON.ravel(), LAT.ravel())
    Z = pred.reshape(LON.shape)
    return LON, LAT, Z


def plot_prediction_grid_map(
    lon_min: float,
    lon_max: float,
    lat_min: float,
    lat_max: float,
    predict_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
    target_name: str = "prediction",
    sample_lon: Optional[np.ndarray] = None,
    sample_lat: Optional[np.ndarray] = None,
    n_lon: int = 45,
    n_lat: int = 45,
    cmap: str = "viridis",
    title: Optional[str] = None,
    out_path: Optional[str | Path] = None,
    figsize: tuple = (9, 8),
):
    """
    Raster-style map: model evaluated on a dense grid (other inputs held fixed
    inside predict_fn). Overlay optional sample points.
    """
    LON, LAT, Z = predict_on_grid(predict_fn, lon_min, lon_max, lat_min, lat_max, n_lon, n_lat)
    fig, ax = plt.subplots(figsize=figsize)
    pcm = ax.pcolormesh(LON, LAT, Z, shading="auto", cmap=cmap)
    plt.colorbar(pcm, ax=ax, shrink=0.8, label=target_name)
    if sample_lon is not None and sample_lat is not None:
        ax.scatter(sample_lon, sample_lat, c="k", s=8, alpha=0.35, label="Samples")
        ax.legend(loc="upper right")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(title or f"Gridded prediction — {target_name}")
    ax.set_aspect("equal", adjustable="box")
    plt.tight_layout()
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
    return fig, ax, Z
