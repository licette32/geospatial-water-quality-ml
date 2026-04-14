# Dataset description

**File:** `data/raw/water_quality_dataset_v1.csv`  
**Purpose:** Training data for geospatial prediction of in-river water quality from environmental covariates.

---

## 1. Dataset overview

The dataset contains **in-situ water quality measurements** at sample locations (lat/lon) with **environmental predictors** extracted or aggregated for the same location (and, where applicable, sample date). It is used to train models that predict three water chemistry targets from satellite-derived indices, climate reanalysis, soil properties, topography, and hydrology. The pipeline uses this table for feature engineering, spatial cross-validation, and stacking ensemble training.

---

## 2. Dimensions

| Metric   | Value |
|----------|--------|
| **Rows** | 9,319 |
| **Columns** | 41 |

Each row corresponds to one sampling event (location and date). Columns include identifiers, three target variables, and numeric predictors from multiple environmental sources.

---

## 3. Target variables

Variables to be predicted by the model (in-river water quality):

| Column | Description |
|--------|-------------|
| **Total Alkalinity** | Acid-neutralizing capacity of the water (e.g. mg/L as CaCO₃). Also available as `total_alkalinity` (normalized name). |
| **Electrical Conductance** | Ability of water to conduct current; proxy for dissolved ions/salinity (e.g. µS/cm). Also `electrical_conductance`. |
| **Dissolved Reactive Phosphorus** | Inorganic phosphorus in solution; nutrient relevant for eutrophication (e.g. µg/L). Also `dissolved_reactive_phosphorus`. |

The pipeline uses the snake_case names (`total_alkalinity`, `electrical_conductance`, `dissolved_reactive_phosphorus`) when present; these may be added from the display names during load.

---

## 4. Feature categories

Predictors are grouped by source and domain.

### 4.1 Satellite-derived indices

Vegetation, moisture, and surface temperature from optical/thermal satellite data (e.g. Landsat, MODIS).

| Variable | Description |
|----------|-------------|
| **NDVI** | Normalized Difference Vegetation Index; greenness / vegetation vigor. |
| **EVI** | Enhanced Vegetation Index; vegetation signal with atmospheric correction. |
| **NDMI** | Normalized Difference Moisture Index; canopy/soil moisture. |
| **MNDWI** | Modified Normalized Difference Water Index; open water / wetness. |
| **nir** | Near-infrared reflectance (Landsat). |
| **green** | Green band reflectance (Landsat). |
| **swir16** | Short-wave infrared 1.6 µm (Landsat). |
| **swir22** | Short-wave infrared 2.2 µm (Landsat). |
| **Land Surface Temperature** | Land surface temperature from thermal infrared (e.g. MODIS LST). |

### 4.2 Climate variables

Precipitation, evaporation, and near-surface/soil temperatures from reanalysis and precipitation products.

| Variable | Description |
|----------|-------------|
| **precipitation** | Precipitation at or near the sample (e.g. CHIRPS). |
| **total_precipitation_sum** | Cumulative precipitation (e.g. ERA5). |
| **total_evaporation_sum** | Cumulative evaporation (e.g. ERA5). |
| **evaporation_precipitation_ratio** | Derived: evaporation / precipitation; aridity proxy. |
| **temperature_2m** | Air temperature at 2 m (e.g. ERA5). |
| **skin_temperature** | Surface skin temperature (e.g. ERA5). |
| **soil_temperature** | Soil temperature in top layer (e.g. ERA5). |
| **volumetric_soil_water** | Volumetric soil moisture in top layer (e.g. ERA5). |
| **pet** | Potential evapotranspiration (e.g. TerraClimate). |

### 4.3 Soil variables

Soil properties at the sample location (e.g. from iSDA or similar).

| Variable | Description |
|----------|-------------|
| **cec** | Cation exchange capacity. |
| **clay** | Clay content (e.g. % or fraction). |
| **pH** | Soil pH. |
| **phosphorous** | Soil phosphorus content (note: spelling as in dataset). |
| **cec_pH_interaction** | Derived: cec × pH. |
| **phosphorous_pH_interaction** | Derived: phosphorous × pH. |
| **cec_clay_ratio** | Derived: cec / clay. |

### 4.4 Hydrological variables

Catchment and flow-related attributes.

| Variable | Description |
|----------|-------------|
| **flow_accumulation** | Upstream accumulated flow (e.g. HydroSHEDS); proxy for drainage size. |
| **flow_acc_clay_interaction** | Derived: flow_accumulation × clay. |
| **flow_acc_phosphorous_interaction** | Derived: flow_accumulation × phosphorous. |

### 4.5 Topography

Elevation and related derivatives.

| Variable | Description |
|----------|-------------|
| **elevation** | Surface elevation at sample location (e.g. NASADEM), meters. |

### 4.6 Other: identifiers and derived

| Variable | Description |
|----------|-------------|
| **Latitude** | Sample latitude (WGS84). |
| **Longitude** | Sample longitude (WGS84). |
| **lat** | Same as Latitude (normalized name, may be added on load). |
| **lon** | Same as Longitude (normalized name). |
| **Sample Date** | Date of the sampling event. |
| **NDVI_LST_interaction** | Derived: NDVI × Land Surface Temperature. |

---

## 5. Full column list with descriptions

| # | Column | Category | Description |
|---|--------|----------|-------------|
| 1 | Latitude | Identifier | Sample latitude (WGS84). |
| 2 | Longitude | Identifier | Sample longitude (WGS84). |
| 3 | Sample Date | Identifier | Date of the in-situ sample. |
| 4 | Total Alkalinity | Target | In-river alkalinity (e.g. mg/L as CaCO₃). |
| 5 | Electrical Conductance | Target | In-river conductivity (e.g. µS/cm). |
| 6 | Dissolved Reactive Phosphorus | Target | Dissolved reactive P (e.g. µg/L). |
| 7 | pet | Climate | Potential evapotranspiration. |
| 8 | elevation | Topography | Surface elevation (m). |
| 9 | EVI | Satellite | Enhanced Vegetation Index. |
| 10 | NDVI | Satellite | Normalized Difference Vegetation Index. |
| 11 | Land Surface Temperature | Satellite | Land surface temperature from thermal IR. |
| 12 | nir | Satellite | Near-infrared reflectance. |
| 13 | green | Satellite | Green band reflectance. |
| 14 | swir16 | Satellite | SWIR 1.6 µm reflectance. |
| 15 | swir22 | Satellite | SWIR 2.2 µm reflectance. |
| 16 | NDMI | Satellite | Normalized Difference Moisture Index. |
| 17 | MNDWI | Satellite | Modified ND Water Index. |
| 18 | cec | Soil | Cation exchange capacity. |
| 19 | clay | Soil | Clay content. |
| 20 | pH | Soil | Soil pH. |
| 21 | phosphorous | Soil | Soil phosphorus (spelling as in data). |
| 22 | flow_accumulation | Hydrological | Upstream flow accumulation. |
| 23 | skin_temperature | Climate | Surface skin temperature. |
| 24 | soil_temperature | Climate | Soil temperature (top layer). |
| 25 | temperature_2m | Climate | Air temperature at 2 m. |
| 26 | total_evaporation_sum | Climate | Cumulative evaporation. |
| 27 | total_precipitation_sum | Climate | Cumulative precipitation (reanalysis). |
| 28 | volumetric_soil_water | Climate | Volumetric soil moisture. |
| 29 | precipitation | Climate | Precipitation (e.g. CHIRPS). |
| 30 | cec_pH_interaction | Soil (derived) | cec × pH. |
| 31 | phosphorous_pH_interaction | Soil (derived) | phosphorous × pH. |
| 32 | NDVI_LST_interaction | Satellite (derived) | NDVI × Land Surface Temperature. |
| 33 | flow_acc_clay_interaction | Hydrological (derived) | flow_accumulation × clay. |
| 34 | flow_acc_phosphorous_interaction | Hydrological (derived) | flow_accumulation × phosphorous. |
| 35 | evaporation_precipitation_ratio | Climate (derived) | Evaporation / precipitation. |
| 36 | cec_clay_ratio | Soil (derived) | cec / clay. |
| 37 | lat | Identifier | Latitude (normalized). |
| 38 | lon | Identifier | Longitude (normalized). |
| 39 | total_alkalinity | Target | Alkalinity (normalized name). |
| 40 | electrical_conductance | Target | Conductance (normalized name). |
| 41 | dissolved_reactive_phosphorus | Target | Dissolved reactive P (normalized name). |

---

## 6. Notes

- **Units** are not standardized in this document; refer to the original data sources (TerraClimate, ERA5, CHIRPS, Landsat, MODIS, NASADEM, iSDA, HydroSHEDS) for exact units and temporal aggregation.
- **Missing values** may occur; the pipeline applies median imputation to numeric predictors before training.
- **Spatial and temporal alignment**: Predictors were extracted or aggregated for the sample location (and, where applicable, sample date). See `DATA_LINEAGE.md` for upstream sources and merge logic.

---

## 7. Geographic coverage

The dataset contains sampling locations in **sub-Saharan Africa**.

Coordinates are expressed in **WGS84** geographic coordinates.

The samples represent **river and freshwater environments** used for environmental monitoring and water quality analysis.

---

## 8. Temporal coverage

Sampling events **span multiple years**.

Temporal predictors (climate variables) correspond to the **period surrounding the sampling date**.

Exact temporal aggregation depends on the **original environmental dataset**.

---

## 9. Environmental data sources

Environmental predictors originate from **publicly available datasets**:

**Satellite data:**
- Landsat surface reflectance
- MODIS vegetation indices
- MODIS land surface temperature

**Climate reanalysis:**
- ERA5 atmospheric reanalysis

**Precipitation datasets:**
- CHIRPS rainfall product

**Climate products:**
- TerraClimate evapotranspiration

**Topography:**
- NASADEM digital elevation model

**Soil properties:**
- iSDA soil database

**Hydrology:**
- HydroSHEDS flow accumulation dataset

---

## 10. Intended use

This dataset is intended for:

- geospatial machine learning
- environmental modeling
- hydrological analysis
- water quality prediction

It is **not** intended for regulatory decision making.
