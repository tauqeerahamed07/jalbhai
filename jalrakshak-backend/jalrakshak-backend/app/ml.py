"""
ML integration point.

Person C: replace the BODIES of `predict()` and `cluster_score()` below
with your real model calls. Keep the function signatures and return
shapes EXACTLY as they are - main.py / routers already depend on this
shape, so a drop-in replacement here requires zero changes anywhere else.

Until USE_REAL_ML=true in .env, both functions return plausible stubbed
numbers derived from the deterministic calc so the API never looks broken
in a demo, while still being obviously "fake" enough (round confidence,
symmetric P10/P90 spread) that it's easy to tell stub output from real
model output once you're integrating.
"""

from app.config import settings


def predict(features: dict) -> dict:
    """
    features: dict of everything available at assessment time, e.g.
        {
            "roof_area_sqm": float,
            "roof_type": str,
            "annual_rainfall_mm": float,
            "infiltration_rate_mm_hr": float,
            "depth_to_water_table_m": float,
            "elevation_m": float,
            "deterministic_volume_litres": float,
        }

    MUST return:
        {
            "p10_litres_per_year": float,
            "p50_litres_per_year": float,
            "p90_litres_per_year": float,
            "confidence": float,           # 0-1
            "feasibility_classification": str,  # optional override of the rule-based one
        }
    """
    if settings.use_real_ml:
        raise NotImplementedError(
            "USE_REAL_ML is true but Person C's real model hasn't been wired in yet. "
            "Implement the model call here, or set USE_REAL_ML=false to keep using the stub."
        )

    baseline = features.get("deterministic_volume_litres", 0.0)
    return {
        "p10_litres_per_year": round(baseline * 0.8, 1),
        "p50_litres_per_year": round(baseline * 1.0, 1),
        "p90_litres_per_year": round(baseline * 1.15, 1),
        "confidence": 0.6,  # deliberately mediocre/round so it's obviously a stub
    }


def cluster_score(ward_features: dict) -> float:
    """
    ward_features: dict with at least
        {"annual_rainfall_mm": float, "infiltration_rate_mm_hr": float, "depth_to_water_table_m": float}

    MUST return a float 0-100 (higher = better RTRWH potential for that ward).
    """
    if settings.use_real_ml:
        raise NotImplementedError(
            "USE_REAL_ML is true but Person C's real clustering model hasn't been wired in yet."
        )

    rainfall = ward_features.get("annual_rainfall_mm", 1100)
    infiltration = ward_features.get("infiltration_rate_mm_hr", 10)
    depth = ward_features.get("depth_to_water_table_m", 8)

    # Simple weighted formula stand-in: more rain + better infiltration + shallower
    # water table => higher score. Purely a placeholder for the real clustering model.
    rainfall_score = min(rainfall / 1400, 1.0) * 40
    infiltration_score = min(infiltration / 25, 1.0) * 35
    depth_score = max(0, 1 - (depth / 20)) * 25
    return round(rainfall_score + infiltration_score + depth_score, 1)
