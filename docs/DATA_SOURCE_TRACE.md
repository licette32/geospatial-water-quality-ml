# Trace: dónde se carga el dataset del pipeline

Rastreo de **todas** las cargas de CSV y de la ruta final usada por `python run_pipeline.py`.

---

## 1. Lugares donde se cargan CSV

| Archivo | Línea (aprox.) | Qué hace |
|---------|----------------|----------|
| **src/data/load_data.py** | 29 | `pd.read_csv(path)` — recibe un `path` ya resuelto; **no** construye la ruta. |
| **src/pipelines/research_pipeline.py** | 174, 182 | Construye `raw` con `_resolve_data_path()` y llama `stage_load_data(raw)` → `load_water_quality_data(raw)` → `pd.read_csv(raw)`. |
| **scripts/prepare_sample_dataset.py** | 18–19 | `pd.read_csv(wq_path)` y `pd.read_csv(fe_path)` — solo si ejecutas este script; rutas son argumento o `data/raw/`. |
| **scripts/run_full_workflow.py** | 39 | Si usas `--merge-dir`, llama a `prepare_sample_dataset.merge()`; escribe en `data/raw/water_quality.csv`. No lee CSV de datos dentro de este script. |

El único flujo que usa **run_pipeline.py** es: **research_pipeline** → **load_water_quality_data(path)** → **pd.read_csv(path)**.

---

## 2. Cómo se construye la ruta en el pipeline

Cuando ejecutas **`python run_pipeline.py`**:

1. **run_pipeline.py** (línea 13):  
   `run_all(ROOT / "config" / "config.yaml")`  
   → `ROOT` = directorio **raíz del proyecto** (donde está `run_pipeline.py`).

2. **research_pipeline.run_all()** llama a **run_full_pipeline(config_path)**.

3. **run_full_pipeline()** (líneas 171–174):
   - `root = Path(config_path).resolve().parent.parent`  
     → **root = raíz del proyecto** (carpeta raíz del repo).
   - `raw_dir = cfg["paths"]["raw_data"]`  
     → **"data/raw"** (config.yaml).
   - `raw = _resolve_data_path(root, raw_dir, cfg["data"]["water_quality_csv"])`  
     → **csv_name = "water_quality_dataset_v1.csv"** (config.yaml).

4. **_resolve_data_path(root, "data/raw", "water_quality_dataset_v1.csv")** (líneas 157–167):
   - `raw_dir_path = root / raw_dir`  
     → **raíz del proyecto/data/raw**
   - `candidates = [csv_name, "water_quality_dataset_v1.csv", "water_quality.csv"]`  
     → **["water_quality_dataset_v1.csv", "water_quality_dataset_v1.csv", "water_quality.csv"]**
   - Recorre `raw_dir_path / name` y devuelve el **primer archivo que exista**.

---

## 3. Rutas exactas que intenta el pipeline

Todas relativas a la raíz del repo **raíz del proyecto**:

| Orden | Ruta absoluta (ejemplo) | Ruta relativa |
|-------|--------------------------|---------------|
| 1 | `C:\Users\bever\Desktop\raíz del proyecto\data\raw\water_quality_dataset_v1.csv` | **data/raw/water_quality_dataset_v1.csv** |
| 2 | (mismo nombre, repetido en candidates) | data/raw/water_quality_dataset_v1.csv |
| 3 | `...\raíz del proyecto\data\raw\water_quality.csv` | **data/raw/water_quality.csv** |

El pipeline **solo** mira dentro de **data/raw/** del propio repo.

---

## 4. Resumen: qué dataset usa `python run_pipeline.py`

| Pregunta | Respuesta |
|----------|-----------|
| ¿De qué carpeta lee? | **data/raw/** (del repo raíz del proyecto). |
| ¿Nombre del archivo? | El primero que exista de: **water_quality_dataset_v1.csv**, **water_quality.csv**. |
| ¿Ruta típica en tu máquina? | `C:\Users\bever\Desktop\raíz del proyecto\data\raw\water_quality_dataset_v1.csv` (si existe). |

---

## 5. Fuente de datos

El dataset proviene de un merge de dos archivos originales:
- `water_quality_training_dataset.csv` (calidad del agua)
- `feature_engineered_training_set.csv` (features ambientales)

El script `scripts/prepare_sample_dataset.py` realiza este merge.

---

## 6. Resumen final

| Concepto | Detalle |
|----------|--------|
| **Archivos que cargan CSV en el pipeline** | `src/data/load_data.py` (read_csv); la ruta la construye `src/pipelines/research_pipeline.py`. |
| **Rutas de datos** | **data/raw/water_quality_dataset_v1.csv** y/o **data/raw/water_quality.csv** (relativas a la raíz raíz del proyecto). |
| **Config** | `config/config.yaml` → `paths.raw_data: data/raw`, `data.water_quality_csv: water_quality_dataset_v1.csv`. |
