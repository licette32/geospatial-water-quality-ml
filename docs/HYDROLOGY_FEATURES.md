# Hydrological predictors and river chemistry

Optional columns (attach at each sample site) improve models because **water chemistry reflects catchment routing and mixing**.

## `basin_id`

- **Meaning:** Discrete identifier of the drainage basin (or sub-basin) containing the sample.
- **Why it helps:** Basins integrate **lithology, land use, and flow paths**. Samples in the same basin share upstream controls; encoding basin captures **unobserved spatial structure** not fully represented by climate grids alone.
- **Use:** Integer or categorical. Tree models split on basin; in spatial CV, avoid using basin alone as a perfect proxy for location if leakage is a concern — prefer holding out **spatial clusters** that may span basins.

## `upstream_area` (catchment area, km²)

- **Meaning:** Contributing area above the sample point (or pour-point proxy).
- **Why it helps:** **Dilution capacity** scales with discharge; large basins often dilute point sources. **Residence time** and **weathering rates** increase with area. Strong predictors for **conductivity, alkalinity, and nutrient loads** where point vs diffuse sources differ.
- **Typical source:** DEM + flow accumulation (e.g. HydroSHEDS, MERIT).

## `distance_to_river` (m)

- **Meaning:** Distance from sampling coordinates to the nearest river channel (or snap distance if samples are bank/shore).
- **Why it helps:** Near-channel samples integrate **mainstem chemistry**; farther points may reflect **tributaries, wetlands, or bank storage**. Useful when GPS precision varies or when predicting from **non-point** extractions (e.g. pixel center vs actual channel).

## Integration in this repository

Provide these columns in **`data/raw/water_quality_dataset_v1.csv (or water_quality.csv)`** alongside other predictors. The pipeline treats numeric columns as features. For **`basin_id`**, use integer codes so they pass the numeric feature filter, or extend preprocessing with one-hot encoding if needed.

See **README** (Scientific motivation) and **LEARNING_GUIDE** for context.
