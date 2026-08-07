"""
JalRakshak ML handoff module for Person B.

Usage:
    from ml.predict import predict, cluster_score

    result = predict({
        "soil_infiltration_rate_mm_hr": 25.0,
        "depth_to_water_table_m": 8.0,
        "open_space_sqm": 45.0,
        "roof_area_sqm": 120.0,
        "annual_rainfall_mm": 1400.0,
        "slope_percent": 2.0,
        "runoff_coefficient": 0.85,  # optional
    })

    score = cluster_score({
        "avg_rainfall_mm": 1400,
        "avg_groundwater_depth_m": 7.0,
        "built_up_density": 0.75,
    })
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"

FEATURE_COLUMNS = [
    "soil_infiltration_rate_mm_hr",
    "depth_to_water_table_m",
    "open_space_sqm",
    "roof_area_sqm",
    "annual_rainfall_mm",
    "slope_percent",
]

WARD_FEATURE_COLUMNS = [
    "avg_rainfall_mm",
    "avg_groundwater_depth_m",
    "built_up_density",
]

_structure_clf = None
_rainfall_artifact: dict[str, Any] | None = None
_ward_kmeans = None
_ward_scaler = None
_ward_cluster_map: dict[int, float] | None = None


def _load_artifacts() -> None:
    global _structure_clf, _rainfall_artifact, _ward_kmeans, _ward_scaler, _ward_cluster_map

    if _structure_clf is None:
        _structure_clf = joblib.load(MODELS_DIR / "structure_classifier.joblib")

    if _rainfall_artifact is None:
        with open(MODELS_DIR / "rainfall_volume.json", encoding="utf-8") as f:
            _rainfall_artifact = json.load(f)

    if _ward_kmeans is None:
        _ward_kmeans = joblib.load(MODELS_DIR / "ward_kmeans.joblib")
        _ward_scaler = joblib.load(MODELS_DIR / "ward_scaler.joblib")
        with open(MODELS_DIR / "ward_clustering.json", encoding="utf-8") as f:
            ward_data = json.load(f)
            _ward_cluster_map = {int(k): float(v) for k, v in ward_data["cluster_score_map"].items()}


def _structure_dimensions(structure_type: str, features: dict[str, float]) -> dict[str, float]:
    """CGWB rule-of-thumb dimensions scaled to site features."""
    space = features["open_space_sqm"]
    roof = features["roof_area_sqm"]
    wt = features["depth_to_water_table_m"]

    if structure_type == "recharge_pit":
        depth = float(np.clip(3.0 - wt * 0.1, 1.0, 3.0))
        diameter = float(np.clip(1.0 + roof / 300, 1.0, 2.0))
        return {"depth_m": round(depth, 2), "diameter_m": round(diameter, 2)}

    if structure_type == "recharge_trench":
        length = float(np.clip(space * 0.4, 10.0, 30.0))
        width = 1.2
        depth = float(np.clip(2.0 - wt * 0.03, 1.5, 2.0))
        return {"length_m": round(length, 2), "width_m": width, "depth_m": round(depth, 2)}

    if structure_type == "recharge_shaft":
        depth = float(np.clip(wt * 0.6, 5.0, 10.0))
        diameter = 0.75
        return {"depth_m": round(depth, 2), "diameter_m": diameter}

    # percolation_tank
    side = float(np.clip(np.sqrt(space * 0.35), 5.0, 15.0))
    depth = 2.5
    return {"length_m": round(side, 2), "width_m": round(side, 2), "depth_m": depth}


def _volume_quantiles(roof_area_sqm: float, runoff_coefficient: float) -> tuple[float, float, float]:
    annual_totals = np.array(_rainfall_artifact["annual_totals_mm"], dtype=float)
    volumes = roof_area_sqm * annual_totals * runoff_coefficient
    return (
        float(np.percentile(volumes, 10)),
        float(np.percentile(volumes, 50)),
        float(np.percentile(volumes, 90)),
    )


def predict(features: dict) -> dict:
    """
    Classify recharge structure and estimate harvestable volume range.

    Required keys: soil_infiltration_rate_mm_hr, depth_to_water_table_m,
    open_space_sqm, roof_area_sqm, annual_rainfall_mm, slope_percent.
    Optional: runoff_coefficient (default 0.85).
    """
    _load_artifacts()

    missing = [k for k in FEATURE_COLUMNS if k not in features]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    runoff = float(features.get("runoff_coefficient", _rainfall_artifact["default_runoff_coefficient"]))
    X = np.array([[float(features[k]) for k in FEATURE_COLUMNS]], dtype=float)

    structure_type = str(_structure_clf.predict(X)[0])
    proba = _structure_clf.predict_proba(X)[0]
    class_idx = list(_structure_clf.classes_).index(structure_type)
    confidence = float(proba[class_idx])

    p10, p50, p90 = _volume_quantiles(float(features["roof_area_sqm"]), runoff)
    dimensions = _structure_dimensions(structure_type, {k: float(features[k]) for k in FEATURE_COLUMNS})

    return {
        "structure_type": structure_type,
        "confidence": round(confidence, 3),
        "dimensions": dimensions,
        "annual_litres_p10": round(p10, 1),
        "annual_litres_p50": round(p50, 1),
        "annual_litres_p90": round(p90, 1),
    }


def cluster_score(ward_features: dict) -> float:
    """
    Return 0-1 ward-level recharge potential score from KMeans tiers.

    Required keys: avg_rainfall_mm, avg_groundwater_depth_m, built_up_density.
    """
    _load_artifacts()

    missing = [k for k in WARD_FEATURE_COLUMNS if k not in ward_features]
    if missing:
        raise ValueError(f"Missing required ward features: {missing}")

    X = np.array([[float(ward_features[k]) for k in WARD_FEATURE_COLUMNS]], dtype=float)
    X_scaled = _ward_scaler.transform(X)
    cluster_id = int(_ward_kmeans.predict(X_scaled)[0])
    return round(float(_ward_cluster_map[cluster_id]), 3)
