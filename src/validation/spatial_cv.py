"""
Spatial cross-validation for geospatial ML.

Nearby samples share environmental conditions; random splits leak information.
We cluster (lat, lon) and use GroupKFold so entire clusters are held out per fold.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.model_selection import BaseCrossValidator, GroupKFold
from typing import Iterator, Optional


def spatial_cluster_groups(
    lat: np.ndarray,
    lon: np.ndarray,
    n_clusters: int = 30,
    random_state: int = 42,
) -> np.ndarray:
    """
    Assign each point to a spatial cluster (KMeans in geographic space).
    Groups are used with GroupKFold: no train point shares a cluster with test.
    """
    X = np.column_stack([lat, lon])
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    return km.fit_predict(X)


class SpatialGroupKFold:
    """
    K-fold CV where folds respect spatial clusters (prevents spatial leakage).
    """

    def __init__(self, n_splits: int = 5, n_clusters: int = 30, random_state: int = 42):
        self.n_splits = n_splits
        self.n_clusters = n_clusters
        self.random_state = random_state
        self._gkf = GroupKFold(n_splits=n_splits)

    def split(
        self,
        X: np.ndarray | pd.DataFrame,
        y=None,
        groups: Optional[np.ndarray] = None,
        lat: Optional[np.ndarray] = None,
        lon: Optional[np.ndarray] = None,
    ) -> Iterator[tuple[np.ndarray, np.ndarray]]:
        if groups is None:
            if lat is None or lon is None:
                raise ValueError("Provide groups= or lat= and lon=")
            groups = spatial_cluster_groups(
                np.asarray(lat), np.asarray(lon), self.n_clusters, self.random_state
            )
        n = len(groups) if hasattr(groups, "__len__") else X.shape[0]
        indices = np.arange(n)
        for train_idx, test_idx in self._gkf.split(indices, y, groups):
            yield train_idx, test_idx

    def get_n_splits(self, X=None, y=None, groups=None) -> int:
        return self.n_splits


def spatial_train_test_split_groups(
    X: pd.DataFrame,
    y: np.ndarray,
    lat: np.ndarray,
    lon: np.ndarray,
    test_size: float = 0.2,
    n_clusters: int = 30,
    random_state: int = 42,
) -> tuple:
    """Hold out whole clusters as test (approximate test_size fraction of clusters)."""
    groups = spatial_cluster_groups(lat, lon, n_clusters, random_state)
    unique = np.unique(groups)
    rng = np.random.default_rng(random_state)
    rng.shuffle(unique)
    n_test_clusters = max(1, int(len(unique) * test_size))
    test_groups = set(unique[:n_test_clusters])
    test_mask = np.array([g in test_groups for g in groups])
    train_mask = ~test_mask
    tr, te = np.where(train_mask)[0], np.where(test_mask)[0]
    return X.iloc[tr], X.iloc[te], y[tr], y[te], groups
