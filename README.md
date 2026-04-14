# River water quality — geospatial machine learning

**Independent research software** for predicting in-river water quality from **coordinates**, optional **sample dates**, and **environmental predictors** (satellite, reanalysis, hydrology). Suitable for **portfolio** and **publication-style** workflows with explicit spatial validation and saved artifacts.

---

## Project overview

The repository implements an end-to-end **geospatial ML pipeline**:

1. Load tabular data (measurements + lat/lon + predictors).  
2. **Feature engineering** — temporal (month, season, rolling precipitation), scientific interactions (e.g. ET/precip), optional hydrology columns.  
3. **Spatial clustering** on coordinates → groups for cross-validation.  
4. **Spatial GroupKFold** — no train/test leakage across nearby sites.  
5. **Stacking ensemble** (LightGBM + XGBoost [+ CatBoost]) per target.  
6. **SHAP** summaries for interpretation.  
7. **Persisted outputs** — metrics JSON, trained bundles, figures.

Orchestration: **`scripts/run_full_workflow.py`** or Python API `src.pipelines.research_pipeline.run_full_pipeline`.

---

## Scientific motivation

River chemistry is controlled by **catchment processes**: dilution, evaporation, weathering, land cover, and flow routing. Environmental covariates at the sample location (and time) act as **proxies** for those processes. Because nearby samples share similar landscapes, **i.i.d. assumptions fail** — standard random train/test splits **inflate** performance. This project uses **spatially blocked validation** so metrics better reflect **prediction at unseen locations**.

Optional hydrologic attributes (**basin_id**, **upstream_area**, **distance_to_river**) further link predictions to **drainage structure**; see **[docs/HYDROLOGY_FEATURES.md](docs/HYDROLOGY_FEATURES.md)**.

---

## Data requirements

| Required | Description |
|----------|-------------|
| **lat**, **lon** | WGS84 recommended |
| **Targets** | Columns to predict (names in `config/config.yaml`) |
| **Predictors** | Numeric features (Landsat indices, ERA5, TerraClimate, soil, flow, etc.) |

| Optional | Description |
|----------|-------------|
| **sample_date** / **Sample Date** | Triggers **month**, **season**, **rolling precipitation** features |
| **precipitation** (or `ppt`, `total_precipitation_sum`) | Needed for rolling precip features |
| **basin_id**, **upstream_area**, **distance_to_river** | Hydrology; see HYDROLOGY_FEATURES.md |

Place the main table at **`data/raw/water_quality.csv`**.

Optional merge of two aligned CSVs:

```text
py scripts/prepare_sample_dataset.py path/to/folder
```

---

## Pipeline architecture

```
load_data
    → feature_engineering (temporal + scientific_interactions)
    → spatial_clustering (KMeans lat/lon → spatial_group_id)
    → spatial_cross_validation + stacking (per target)
    → SHAP (surrogate tree model on stacked predictions for visualization)
    → save_results (outputs/metrics_all.json, outputs/artifacts/bundle_*.joblib, outputs/figures/*.png)
```

Config: **`config/config.yaml`** (`paths.outputs`, `validation.spatial`, `project.targets`).

---

## Spatial machine learning

- **Clusters:** KMeans in geographic space → `spatial_group_id`.  
- **GroupKFold:** each fold holds out **entire groups** — training and test sites are **spatially separated**, reducing **spatial leakage**.  
- **Why random splits fail:** Train and test both contain neighbors; the model exploits **implicit spatial autocorrelation**; test R² is optimistic for **new regions**.

Teaching: **[docs/LEARNING_GUIDE.md](docs/LEARNING_GUIDE.md)** and **`notebooks/03_spatial_validation.ipynb`**.

---

## Model interpretability

- **Stacking** combines diverse gradient boosters; **Ridge** meta-learner blends their outputs.  
- **SHAP** (on a **surrogate** LightGBM fit to stacked predictions) gives **global bar plots** of driver importance — useful for **hypothesis alignment**, not causal claims.

Figures written to **`outputs/figures/`**.

---

## How to run the project

**1. Environment (Windows — if `pip` is not on PATH):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

**2. Data:** ensure **`data/raw/water_quality.csv`** exists (or run merge script).

**3. Full workflow:**

```powershell
py scripts/run_full_workflow.py
```

Optional merge + workflow:

```powershell
py scripts/run_full_workflow.py --merge-dir "path/to/data_folder"
```

**4. Notebooks (if Jupyter on PATH):**

```powershell
py -m jupyter lab notebooks/
```

**5. Programmatic:**

```python
from pathlib import Path
from src.pipelines.research_pipeline import run_full_pipeline
run_full_pipeline(Path("config/config.yaml"))
```

---

## Visualization

**`src/visualization/maps.py`**

| Function | Role |
|----------|------|
| `plot_sampling_points` | Sites map |
| `plot_spatial_clusters` | CV groups |
| `plot_prediction_map` | Observed vs predicted at samples |
| `plot_prediction_grid_map` | **Grid** over bbox; `predict_fn(lon, lat)` must fill non-spatial features (e.g. medians) |

---

## Learning materials

- **[docs/LEARNING_GUIDE.md](docs/LEARNING_GUIDE.md)** — pedagogy (spatial ML, ensembles, SHAP).  
- **notebooks/01…05** — step-by-step.  
- **[docs/DATASETS_REQUIRED.md](docs/DATASETS_REQUIRED.md)** — data checklist.  
- **[docs/SCIENCE_OVERVIEW.md](docs/SCIENCE_OVERVIEW.md)** — short design note.

---

## Citation & license

Cite this software and all **data products** you use (Landsat, ERA5, etc.) per their terms. Use for research and education; comply with upstream data licenses.
