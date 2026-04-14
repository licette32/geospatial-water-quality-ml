# Auditoría de notebooks

Este documento resume la evaluación de los notebooks en `notebooks/` respecto a su propósito, datos utilizados, dependencias de retos/challenges y solapamiento con el pipeline en `src/`.

---

## 1. Listado de notebooks

| Notebook | Descripción breve |
|----------|-------------------|
| `01_data_exploration.ipynb` | Exploración de datos, estructura del dataset, mapas y distribuciones de targets |
| `02_feature_engineering.ipynb` | Índices espectrales e interacciones científicas |
| `03_spatial_validation.ipynb` | Clustering espacial y GroupKFold para validación espacial |
| `04_model_training.ipynb` | Entrenamiento con LightGBM/XGBoost/CatBoost, RegressorChain y stacking |
| `05_model_explainability.ipynb` | Explicabilidad con SHAP (resumen global y dependencia) |

---

## 2. Evaluación por notebook

### 01_data_exploration.ipynb

| Criterio | Detalle |
|----------|--------|
| **Propósito** | Enseñar la estructura de datos de calidad de agua para ML geoespacial: coordenadas, targets y predictores ambientales. Revisar valores faltantes, outliers y cobertura espacial. Explicar por qué se usa validación cruzada espacial. |
| **Datasets que carga** | `data/raw/water_quality_dataset_v1.csv` o `data/raw/water_quality.csv` (resolución por existencia en `data/raw`). |
| **Dependencia de datos “challenge”** | **No.** Usa nombres neutros; no referencia EY ni retos concretos. |
| **Duplicación con pipeline** | **No.** El pipeline no hace EDA ni visualizaciones exploratorias; el notebook es material didáctico complementario. |

---

### 02_feature_engineering.ipynb

| Criterio | Detalle |
|----------|--------|
| **Propósito** | Construir índices espectrales (cuando hay bandas tipo Landsat) e interacciones científicas (ET/precipitación, precipitación×runoff, etc.) con interpretación física. |
| **Datasets que carga** | Mismo CSV: `water_quality_dataset_v1.csv` o `water_quality.csv`. |
| **Dependencia de datos “challenge”** | **No.** Sin referencias a retos ni datos propietarios de challenge. |
| **Duplicación con pipeline** | **Parcial.** El pipeline aplica `add_temporal_features` y `add_scientific_interactions` en `stage_feature_engineering`; el notebook muestra el mismo tipo de lógica (módulos `src.features`) de forma paso a paso para aprendizaje. No reimplementa la lógica, solo la invoca y explica. |

---

### 03_spatial_validation.ipynb

| Criterio | Detalle |
|----------|--------|
| **Propósito** | Explicar clustering espacial (lat/lon) y GroupKFold para que folds enteros (clusters) queden en train o test, evitando fugas espaciales. Justificar validación espacial para generalización a nuevas ubicaciones. |
| **Datasets que carga** | Mismo CSV: `water_quality_dataset_v1.csv` o `water_quality.csv`. |
| **Dependencia de datos “challenge”** | **No.** Sin referencias a retos. |
| **Duplicación con pipeline** | **Parcial.** El pipeline usa `spatial_cluster_groups` y `SpatialGroupKFold` en `stage_spatial_clustering` y `stage_spatial_cv_stacking`; el notebook usa los mismos módulos (`src.validation.spatial_cv`, `src.visualization.maps`) para ilustrar el concepto y mostrar un bucle de folds. Es complemento didáctico, no código duplicado. |

---

### 04_model_training.ipynb

| Criterio | Detalle |
|----------|--------|
| **Propósito** | Entrenar LightGBM, XGBoost y CatBoost con GroupKFold espacial; opcionalmente RegressorChain (multi-target) y stacking (ensemble). Explicar ventajas del ensemble (diversidad, robustez, meta-learner). |
| **Datasets que carga** | Mismo CSV: `water_quality_dataset_v1.csv` o `water_quality.csv`. |
| **Dependencia de datos “challenge”** | **No.** Sin referencias a retos. |
| **Duplicación con pipeline** | **Sí, conceptual.** El pipeline ejecuta el flujo completo en `stage_spatial_cv_stacking` (GroupKFold + `fit_stacking_per_target`). El notebook desglosa el mismo flujo (carga → features → spatial CV → stacking) para enseñanza; usa los mismos componentes de `src` (p. ej. `multi_target`). No hay lógica duplicada en el notebook, solo orquestación explícita paso a paso. |

---

### 05_model_explainability.ipynb

| Criterio | Detalle |
|----------|--------|
| **Propósito** | Usar SHAP en modelos tipo árbol: importancia global (mean \|SHAP\|) y dependencia de variables climáticas. Explicar interpretación para gestores del agua. |
| **Datasets que carga** | Mismo CSV: `water_quality_dataset_v1.csv` o `water_quality.csv`. |
| **Dependencia de datos “challenge”** | **No.** Sin referencias a retos. |
| **Duplicación con pipeline** | **Parcial.** El pipeline tiene una etapa SHAP (`stage_shap` / explainability); el notebook llama a `shap_summary_bar` y `shap_dependence_climate` de `src.models.explainability` para mostrar resultados. Misma funcionalidad expuesta de forma didáctica. |

---

## 3. Clasificación

| Clasificación | Notebooks | Criterio |
|---------------|-----------|----------|
| **A) Útiles y reutilizables** | `01_data_exploration.ipynb`, `02_feature_engineering.ipynb`, `03_spatial_validation.ipynb`, `04_model_training.ipynb`, `05_model_explainability.ipynb` | Material didáctico alineado con el pipeline; usan datos genéricos (`water_quality_dataset_v1.csv` / `water_quality.csv`); sin dependencias de challenge; reutilizan módulos de `src` sin duplicar lógica. |
| **B) Parcialmente útiles** | — | Ninguno clasificado aquí; los cinco son considerados útiles y reutilizables en su conjunto. |
| **C) Obsoletos o específicos de challenge** | — | Ninguno. No se encontraron notebooks que dependan de datos o terminología de un reto concreto ni que estén obsoletos. |

---

## 4. Resumen

- **Total de notebooks revisados:** 5  
- **Datasets utilizados:** `data/raw/water_quality_dataset_v1.csv` o `data/raw/water_quality.csv` (alternativa en el mismo directorio).  
- **Dependencias de challenge:** Ninguna; todos usan nombres y rutas neutros.  
- **Relación con el pipeline:** Los notebooks **no duplican** la implementación del pipeline; la **ilustran** usando los mismos módulos de `src` (features, validation, models, explainability). Son material educativo que acompaña a `research_pipeline` y `run_full_workflow`.  

**Recomendación:** Mantener los cinco notebooks en `notebooks/`. La carpeta `notebooks/archive/` se ha creado para futuros notebooks que se clasifiquen como obsoletos o específicos de un challenge; en esta auditoría no se ha movido ningún archivo.

---

## 5. Ubicación del archivo

- **Informe:** `docs/NOTEBOOK_AUDIT.md`  
- **Carpeta de archivo:** `notebooks/archive/` (vacía; lista para uso futuro).

---

## 6. Notebook workflow

The notebooks follow a logical progression aligned with the research workflow:

1. Data exploration  
2. Feature engineering  
3. Spatial validation  
4. Model training  
5. Model explainability  

This structure mirrors a typical environmental machine learning workflow, from understanding the dataset to training and interpreting predictive models.

**Flujo de los notebooks:**

```
Dataset
   ↓
01_data_exploration
   ↓
02_feature_engineering
   ↓
03_spatial_validation
   ↓
04_model_training
   ↓
05_model_explainability
```
