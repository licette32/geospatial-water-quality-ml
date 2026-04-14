"""
Hydrology- and geochemistry-inspired interaction features.

Physical interpretations documented in docstrings and LEARNING_GUIDE.md.
"""

import numpy as np
import pandas as pd
from typing import Optional

EPS = 1e-8


def add_scientific_interactions(df: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
    """
    Adds (when source columns exist):

    - et_precip_ratio: AET or PET divided by precipitation → aridity / concentration proxy
    - precip_runoff_proxy: precipitation * runoff_proxy (q or flow_accumulation scaled)
    - soil_moisture_ndmi: volumetric soil water * NDMI → land–atmosphere moisture coupling
    - cond_alk_ratio: conductance / alkalinity → ionic strength per buffering unit (dimensionless mix)
    """
    out = df if inplace else df.copy()

    # Evapotranspiration / precipitation — higher ratio → less dilution, more evap concentration
    et_cols = ["aet", "pet", "total_evaporation_sum"]
    p_cols = ["precipitation", "total_precipitation_sum", "ppt"]
    et = next((out[c] for c in et_cols if c in out.columns), None)
    pr = next((out[c] for c in p_cols if c in out.columns), None)
    if et is not None and pr is not None:
        out["et_precip_ratio"] = et.astype(float) / (pr.astype(float).abs() + EPS)

    # Precipitation * runoff — wet loading + transport capacity
    runoff = None
    for c in ("q", "flow_accumulation", "runoff"):
        if c in out.columns:
            runoff = out[c]
            break
    if pr is not None and runoff is not None:
        out["precip_runoff_proxy"] = pr.astype(float) * runoff.astype(float)

    # Soil moisture * NDMI — moisture status of land surface vs vegetation water stress
    sm = None
    for c in ("volumetric_soil_water", "soil", "soil_moisture"):
        if c in out.columns:
            sm = out[c]
            break
    if sm is not None and "NDMI" in out.columns:
        out["soil_moisture_ndmi"] = sm.astype(float) * out["NDMI"].astype(float)

    # Conductivity / alkalinity — salinity vs acid-neutralizing capacity (interpret with care)
    cond = None
    for c in ("electrical_conductance", "conductivity", "EC"):
        if c in out.columns:
            cond = out[c]
            break
    alk = None
    for c in ("total_alkalinity", "Total Alkalinity", "alkalinity"):
        if c in out.columns:
            alk = out[c]
            break
    if cond is not None and alk is not None:
        out["cond_alk_ratio"] = cond.astype(float) / (alk.astype(float).abs() + EPS)

    return out
