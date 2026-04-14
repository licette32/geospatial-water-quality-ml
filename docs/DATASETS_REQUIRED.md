# Data requirements

See **README.md** (Data requirements) and **docs/HYDROLOGY_FEATURES.md**.

Minimum: **`data/raw/water_quality_dataset_v1.csv`** (or `water_quality.csv`) with `lat`, `lon`, numeric predictors, and target columns named in `config/config.yaml`.

Optional: **`sample_date`** → temporal features; **`precipitation`** → rolling features; **`basin_id`**, **`upstream_area`**, **`distance_to_river`** → hydrology.

Merge helper:

```bash
py scripts/prepare_sample_dataset.py path/to/folder
```

Full run:

```bash
py scripts/run_full_workflow.py
```
