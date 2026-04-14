# River Water Quality Prediction

> Geospatial machine learning pipeline for predicting in-river water quality from environmental covariates with spatial cross-validation.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## 🎯 What is this?

An end-to-end ML pipeline that predicts **three water quality parameters** in rivers:

| Target | Description | R² (Spatial CV) |
|--------|-------------|----------------|
| Total Alkalinity | Acid-neutralizing capacity | **0.31** |
| Electrical Conductance | Dissolved ions/salinity | **0.27** |
| Dissolved Reactive Phosphorus | Nutrient (eutrophication) | 0.00* |

*Phosphorus is harder to predict — requires field-specific data

---

## 🚀 Quick Start

```bash
# 1. Clone & enter
git clone https://github.com/licette32/geospatial-water-quality-ml.git
cd geospatial-water-quality-ml

# 2. Create environment
python -m venv .venv
source .venv/Scripts/activate  # Linux: source .venv/bin/activate
pip install -r requirements.txt

# 3. Run pipeline
python scripts/run_full_workflow.py
```

---

## 📊 The Problem

River water quality depends on **catchment processes**:
- Dilution & evaporation
- Weathering & soil chemistry
- Land cover & flow routing

Nearby samples share similar landscapes → **random train/test splits inflate performance**. This pipeline uses **spatial cross-validation** for honest metrics.

---

## 🔧 Pipeline Architecture

```
┌─────────────────┐
│  1. Load Data  │  (lat/lon + targets + predictors)
└────────┬────────┘
         ▼
┌─────────────────────┐
│ 2. Feature Eng.  │  (temporal, scientific interactions)
└────────┬────────────┘
         ▼
┌──────────────────────┐
│ 3. Spatial Clusters │  (KMeans on coordinates)
└────────┬───────────────┘
         ▼
┌───────────────────────────┐
│ 4. Spatial GroupKFold │  (blocks to prevent leakage)
└────────┬───────────────┘
         ▼
┌─────────────────────┐
│ 5. Stacking Ens.  │  (LightGBM + XGBoost + CatBoost)
└────────┬────────────┘
         ▼
┌─────────────────┐
│ 6. SHAP Explainer │  (feature importance)
└────────┬────────┘
         ▼
┌─────────────────────┐
│ 7. Save Artifacts │  (models, metrics, figures)
└─────────────────┘
```

---

## 📁 Project Structure

```
├── data/
│   └── raw/water_quality_dataset_v1.csv   # 9,319 samples, 41 features
├── src/
│   ├── data/                            # Data loading
│   ├── features/                     # Feature engineering
│   ├── models/                      # Training & stacking
│   ├── pipelines/                   # Orchestration
│   ├── validation/                 # Spatial CV
│   └── visualization/              # Maps & plots
├── notebooks/                      # 10 Jupyter notebooks
├── config/config.yaml              # Configuration
��── run_pipeline.py                # Entry point
```

---

## 🔬 Features Used

| Category | Variables |
|----------|----------|
| **Satellite** | NDVI, EVI, NDMI, MNDWI, LST, NIR, Green, SWIR |
| **Climate** | Precipitation, evaporation, temperature, soil moisture |
| **Soil** | CEC, clay, pH, phosphorus |
| **Hydrology** | Flow accumulation |
| **Interactions** | ET/precip ratio, soil pH, flow × soil |

---

## 📓 Notebooks

| # | Title | Description |
|---|-------|------------|
| 01 | Data Exploration | Load & examine data |
| 02 | Feature Engineering | Create derived features |
| 03 | Spatial Validation | Spatial autocorrelation & CV |
| 04 | Model Training | Stacking ensemble |
| 05 | Explainability | SHAP importance |
| 06 | Diagnostics | Model metrics |
| 07 | Prediction Maps | Spatial interpolation |
| 08 | Stability Analysis | Robustness checks |
| 09 | Feature Sensitivity | Feature ablation |
| 10 | Uncertainty | Confidence intervals |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **ML:** LightGBM, XGBoost, CatBoost
- **Spatial:** Scikit-learn, GeoPandas
- **Visualization:** Matplotlib, SHAP
- **Data:** Pandas, NumPy

---

## 📝 Citation

If you use this code, cite:

```bibtex
@software{geospatial-water-quality-ml,
  author = {Your Name},
  title = {River Water Quality — Geospatial ML Pipeline},
  url = {https://github.com/licette32/geospatial-water-quality-ml},
  year = {2026}
}
```

---

## 📄 License

MIT License — free to use and modify.

---

## 🤝 Contributing

Issues and pull requests welcome!