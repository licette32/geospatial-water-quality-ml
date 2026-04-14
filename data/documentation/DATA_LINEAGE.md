# Dataset lineage audit

**Objetivo:** Identificar qué archivos dentro de `proyectos-ey` contribuyeron al dataset final usado por este proyecto, antes de eliminar esa carpeta.

**Dataset final:** `data/raw/water_quality_dataset_v1.csv`

---

## 1. Resumen ejecutivo

El dataset final **water_quality_dataset_v1.csv** se obtuvo por **fusión (merge)** de dos archivos que existen **solo en proyecto 4**:

| Archivo directo | Ubicación en proyectos-ey | Contribución |
|-----------------|----------------------------|--------------|
| **water_quality_training_dataset.csv** | `proyecto 4/.../data/` (carpeta de datos del proyecto fuente) | Coordenadas, fecha, targets (TA, EC, DRP) |
| **feature_engineered_training_set.csv** | `proyecto 4/.../data/` (carpeta de datos del proyecto fuente) | Variables ambientales y de interacción |

`feature_engineered_training_set.csv` fue generado en el notebook **eda.ipynb** del proyecto 4, a partir de la unión de varios CSVs de características por fuente (Landsat, TerraClimate, ERA5, CHIRPS, MODIS, NASADEM, iSDA, HydroSHEDS) y del cálculo de interacciones en el EDA.

**Conclusión:** La carpeta **proyecto 4** es la única que contiene los dos insumos directos del dataset final. Los proyectos 1, 2 y 3 comparten el mismo `water_quality_training_dataset.csv` (o equivalente), pero **no** generan `feature_engineered_training_set.csv`; por tanto, el linaje del dataset final está íntegramente en **proyecto 4**.

---

## 2. Alcance de la búsqueda

- **Dataset final inspeccionado:** `data/raw/water_quality_dataset_v1.csv` (41 columnas, misma estructura que la salida del script `scripts/prepare_sample_dataset.py`).
- **Carpeta revisada:** `proyectos-ey` (en el repositorio bajo la raíz del proyecto). La misma estructura puede existir en `C:\Users\bever\Downloads\proyectos-ey`; el mapeo de archivos es equivalente.
- **Tipos de archivos buscados:** CSV, shapefiles (.shp), rasters (.tif). Solo se encontraron **CSV** relevantes para el dataset tabular final; no hay shapefiles ni rasters en `proyectos-ey` que se lean directamente para construir `water_quality_dataset_v1.csv`.

---

## 3. Estructura del dataset final

Columnas de `water_quality_dataset_v1.csv` (41 en total):

- **Identificación/geografía:** Latitude, Longitude, Sample Date  
- **Targets (nombres estándar):** Total Alkalinity, Electrical Conductance, Dissolved Reactive Phosphorus  
- **Variables ambientales:** pet, elevation, EVI, NDVI, Land Surface Temperature, nir, green, swir16, swir22, NDMI, MNDWI, cec, clay, pH, phosphorous, flow_accumulation, skin_temperature, soil_temperature, temperature_2m, total_evaporation_sum, total_precipitation_sum, volumetric_soil_water, precipitation  
- **Interacciones:** cec_pH_interaction, phosphorous_pH_interaction, NDVI_LST_interaction, flow_acc_clay_interaction, flow_acc_phosphorous_interaction, evaporation_precipitation_ratio, cec_clay_ratio  
- **Normalizaciones (añadidas en merge/carga):** lat, lon, total_alkalinity, electrical_conductance, dissolved_reactive_phosphorus  

---

## 4. Archivos en proyectos-ey que contribuyeron

### 4.1 Contribución directa (merge al dataset final)

| Archivo | Proyecto | Rol |
|---------|----------|-----|
| **water_quality_training_dataset.csv** | proyecto 4 | Filas por muestra; columnas: Latitude, Longitude, Sample Date, Total Alkalinity, Electrical Conductance, Dissolved Reactive Phosphorus. Mismo orden de filas que en feature_engineered. |
| **feature_engineered_training_set.csv** | proyecto 4 | Generado en `eda.ipynb`; contiene Unnamed: 0, targets (eliminados en merge), variables ambientales e interacciones. Se concatena por fila con water_quality. |

### 4.2 Insupos de feature_engineered_training_set.csv (proyecto 4)

En `proyecto 4/.../data/` (carpeta de datos del proyecto fuente) se encuentran los CSVs que el EDA une y transforma para producir `feature_engineered_training_set.csv`:

| Archivo de características | Columnas que aportan al dataset final |
|----------------------------|----------------------------------------|
| **landsat_features_training.csv** | nir, green, swir16, swir22, NDMI, MNDWI |
| **terraclimate_features_training.csv** | pet |
| **era5_features_training.csv** | skin_temperature, soil_temperature, temperature_2m, total_evaporation_sum, total_precipitation_sum, volumetric_soil_water (renombrados desde *_median) |
| **chirps_features_training.csv** | precipitation |
| **modisVI_features_training.csv** | EVI, NDVI (renombrados desde EVI_median, NDVI_median) |
| **modisLST_features_training.csv** | Land Surface Temperature |
| **nasadem_features_training.csv** | elevation |
| **iSDA_features_training.csv** | cec, clay, pH, phosphorous (agregados desde *_mean / *_median en el EDA) |
| **hydrosheds_features_training.csv** | flow_accumulation |

Las **interacciones** (cec_pH_interaction, phosphorous_pH_interaction, NDVI_LST_interaction, flow_acc_clay_interaction, flow_acc_phosphorous_interaction, evaporation_precipitation_ratio, cec_clay_ratio) se **calculan en el EDA** (eda.ipynb) a partir de estas variables; no provienen de un CSV externo adicional.

**No usados en el dataset final:**  
- `jrc_features_training.csv` (en proyecto 4): se usó en el EDA pero las variables *occurrence* y *seasonality* se descartaron para el conjunto final.  
- **training_set.csv** y **validation_set.csv** (proyecto 4): son salidas del mismo pipeline (train/val split), no insumos del merge que genera `water_quality_dataset_v1.csv`.

---

## 5. Tabla de linaje: columna final → dataset original → carpeta

| Columna en water_quality_dataset_v1.csv | Dataset original / origen | Carpeta en proyectos-ey |
|---------------------------------|---------------------------|--------------------------|
| Latitude | water_quality_training_dataset.csv | proyecto 4 |
| Longitude | water_quality_training_dataset.csv | proyecto 4 |
| Sample Date | water_quality_training_dataset.csv | proyecto 4 |
| Total Alkalinity | water_quality_training_dataset.csv | proyecto 4 |
| Electrical Conductance | water_quality_training_dataset.csv | proyecto 4 |
| Dissolved Reactive Phosphorus | water_quality_training_dataset.csv | proyecto 4 |
| pet | terraclimate_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| elevation | nasadem_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| EVI | modisVI_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| NDVI | modisVI_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| Land Surface Temperature | modisLST_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| nir | landsat_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| green | landsat_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| swir16 | landsat_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| swir22 | landsat_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| NDMI | landsat_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| MNDWI | landsat_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| cec | iSDA_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| clay | iSDA_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| pH | iSDA_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| phosphorous | iSDA_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| flow_accumulation | hydrosheds_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| skin_temperature | era5_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| soil_temperature | era5_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| temperature_2m | era5_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| total_evaporation_sum | era5_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| total_precipitation_sum | era5_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| volumetric_soil_water | era5_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| precipitation | chirps_features_training.csv → feature_engineered_training_set.csv | proyecto 4 |
| cec_pH_interaction | Calculado en eda.ipynb (cec, pH) | proyecto 4 |
| phosphorous_pH_interaction | Calculado en eda.ipynb (phosphorous, pH) | proyecto 4 |
| NDVI_LST_interaction | Calculado en eda.ipynb (NDVI, Land Surface Temperature) | proyecto 4 |
| flow_acc_clay_interaction | Calculado en eda.ipynb (flow_accumulation, clay) | proyecto 4 |
| flow_acc_phosphorous_interaction | Calculado en eda.ipynb (flow_accumulation, phosphorous) | proyecto 4 |
| evaporation_precipitation_ratio | Calculado en eda.ipynb (total_evaporation_sum, total_precipitation_sum) | proyecto 4 |
| cec_clay_ratio | Calculado en eda.ipynb (cec, clay) | proyecto 4 |
| lat | Derivado de Latitude en merge/load_data | proyecto 4 (vía water_quality) |
| lon | Derivado de Longitude en merge/load_data | proyecto 4 (vía water_quality) |
| total_alkalinity | Derivado de Total Alkalinity en merge/load_data | proyecto 4 (vía water_quality) |
| electrical_conductance | Derivado de Electrical Conductance en merge/load_data | proyecto 4 (vía water_quality) |
| dissolved_reactive_phosphorus | Derivado de Dissolved Reactive Phosphorus en merge/load_data | proyecto 4 (vía water_quality) |

---

## 6. Proyectos 1, 2 y 3

- **Proyecto 1:** Tiene `water_quality_training_dataset.csv` y CSVs de Landsat/TerraClimate con nombres similares; **no** tiene `feature_engineered_training_set.csv`. No es origen del dataset final.
- **Proyecto 2:** Tiene `water_quality_training_dataset.csv` y landsat/terraclimate features; **no** tiene `feature_engineered_training_set.csv`. No es origen del dataset final.
- **Proyecto 3:** Tiene `water_quality_training_dataset.csv`, landsat/terraclimate (y terraclimate_extended); **no** tiene `feature_engineered_training_set.csv`. No es origen del dataset final.

El `water_quality_training_dataset.csv` puede ser el mismo archivo base compartido en todos los proyectos; el dataset final depende de la **versión de proyecto 4** y de su `feature_engineered_training_set.csv`.

---

## 7. Recomendación antes de eliminar proyectos-ey

1. **Conservar una copia de proyecto 4** si se desea poder regenerar exactamente `feature_engineered_training_set.csv` o auditar las fórmulas de interacciones (p. ej. copiando solo la carpeta `proyecto 4 (carpeta del proyecto fuente)` en otro lugar o en un archivo comprimido).
2. **Dataset final ya disponible:** `data/raw/water_quality_dataset_v1.csv` es autosuficiente para el pipeline actual; no se leen archivos dentro de `proyectos-ey` en tiempo de ejecución.
3. **Reproducibilidad:** El script `scripts/prepare_sample_dataset.py` documenta el merge; para reproducir el dataset hace falta tener `water_quality_training_dataset.csv` y `feature_engineered_training_set.csv` (por ejemplo, los de proyecto 4) en la ruta indicada.
4. **Eliminación de proyectos-ey:** Tras esta auditoría, es seguro eliminar la carpeta `proyectos-ey` siempre que:
   - `data/raw/water_quality_dataset_v1.csv` esté guardado y versionado, y  
   - se acepte no poder regenerar `feature_engineered_training_set.csv` desde los CSVs de proyecto 4 a menos que se conserve una copia de ese proyecto (o de sus archivos de datos y del EDA).

---

*Documento generado como auditoría de linaje antes de eliminar la carpeta proyectos-ey.*
