# Learning guide — geospatial ML for river water quality

This guide explains **why** the pipeline is built as it is, so you can run and extend it without relying only on automated tools.

---

## Why spatial ML is necessary

Water quality observations are **spatially dependent**: two sites close together share similar **geology, climate, land cover, and upstream area**. Standard statistics often assume **independent** observations. In rivers, that assumption is **wrong**. A model can achieve high accuracy by learning **where** samples lie (directly or through correlated features), not only **why** chemistry varies. For **management and mapping in new areas**, you need validation that mimics **prediction at new locations** — that is **spatial machine learning**.

---

## Why random train/test splits fail

If you split rows **at random**, many **neighboring** sites fall in **both** train and test. The test set is not an independent draw from the same process; it **repeats** spatial context already seen in training. **Test error becomes optimistically low** while **deployment error** (new basins or regions) can be much higher. This is called **spatial leakage**. The fix is to **block** validation by **space** (or by basin), so the model is scored only on **held-out regions**.

---

## How ensembles improve robustness

**LightGBM**, **XGBoost**, and (optionally) **CatBoost** each optimize slightly different **tree structures** and **splits**. Their errors on hard samples are **partially uncorrelated**. **Stacking** trains a **meta-model** (here, Ridge regression) on the **concatenated predictions** of the base models. The meta-model learns **weights** that reduce variance and often **improve** generalization compared to any single algorithm. Ensembles do **not** guarantee better spatial transfer, but they usually **stabilize** predictions under noisy environmental data.

---

## How SHAP helps scientific interpretation

**SHAP** (SHapley Additive exPlanations) assigns each feature a **contribution** to each prediction, consistent with a fair allocation rule from game theory. **Global summaries** (mean absolute SHAP) rank **which environmental variables** move predictions most across the dataset. **Dependence plots** show **how** a variable’s values relate to higher or lower predictions. SHAP supports **communication** with hydrologists and managers (“model pays attention to precipitation and upstream area”) but does **not** prove **causality** — confounding and spatial structure still matter.

---

## Workflow summary

1. **Data** — lat/lon, targets, predictors; optional date and hydrology columns.  
2. **Features** — temporal encodings; rolling precip along date order; interaction terms (ET/precip, etc.).  
3. **Spatial CV** — cluster coordinates → GroupKFold by cluster.  
4. **Training** — stacking per target; save scaler + model + imputation medians.  
5. **Interpretation** — SHAP figures; maps (points, clusters, grids).  

---

## Repository map

| Path | Role |
|------|------|
| `src/pipelines/research_pipeline.py` | Full staged pipeline + saves |
| `src/features/temporal_features.py` | Month, season, rolling precip |
| `src/features/scientific_interactions.py` | Hydrology/geochemistry interactions |
| `docs/HYDROLOGY_FEATURES.md` | basin_id, upstream_area, distance_to_river |
| `src/validation/spatial_cv.py` | Clusters + GroupKFold |
| `scripts/run_full_workflow.py` | One-command reproducible run |
| `outputs/` | metrics, artifacts, figures (gitignored optional) |

---

## Running and reproducibility

Use a **fixed** `random_state` in config. Save **metrics** and **joblib bundles** after each run. Document **data version** and **config** in a lab notebook or README section for any publication or portfolio entry.

```bash
py -m pip install -r requirements.txt
py scripts/run_full_workflow.py
```

---

*Independent research pipeline — no competition-specific framing.*
