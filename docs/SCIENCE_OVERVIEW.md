# Science overview

**Goal:** Predict river water quality at sample sites using environmental predictors aligned in space (and time when applicable).

**Design principles**

1. **Spatial dependence** — Samples are not independent; validation uses **spatial clusters + GroupKFold**.
2. **Open data** — Landsat, reanalysis (ERA5), gridded climate (TerraClimate), hydrology layers; user supplies extractions at coordinates.
3. **Interpretability** — SHAP links predictions to drivers; interaction features encode hydrologic/geochemical hypotheses.
4. **Ensembles** — Stacking over LightGBM, XGBoost, CatBoost reduces variance and combines complementary fits.

**Workflow:** Data exploration → feature engineering → spatial CV → training → SHAP → maps.

Full teaching path: **LEARNING_GUIDE.md** and **notebooks/01–05**.
