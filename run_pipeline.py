#!/usr/bin/env python3
"""Run spatial CV + stacking over configured targets."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.pipelines.research_pipeline import run_all

if __name__ == "__main__":
    out = run_all(ROOT / "config" / "config.yaml")
    print(json.dumps(out, indent=2))
