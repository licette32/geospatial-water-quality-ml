# Dataset and pipeline audit — full report

Rigorous audit of the data used by the pipeline and of all column expectations across the repository. Assumes scientific-quality geospatial ML.

---

## 1. Dataset inspected

**Source:** `data/raw/water_quality_dataset_v1.csv` (or `data/raw/water_quality.csv` if the first is missing).

**Columns in current dataset (41 total):**

| # | Column |
|---|--------|
| 1 | Latitude |
| 2 | Longitude |
| 3 | Sample Date |
| 4 | Total Alkalinity |
| 5 | Electrical Conductance |
| 6 | Dissolved Reactive Phosphorus |
| 7 | pet |
| 8 | elevation |
| 9 | EVI |
| 10 | NDVI |
| 11 | Land Surface Temperature |
| 12 | nir |
| 13 | green |
| 14 | swir16 |
| 15 | swir22 |
| 16 | NDMI |
| 17 | MNDWI |
| 18 | cec |
| 19 | clay |
| 20 | pH |
| 21 | phosphorous |
| 22 | flow_accumulation |
| 23 | skin_temperature |
| 24 | soil_temperature |
| 25 | temperature_2m |
| 26 | total_evaporation_sum |
| 27 | total_precipitation_sum |
| 28 | volumetric_soil_water |
| 29 | precipitation |
| 30 | cec_pH_interaction |
| 31 | phosphorous_pH_interaction |
| 32 | NDVI_LST_interaction |
| 33 | flow_acc_clay_interaction |
| 34 | flow_acc_phosphorous_interaction |
| 35 | evaporation_precipitation_ratio |
| 36 | cec_clay_ratio |
| 37 | lat |
| 38 | lon |
| 39 | total_alkalinity |
| 40 | electrical_conductance |
| 41 | dissolved_reactive_phosphorus |

*(Columns 37–41 are added or normalized by `load_data.py` when reading from CSV with Latitude/Longitude and alternate target column names.)*

---

## 2. Where the code expects or uses columns

### 2.1 Required by pipeline (must exist for training)

| Module | Columns | Notes |
|--------|---------|--------|
| **load_data.py** | `lat` or `Latitude`; `lon` or `Longitude` | Normalized to `lat`, `lon`. Required for spatial CV and maps. |
| **load_data.py** | At least one of: `total_alkalinity`, `electrical_conductance`, `dissolved_reactive_phosphorus` (or alternate column names) | Config lists all three; pipeline trains only on targets present in `df.columns`. |
| **preprocess.feature_columns()** | At least one numeric column not in {id_cols, targets} | Otherwise feature matrix is empty and pipeline fails. |

**Conclusion:** The dataset has **lat**, **lon**, all three targets, and many numeric predictors → **all required data for the current pipeline is present.**

### 2.2 Optional — used when present

| Module | Columns checked / used | In dataset? |
|--------|-------------------------|-------------|
| **temporal_features** | Date: `sample_date`, `Sample Date`, `sampledate`, `date` | ✅ Sample Date |
| **temporal_features** | Precip for rolling: `precipitation`, `precip`, `ppt`, `total_precipitation_sum` | ✅ precipitation, total_precipitation_sum |
| **scientific_interactions** | ET: `aet`, `pet`, `total_evaporation_sum` | ✅ pet, total_evaporation_sum |
| **scientific_interactions** | Precip: `precipitation`, `total_precipitation_sum`, `ppt` | ✅ |
| **scientific_interactions** | Runoff: `q`, `flow_accumulation`, `runoff` | ✅ flow_accumulation |
| **scientific_interactions** | Soil moisture: `volumetric_soil_water`, `soil`, `soil_moisture` | ✅ volumetric_soil_water |
| **scientific_interactions** | NDMI for soil_moisture_ndmi | ✅ NDMI |
| **scientific_interactions** | cond_alk: `electrical_conductance`, `total_alkalinity` (or aliases) | ✅ (as targets; ratio still computed) |
| **validation (spatial_cv)** | `lat`, `lon` (from df) | ✅ |
| **visualization (maps)** | `lon`, `lat` arrays passed by caller | From df ✅ |
| **explainability** | Any `X.columns`; climate plot uses one feature name in `X` | Uses whatever feature_columns() returns ✅ |

All of these are **optional** in the sense that the code uses `if c in df.columns` or `.get(..., None)`; no run fails if a column is missing, but derived features (e.g. et_precip_ratio, precip_roll_7d) are only created when the needed columns exist. In the current dataset they do.

### 2.3 Not used by the current pipeline

| Module | Columns | Notes |
|--------|---------|--------|
| **spectral_indices** | B2, B3, B4, B5, B6, B7 (or blue, green, red, nir, swir1, swir2) | **Not called** by `research_pipeline.py` (mode: tabular). Dataset already has NDVI, NDMI, MNDWI, etc. |
| **extract_landsat** | — | Not invoked; would write band columns from rasters. |
| **extract_climate** | — | Not invoked; would write e.g. precipitation, temperature from rasters. |
| **environmental_features.build_environmental_features** | — | Not called by pipeline; would add spectral indices + cleanup. |

---

## 3. Columns referenced in code but missing from the dataset

**None.** Every place that uses column names either:

- Requires only **lat/lon + ≥1 target** (and optionally date), or
- Uses **“if present”** logic (scientific_interactions, temporal_features) or takes whatever **feature_columns()** returns (numeric non-id, non-target).

The current CSV contains all columns that the pipeline and the optional feature steps use.

---

## 4. Optional columns that would improve the analysis

Documented in **docs/HYDROLOGY_FEATURES.md** and useful for scientific geospatial ML:

| Column | Role | In dataset? | Suggestion |
|--------|------|-------------|------------|
| **basin_id** | Drainage basin (or sub-basin) identifier | ❌ | Add as integer/categorical per site; supports structure and interpretation. |
| **upstream_area** | Catchment area (e.g. km²) | ❌ | Add from DEM/flow (e.g. HydroSHEDS); dilution and residence time. |
| **distance_to_river** | Distance to nearest channel (m) | ❌ | Add if GPS/snap uncertainty or off-channel sites matter. |
| **Land cover** | e.g. % urban/agriculture/water in buffer | ❌ | Would strengthen land-use interpretation; not in repo yet. |
| **Soil properties** | cec, clay, pH, phosphorous | ✅ | Already present. |
| **Hydrological** | flow_accumulation | ✅ | Present. basin_id, upstream_area, distance_to_river would complement. |
| **Climate** | pet, precipitation, total_evaporation_sum, total_precipitation_sum, temperatures | ✅ | Present. |

**Recommendation:** Add **basin_id**, **upstream_area**, and **distance_to_river** when available (e.g. from HydroSHEDS or similar) to improve interpretability and possibly performance. Land cover (e.g. from ESA WorldCover) is a next step for higher scientific quality.

---

## 5. Scripts / data sources not currently used by the pipeline

| Script / module | Purpose | Used by `run_pipeline.py`? |
|------------------|---------|-----------------------------|
| **scripts/prepare_sample_dataset.py** | Merge WQ + feature CSV → `data/raw/water_quality.csv` | No (run once manually to create CSV). |
| **scripts/run_full_workflow.py** | Optional merge + full pipeline | Can call merge via `--merge-dir`; then runs same pipeline. |
| **src/data/extract_landsat.py** | Sample Landsat rasters at (lon, lat) → band columns | No (config `pipeline.mode: tabular`; no raster extraction). |
| **src/data/extract_climate.py** | Sample climate rasters at (lon, lat) → e.g. precipitation, temperature | No (same as above). |
| **src/features/environmental_features.build_environmental_features** | Spectral indices + non-feature column drop | No (not imported in research_pipeline). |
| **src/features/spectral_indices.compute_spectral_indices** | Add NDVI, NDWI, MNDWI, NDBI, BSI from B2–B7 | No (tabular data already has indices; pipeline doesn’t call it). |

So: **extract_landsat**, **extract_climate**, **build_environmental_features**, and **compute_spectral_indices** are available for other workflows (e.g. raster-based or notebooks) but are **not** in the current `run_pipeline.py` path.

---

## 6. Final report summary

### Required columns (must exist)

| Column role | Accepted names | Status in dataset |
|-------------|----------------|-------------------|
| Latitude | `lat` or `Latitude` | ✅ lat, Latitude |
| Longitude | `lon` or `Longitude` | ✅ lon, Longitude |
| ≥ 1 target | `total_alkalinity`, `electrical_conductance`, `dissolved_reactive_phosphorus` (or alternate column names) | ✅ All three |
| ≥ 1 numeric predictor | Any numeric not in id/target list | ✅ Many (pet, elevation, NDVI, …) |

No required column is missing.

### Optional columns that would improve the models

- **basin_id** — basin or sub-basin identifier.
- **upstream_area** — catchment area (e.g. km²).
- **distance_to_river** — distance to nearest channel (m).
- **Land cover** — e.g. % classes in buffer (not yet in repo).

Soil, hydrology (flow_accumulation), and climate variables are already present and used.

### Scripts or data sources not used by the pipeline

- **extract_landsat.py** — raster → band columns (not called in tabular mode).
- **extract_climate.py** — raster → climate columns (not called in tabular mode).
- **environmental_features.build_environmental_features** — not called.
- **spectral_indices.compute_spectral_indices** — not called (data already has indices).
- **prepare_sample_dataset.py** — used only to build the CSV once; not part of `run_pipeline.py`.

### Recommendations for dataset quality

1. **Keep current CSV as-is for pipeline:** All required and currently used optional columns are present; no code change needed for existing runs.
2. **Add hydrology when possible:** **basin_id**, **upstream_area**, **distance_to_river** (see HYDROLOGY_FEATURES.md) for better process interpretation and potential gains.
3. **Document provenance:** Record how `water_quality_dataset_v1.csv` was built (e.g. merge of which WQ and feature-engineering outputs) and any spatial/temporal filters.
4. **Consider land cover:** Add land-cover features (e.g. from WorldCover) if the project aims for publication-level geospatial ML.
5. **Optional raster path:** If you later want to run from raw rasters, enable a mode that calls **extract_landsat** and **extract_climate** and optionally **compute_spectral_indices** so the same pipeline can be used with raster-derived inputs.

---

*Audit based on: `data/raw/water_quality_dataset_v1.csv` (41 columns), `src/pipelines/research_pipeline.py`, `src/features/*.py`, `src/data/load_data.py`, `src/validation/spatial_cv.py`, `src/visualization/maps.py`, `config/config.yaml`.*
