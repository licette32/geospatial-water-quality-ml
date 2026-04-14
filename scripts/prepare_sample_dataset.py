"""
Optional: build water_quality.csv from any folder that has
water_quality_training_dataset.csv + feature_engineered_training_set.csv
(same row order). Generic scientific use — no external branding.

Usage:
  py scripts/prepare_sample_dataset.py [path_to_data_dir]
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def merge(wq_path: Path, fe_path: Path, out: Path) -> None:
    wq = pd.read_csv(wq_path)
    fe = pd.read_csv(fe_path)
    drop = {"Unnamed: 0", "Total Alkalinity", "Electrical Conductance", "Dissolved Reactive Phosphorus"}
    fe = fe.drop(columns=[c for c in drop if c in fe.columns], errors="ignore")
    if len(wq) != len(fe):
        raise SystemExit("Row count mismatch")
    out_df = pd.concat([wq.reset_index(drop=True), fe.reset_index(drop=True)], axis=1)
    out_df = out_df.loc[:, ~out_df.columns.duplicated()]
    if "Latitude" in out_df.columns:
        out_df["lat"] = out_df["Latitude"]
    if "Longitude" in out_df.columns:
        out_df["lon"] = out_df["Longitude"]
    for old, new in [
        ("Total Alkalinity", "total_alkalinity"),
        ("Electrical Conductance", "electrical_conductance"),
        ("Dissolved Reactive Phosphorus", "dissolved_reactive_phosphorus"),
    ]:
        if old in out_df.columns and new not in out_df.columns:
            out_df[new] = out_df[old]
    out.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out, index=False)
    print("Wrote", out, "rows", len(out_df))


if __name__ == "__main__":
    data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "raw"
    wq = data_dir / "water_quality_training_dataset.csv"
    fe = data_dir / "feature_engineered_training_set.csv"
    if not wq.exists() or not fe.exists():
        print("Place water_quality_training_dataset.csv and feature_engineered_training_set.csv in", data_dir)
        print("Or pass directory as first argument.")
        sys.exit(1)
    merge(wq, fe, ROOT / "data" / "raw" / "water_quality.csv")
