# Notebook research summary

**Document purpose:** Rigorous summary of the analytical workflow implemented in the Jupyter notebooks of this repository, and how they support a reproducible geospatial machine learning study for river water quality prediction.

---

## 1. Overview

### Purpose of the notebooks

The notebooks implement a **step-by-step analytical workflow** for predicting in-river water quality (total alkalinity, electrical conductance, dissolved reactive phosphorus) from environmental covariates. They serve four main roles:

- **Exploratory analysis** — Inspecting the dataset, checking missing values, spatial coverage, and target distributions (Notebook 01).
- **Methodological validation** — Demonstrating why spatial cross-validation is necessary, comparing random vs spatial splits, and diagnosing model behavior (Notebooks 03, 06, 08).
- **Scientific interpretation** — Explaining which drivers matter (SHAP, feature importance, sensitivity curves), where the model errs (residual maps, error vs environment), and implications for hydrology (Notebooks 05, 06, 08, 09).
- **Model diagnostics** — Residual analysis, uncertainty from ensemble spread, stability of feature importance across folds, and prediction maps (Notebooks 06, 07, 08, 10).

### Relationship to the pipeline in `src/`

The notebooks **do not replace** the pipeline; they **complement** it. The production workflow is implemented in `src/pipelines/research_pipeline.py`, which runs:

1. Data loading  
2. Feature engineering (temporal + scientific interactions)  
3. Spatial clustering  
4. Spatial cross-validation with stacking  
5. SHAP explainability  
6. Saving of metrics, models, and figures  

The notebooks call the **same modules** from `src/` (e.g. `feature_columns`, `impute_median`, `SpatialGroupKFold`, `add_scientific_interactions`, `shap_summary_bar`) and illustrate each stage with explicit code and visualizations. They are used for teaching, debugging, and reporting; the pipeline is used for one-command reproducible runs.

---

## 2. Dataset used in the notebooks

### Source and location

All notebooks that load data use the same dataset:

- **Primary file:** `data/raw/water_quality_dataset_v1.csv`  
- **Fallback:** `data/raw/water_quality.csv` (if the primary file is absent)

The path is resolved at runtime (e.g. under `data/raw/`).

### Dimensions and structure

| Attribute        | Value   |
|-----------------|--------|
| **Dataset file**| `water_quality_dataset_v1.csv` |
| **Number of rows** | 9,319 |
| **Number of columns** | 41 |

Each row is one **sampling event** (location and date). Columns include identifiers (Latitude, Longitude, Sample Date), three target variables, and numeric predictors from multiple environmental sources.

### Target variables

| Column (normalized) | Description |
|---------------------|-------------|
| **total_alkalinity** | Acid-neutralizing capacity (e.g. mg/L as CaCO₃). |
| **electrical_conductance** | Conductivity; proxy for dissolved ions/salinity (e.g. µS/cm). |
| **dissolved_reactive_phosphorus** | Inorganic phosphorus in solution (e.g. µg/L). |

The notebooks and pipeline accept both display names (Total Alkalinity, etc.) and snake_case names; normalization is applied during load.

### Main feature categories

Summarized from `data/documentation/DATASET_DESCRIPTION.md`:

- **Satellite-derived:** NDVI, EVI, NDMI, MNDWI, Land Surface Temperature, reflectance bands (nir, green, swir16, swir22).  
- **Climate:** precipitation, total_precipitation_sum, total_evaporation_sum, temperature_2m, skin_temperature, soil_temperature, volumetric_soil_water, pet, evaporation_precipitation_ratio.  
- **Soil:** cec, clay, pH, phosphorous; derived interactions (cec_pH, phosphorous_pH, cec_clay_ratio).  
- **Hydrological:** flow_accumulation; flow_acc_clay and flow_acc_phosphorous interactions.  
- **Topography:** elevation.  

### Lineage and documentation

- **DATA_LINEAGE.md** (in `data/documentation/`) describes how the final table was built from upstream CSVs (e.g. water quality training data plus feature-engineered environmental and interaction variables).  
- **DATASET_DESCRIPTION.md** documents dimensions, targets, feature categories, geographic coverage (sub-Saharan Africa, WGS84), temporal coverage (multi-year sampling), environmental data sources (Landsat, MODIS, ERA5, CHIRPS, TerraClimate, NASADEM, iSDA, HydroSHEDS), and intended use (geospatial ML, environmental modeling, water quality prediction; not for regulatory decision making).

---

## 3. Notebook workflow

### Stages implemented across notebooks

The repository contains **ten** notebooks. All of the following exist and are part of the workflow:

| # | Notebook | Stage |
|---|----------|--------|
| 01 | `01_data_exploration.ipynb` | Data exploration |
| 02 | `02_feature_engineering.ipynb` | Feature engineering |
| 03 | `03_spatial_validation.ipynb` | Spatial validation |
| 04 | `04_model_training.ipynb` | Model training |
| 05 | `05_model_explainability.ipynb` | Model explainability |
| 06 | `06_spatial_model_diagnostics.ipynb` | Spatial model diagnostics |
| 07 | `07_spatial_prediction_maps.ipynb` | Spatial prediction mapping |
| 08 | `08_model_stability_analysis.ipynb` | Model stability analysis |
| 09 | `09_feature_sensitivity_analysis.ipynb` | Feature sensitivity analysis |
| 10 | `10_uncertainty_analysis.ipynb` | Uncertainty analysis |

**No notebooks from this list are missing.**

### Description of each stage

1. **Data exploration (01)** — Load dataset, normalize column names, inspect structure; visualize spatial coverage and target distributions; discuss missing data and the need for spatial validation.  
2. **Feature engineering (02)** — Build spectral indices (where band columns exist) and scientific interaction features (e.g. ET/precipitation, precipitation×runoff); document physical interpretation.  
3. **Spatial validation (03)** — Compute Moran's I for targets; perform spatial clustering and SpatialGroupKFold; compare random KFold vs SpatialGroupKFold (RMSE, R²); map residuals; interpret why spatial CV is necessary.  
4. **Model training (04)** — Train LightGBM, XGBoost, CatBoost with SpatialGroupKFold; optional RegressorChain and stacking; report spatial CV metrics per target.  
5. **Model explainability (05)** — SHAP summary (mean |SHAP|) and dependence plots for climate-related variables; interpret drivers of predictions.  
6. **Spatial model diagnostics (06)** — After spatial CV: residual map, residual distribution (histogram, KDE, bias, skewness), residuals vs environmental variables (with LOWESS if available), Moran's I on residuals, feature importance from full-data model; interpret spatial error patterns and missing structure.  
7. **Spatial prediction maps (07)** — Train one model per target on full data; build 100×100 grid over bounding box; interpolate features to grid via nearest-neighbor; predict and plot one map per target (lon, lat, color = prediction).  
8. **Model stability analysis (08)** — SpatialGroupKFold training; extract feature_importances_ per fold; mean and std of importance; coefficient of variation (std/mean) to flag unstable (region-dependent) predictors; interpret stable vs unstable features.  
9. **Feature sensitivity analysis (09)** — Train single model (e.g. LightGBM) on full data; for key variables (precipitation, elevation, NDVI, clay, temperature_2m), vary one over its range with others at median; plot response curves (x = variable, y = predicted target); interpret thresholds and nonlinearity.  
10. **Uncertainty analysis (10)** — Train LightGBM, RandomForest, XGBoost; predict with each; mean_prediction and prediction_std across models; histogram and spatial map of uncertainty; compare prediction error (|observed − mean_prediction|) vs prediction_std; interpret regions of high uncertainty and implications for monitoring.

### Workflow diagram

```
Dataset (water_quality_dataset_v1.csv)
        │
        ▼
┌───────────────────────┐
│ 01_data_exploration   │  Structure, coverage, targets
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│ 02_feature_engineering│  Spectral indices, interactions
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│ 03_spatial_validation │  Moran's I, clusters, random vs spatial CV
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│ 04_model_training     │  SpatialGroupKFold + stacking, multi-target
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│ 05_model_explainability│  SHAP summary and dependence
└───────────┬───────────┘
            │
            ├──────────────────────────────────────────────┐
            ▼                                              ▼
┌───────────────────────┐                    ┌───────────────────────┐
│ 06_spatial_model_     │                    │ 07_spatial_prediction_│
│    diagnostics        │                    │    maps                │
│ Residuals, Moran's I   │                    │ Grid + NN interpolation│
│ on residuals, drivers  │                    │ Maps per target       │
└───────────────────────┘                    └───────────────────────┘
            │                                              │
            ▼                                              ▼
┌───────────────────────┐                    ┌───────────────────────┐
│ 08_model_stability_    │                    │ 09_feature_sensitivity_│
│    analysis            │                    │    analysis           │
│ Importance stability   │                    │ Response curves       │
│ across folds, CV       │                    │ (one variable varied)  │
└───────────────────────┘                    └───────────────────────┘
            │
            ▼
┌───────────────────────┐
│ 10_uncertainty_       │
│    analysis           │
│ Ensemble spread,      │
│ error vs uncertainty  │
└───────────────────────┘
```

---

## 4. Methods implemented

### Main analytical methods

- **Spatial clustering** — KMeans on (lat, lon) to partition the study area into spatial groups. Used so that cross-validation folds hold out **entire regions** rather than random subsets. Implemented in `src/validation/spatial_cv.py` and used in notebooks 03, 04, 06, 08.  
- **Spatial cross-validation (SpatialGroupKFold)** — GroupKFold with group labels given by spatial clusters. Each fold uses some clusters for training and others for testing, avoiding spatial leakage.  
- **Stacking ensemble** — Multiple base models (LightGBM, XGBoost, CatBoost) with a meta-learner (e.g. Ridge) on their predictions. Used in the pipeline and in notebook 04.  
- **SHAP explainability** — Shapley-based feature contributions for tree models: global summary (mean absolute SHAP) and dependence plots. Implemented in `src/models/explainability.py` and used in notebooks 05 and the pipeline.  
- **Residual spatial analysis** — Residuals (observed − predicted) mapped in space; Moran's I computed on residuals to detect remaining spatial structure. Used in notebooks 03 and 06.  
- **Feature sensitivity analysis** — One-at-a-time variation of a predictor over its observed range while holding others at the median; prediction curves show marginal, possibly nonlinear, effects. Implemented in notebook 09.  
- **Uncertainty estimation** — Ensemble of different model types; standard deviation of their predictions used as a proxy for prediction uncertainty. Implemented in notebook 10.

### Why these methods are appropriate for geospatial environmental modeling

- **Spatial clustering and spatial CV** address the non-independence of nearby observations (same climate, geology, land use). Random splits underestimate generalization error to new locations; spatial CV gives a more honest estimate for mapping and transfer.  
- **Stacking** combines different algorithms to reduce variance and often improves robustness with noisy, mixed-scale environmental covariates.  
- **SHAP** supports communication with domain experts and helps identify which environmental drivers the model uses, without assuming linearity.  
- **Residual maps and Moran's I on residuals** reveal where and whether the model still misses spatial structure, guiding data collection or model refinement.  
- **Sensitivity curves** summarize how predictions respond to key variables (e.g. precipitation, elevation), supporting process interpretation and scenario discussion.  
- **Ensemble-based uncertainty** highlights locations where models disagree, useful for prioritizing monitoring or conservative interpretation.

---

## 5. Key findings from the analysis

The following summarizes results **taken from the actual notebook outputs** (executed on `water_quality_dataset_v1.csv`).

- **Moran's I** — Notebook 03 reports Moran's I for the three targets (subsample n≈2500, k=10 neighbors). All show strong positive autocorrelation: total_alkalinity I = 0.79, z ≈ 93.07; electrical_conductance I = 0.79, z ≈ 92.07; dissolved_reactive_phosphorus I = 0.55, z ≈ 71.95. With |z| > 2.58, all are significant at p < 0.01 (two-tailed), justifying spatial cross-validation.  
- **Random vs spatial CV** — In notebook 03, for total_alkalinity: **Random KFold** RMSE = 29.87, R² = 0.84; **SpatialGroupKFold** RMSE = 62.85, R² = 0.29. Spatial CV yields much higher RMSE and lower R²; this reflects **honest** evaluation for prediction at new locations, not a weak model.  
- **Spatial CV metrics (Notebook 04)** — With stacking and SpatialGroupKFold, the reported metrics are: total_alkalinity R² = 0.335, RMSE = 60.90; electrical_conductance R² = 0.268, RMSE = 292.46; dissolved_reactive_phosphorus R² = 0.018, RMSE = 50.51. Alkalinity and conductance have moderate spatial predictive skill; phosphorus is very hard to predict spatially.  
- **Residual diagnostics (Notebook 06)** — For total_alkalinity (spatial CV): mean residual (bias) = 5.33, skewness = 0.49, kurtosis = 0.79. Moran's I on residuals I = 0.67, z ≈ 86.30, so residuals remain strongly spatially autocorrelated → the model still misses part of the spatial structure.  
- **Feature importance stability (Notebook 08)** — With threshold CV > 0.5: **0 unstable** and **30 stable** features; all analysed predictors show relatively stable importance across spatial folds.  
- **Uncertainty (Notebook 10)** — Prediction std (ensemble spread): mean = 7.40, max = 93.87. Correlation between absolute error and prediction_std = 0.77, so higher ensemble disagreement tends to co-occur with larger errors.  
- **Main predictors** — Feature importance and SHAP (notebooks 05, 06, 08) highlight which variables drive predictions; stability analysis (08) indicates that, for this run, all considered features were stable across folds.  
- **Spatial patterns of error** — Residual maps (notebooks 03, 06) show where the model over- or under-predicts; residual Moran's I (06) confirms remaining spatial structure in errors.

---

## 6. Model evaluation strategy

### Random KFold

- **Implementation:** Standard KFold with shuffle (e.g. 5 folds). Samples are split randomly into train and test.  
- **Use:** In notebook 03, a baseline model is evaluated with random KFold to **compare** with SpatialGroupKFold.  
- **Limitation:** Neighboring locations can appear in both train and test. Test error is then **optimistic** for the task of predicting at new, unsampled locations.

### SpatialGroupKFold

- **Implementation:** First, spatial clusters are obtained (e.g. KMeans on lat/lon). Then GroupKFold is applied with cluster IDs as groups, so that **entire clusters** are either in train or in test for each fold.  
- **Use:** This is the **primary** evaluation method in the pipeline and in notebooks 03, 04, 06, 08. Metrics from spatial CV are reported as the main performance summary.  
- **Advantage:** Mimics deployment to new regions; reduces spatial leakage and gives a more realistic estimate of generalization.

### Why spatial cross-validation is necessary

In geospatial data, **proximity implies similarity** (shared catchment, climate, geology). A random split allows the model to “see” the same landscape in train and test, so test error underestimates **transfer error**. For **mapping** and **prediction at new sites**, validation must hold out **whole regions**. SpatialGroupKFold does this by construction. The notebooks (especially 03) and `docs/LEARNING_GUIDE.md` explain this rationale in detail.

---

## 7. Model diagnostics

- **Residual analysis (Notebook 06)** — After spatial CV, residuals (observed − predicted) are stored and analyzed: histogram and KDE, bias (mean residual), skewness, kurtosis. This reveals systematic bias and non-normal error distributions.  
- **Spatial error patterns** — Residuals are mapped in geographic space (scatter: lon, lat, color = residual). Clusters of positive or negative residuals indicate **regional bias** or missing spatial drivers.  
- **Environmental drivers of error** — Residuals are plotted against key variables (e.g. elevation, precipitation, NDVI, clay, temperature_2m), with LOWESS smoothing when available. Systematic trends (e.g. underprediction at high elevation) suggest under-used or missing predictors.  
- **Moran's I on residuals** — If residuals remain spatially autocorrelated, the model has not fully captured spatial structure; this may call for additional spatial features or regional models.  
- **Feature importance stability (Notebook 08)** — Importance is computed per spatial fold. High coefficient of variation (std/mean) across folds flags **region-dependent** predictors; low CV indicates **stable** drivers that are more reliable for interpretation and transfer.

Together, these diagnostics show **where** and **why** the model fails, and which predictors are robust across space.

---

## 8. Limitations of the analysis

- **Spatial extrapolation** — Predictions and maps are most reliable **within** the spatial and environmental range of the training data. Extrapolation to distant or very different regions (e.g. different climate or geology) is uncertain; the notebooks and documentation state this.  
- **Cluster definition** — Spatial groups are based on KMeans on (lat, lon). This is scale-dependent and does not use watershed boundaries or other process-based groupings. Alternative definitions (e.g. by basin) could be used if available.  
- **Missing predictors** — The dataset may not include all relevant drivers (e.g. land cover, point sources, soil depth). Residual patterns and sensitivity analysis help identify potential gaps but cannot add missing data.  
- **Temporal variability** — Sampling spans multiple years; temporal alignment of climate and satellite predictors with sample dates depends on the original products. The analysis does not fully separate temporal from spatial effects (e.g. no dedicated temporal CV).  
- **Nearest-neighbor interpolation (Notebook 07)** — Grid predictions assign to each grid point the feature vector of the nearest sample. This does not perform true spatial interpolation of each covariate (e.g. kriging) and can produce step-like patterns.  
- **In-sample uncertainty (Notebook 10)** — Uncertainty is derived from ensemble spread on the same data used for training. Correlation between uncertainty and error is informative but can be weak when all models are similarly wrong; out-of-sample validation (e.g. spatial CV) remains the reference for performance.

---

## 9. Reproducibility

### Dataset location

- **Primary:** `data/raw/water_quality_dataset_v1.csv`  
- **Alternative:** `data/raw/water_quality.csv`  
Notebooks resolve the path under `data/raw/` (and optionally the project root).

### Modules imported from `src/`

Notebooks rely on the same codebase for consistency and reproducibility:

- **Data:** `src.features.preprocess.feature_columns`, `impute_median`; often `src.data.load_data` or equivalent logic inlined (normalization of column names).  
- **Validation:** `src.validation.spatial_cv.spatial_cluster_groups`, `SpatialGroupKFold`.  
- **Features:** `src.features.scientific_interactions.add_scientific_interactions`, `src.features.temporal_features.add_temporal_features` (in pipeline and some notebooks).  
- **Models:** `src.models.multi_target` (e.g. `fit_stacking_per_target`), `src.models.explainability` (e.g. `shap_summary_bar`, `shap_dependence_climate`).  
- **Visualization:** `src.visualization.maps` (e.g. `plot_spatial_clusters`, `plot_prediction_map`).

The full pipeline is run via `src.pipelines.research_pipeline` and orchestrated by `scripts/run_full_workflow.py`.

### Required Python libraries

From `requirements.txt` and notebook usage:

- **Core:** pandas, numpy, scikit-learn  
- **Models:** lightgbm, xgboost, catboost  
- **Spatial/IO:** geopandas, rasterio (optional for some steps)  
- **Config and viz:** pyyaml, matplotlib, shap  
- **Notebooks:** jupyter, ipykernel  
- **Other:** scipy (e.g. distance, stats), statsmodels (optional, for LOWESS in notebook 06)

Installing from `requirements.txt` and running notebooks from the project root (so that `src` is on the path) ensures the same environment and behavior.

---

## 10. Overall evaluation

### Strengths of the methodology

- **Spatial validation is central** — SpatialGroupKFold and Moran's I are used to justify and implement validation that respects spatial dependence. This is a strength compared to workflows that rely only on random splits.  
- **Multi-target stacking** — The pipeline and notebook 04 train a stacking ensemble per target and report metrics for all three water quality variables, with a clear multi-step workflow.  
- **Interpretability** — SHAP, feature importance, sensitivity curves, and residual diagnostics support scientific interpretation and communication with domain experts.  
- **Diagnostics and uncertainty** — Residual maps, Moran's I on residuals, stability of importance across folds, and ensemble-based uncertainty provide multiple views on model reliability and where to improve.  
- **Modularity and reproducibility** — Notebooks call shared `src/` modules; the pipeline can be run end-to-end via config and scripts; documentation (DATASET_DESCRIPTION, DATA_LINEAGE, LEARNING_GUIDE) supports replication and extension.

### Rigor of spatial validation

- Spatial autocorrelation is **tested** (Moran's I) and used to motivate spatial CV.  
- **Random vs spatial CV** are compared explicitly (notebook 03), and the lower performance under spatial CV is correctly framed as **honest** evaluation for prediction at new locations.  
- Cluster-based GroupKFold is **consistent** across the pipeline and notebooks (same `n_clusters`, `n_splits` where applicable).  
- Limitations (extrapolation, cluster definition, in-sample uncertainty) are stated in the notebooks and in this summary.

### Interpretability of results

- **Global:** SHAP and feature importance rank drivers; stability analysis (CV across folds) separates stable from region-dependent predictors.  
- **Marginal:** Sensitivity curves show how predictions change with one variable at a time (others at median).  
- **Spatial:** Residual maps and uncertainty maps show where the model is wrong or uncertain.  
- **Process-oriented:** Documentation and markdown in the notebooks link results to hydrology and environmental monitoring (e.g. dilution, weathering, extrapolation limits).

### How the notebooks support a reproducible geospatial ML study

The notebooks provide a **transparent**, step-by-step account of the analytical workflow: from data exploration and feature engineering, through spatial validation and model training, to explainability, diagnostics, prediction maps, stability, sensitivity, and uncertainty. They use a **single documented dataset** and the **same** preprocessing and validation logic as the pipeline in `src/`. Together with the pipeline scripts and documentation (dataset description, lineage, learning guide), they support a **reproducible** geospatial machine learning study for river water quality prediction, suitable for research, teaching, and further development.

---

## 11. Experimental results

This section reports **numerical results extracted from the executed notebook outputs** (dataset: `water_quality_dataset_v1.csv`, 9,319 rows). Metrics may vary slightly if notebooks are re-run (e.g. different random seeds or versions).

### 11.1 Spatial autocorrelation (Notebook 03)

Moran's I was computed on a subsample (n ≈ 2,500, k = 10 nearest neighbors, inverse-distance weights). Significance is indicated by |z| > 2.58 (≈ p < 0.01, two-tailed). The notebooks report z-scores from a permutation-based approximation; formal p-values are not printed.

| Target | Moran's I | z-score | Interpretation |
|--------|-----------|---------|----------------|
| total_alkalinity | 0.7943 | ≈ 93.07 | Strong positive autocorrelation *** |
| electrical_conductance | 0.7897 | ≈ 92.07 | Strong positive autocorrelation *** |
| dissolved_reactive_phosphorus | 0.5536 | ≈ 71.95 | Moderate–strong positive autocorrelation *** |

**Interpretation:** All three targets are strongly spatially autocorrelated. Nearby locations tend to have similar water chemistry. Random train/test splits would therefore leak spatial information; spatial cross-validation is required for honest performance estimates.

### 11.2 Model performance under SpatialGroupKFold (Notebooks 03, 04)

- **Notebook 03** (single baseline model, target = total_alkalinity): comparison of **Random KFold** vs **SpatialGroupKFold** (5 folds, 30 clusters).

| Method | RMSE | R² |
|--------|------|-----|
| Random KFold | 29.87 | 0.8401 |
| SpatialGroupKFold | 62.85 | 0.2920 |

- **Notebook 04** (stacking ensemble, SpatialGroupKFold): performance **per target**. MAE is not reported in the current notebook outputs but can be computed from the same out-of-fold predictions if needed.

| Target | R² | RMSE |
|--------|-----|------|
| total_alkalinity | 0.335 | 60.899 |
| electrical_conductance | 0.268 | 292.456 |
| dissolved_reactive_phosphorus | 0.018 | 50.513 |

**Interpretation:** Spatial CV gives much worse metrics than random CV for the same model, which is expected when spatial autocorrelation is strong. The stacking ensemble achieves moderate explanatory power for alkalinity and conductance (R² ≈ 0.27–0.34) and very low for dissolved reactive phosphorus (R² ≈ 0.02), consistent with stronger local/non-stationary drivers for P.

### 11.3 Residual diagnostics (Notebook 06, target = total_alkalinity)

Out-of-fold predictions from SpatialGroupKFold; residuals = observed − predicted.

| Metric | Value |
|--------|--------|
| Spatial CV RMSE | 62.85 |
| Spatial CV R² | 0.2920 |
| Bias (mean residual) | 5.33 |
| Skewness | 0.49 |
| Kurtosis | 0.79 |
| Moran's I (residuals) | 0.6665 |
| z-score (residuals) | ≈ 86.30 |

**Interpretation:** Positive bias indicates slight systematic overprediction on average. Skewness and kurtosis suggest a somewhat right-skewed but not heavily tailed residual distribution. **Moran's I on residuals remains high** (I = 0.67, z ≈ 86), so the model has not fully captured spatial structure; regional biases or missing spatial predictors are likely.

### 11.4 Feature importance stability (Notebook 08)

Stability is assessed by the coefficient of variation (CV = std / mean) of feature importance across 5 spatial folds (30 clusters). Threshold for “unstable”: CV > 0.5.

| Category | Count |
|----------|--------|
| Unstable (CV > 0.5) | 0 |
| Stable (CV ≤ 0.5) | 30 |

**Interpretation:** In this run, all 30 analysed features had CV ≤ 0.5, i.e. importance rankings were relatively stable across spatial folds. Mean importance, standard deviation, and CV per feature are computed in the notebook (bar chart with error bars); the summary here shows that no predictor was classified as highly region-dependent for this target and fold setup.

### 11.5 Uncertainty analysis (Notebook 10, target = total_alkalinity)

Ensemble: LightGBM, RandomForest, XGBoost. Uncertainty proxy = standard deviation of predictions across the three models (prediction_std).

| Metric | Value |
|--------|--------|
| Mean prediction (min, max) | 3.41, 352.54 |
| prediction_std — mean | 7.40 |
| prediction_std — max | 93.87 |
| Correlation (absolute error, prediction_std) | 0.7688 |

**Interpretation:** Higher ensemble spread (prediction_std) is associated with larger absolute prediction errors (correlation ≈ 0.77). The uncertainty proxy is therefore informative: locations where the models disagree tend to be those where the mean prediction is less accurate. For monitoring, reporting mean_prediction ± prediction_std (or percentiles) can help flag less reliable areas.

### 11.6 Sensitivity analysis (Notebook 09)

Notebook 09 trains a single model (e.g. LightGBM) on full data for **total_alkalinity** and plots **response curves**: one variable varied over its observed range, others fixed at median. The notebook does not print summary statistics for these curves; the main outputs are the plots.

- **Main trends:** Response curves show how predicted total_alkalinity changes with precipitation, elevation, NDVI, clay, and temperature_2m. The curves are often **nonlinear** (e.g. plateau or threshold effects), consistent with tree-based models.
- **Thresholds / nonlinearities:** Specific thresholds are not reported numerically in the notebook; they can be read from the figures. Typical patterns include: higher elevation or lower precipitation associated with different predicted alkalinity levels; NDVI and soil/climate variables showing non-linear marginal effects.
- **Implications:** Sensitivity analysis supports process-oriented interpretation (e.g. dilution vs. weathering) and helps identify variables for which the model’s response is most sensitive; it does not imply causation.
