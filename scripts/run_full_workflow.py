#!/usr/bin/env python3
"""
Full reproducible workflow (portfolio / research):

  1. Optional: merge aligned CSVs → data/raw/water_quality.csv
  2. Load + feature engineering + spatial clustering
  3. Spatial cross-validation + stacking per target
  4. SHAP figures
  5. Save metrics, artifacts, maps

Usage (from repo root):
  py -m pip install -r requirements.txt
  py scripts/run_full_workflow.py

If pip/jupyter are not on PATH, use:
  py -m pip install -r requirements.txt
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description="Run full geospatial ML workflow")
    parser.add_argument("--config", default=str(ROOT / "config" / "config.yaml"))
    parser.add_argument("--merge-dir", default=None, help="Folder with water_quality_training_dataset.csv + feature_engineered_training_set.csv")
    args = parser.parse_args()

    if args.merge_dir:
        import importlib.util
        spec = importlib.util.spec_from_file_location("prep", ROOT / "scripts" / "prepare_sample_dataset.py")
        prep = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(prep)
        merge = prep.merge
        d = Path(args.merge_dir)
        merge(d / "water_quality_training_dataset.csv", d / "feature_engineered_training_set.csv", ROOT / "data" / "raw" / "water_quality.csv")
        print("Merged → data/raw/water_quality.csv")

    from src.pipelines.research_pipeline import run_full_pipeline

    result = run_full_pipeline(args.config)
    print("Metrics:", result.metrics)
    print("Figures:", result.figure_paths)
    print("Artifacts:", result.artifact_dir)


if __name__ == "__main__":
    main()
