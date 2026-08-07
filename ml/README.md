# JalRakshak ML Layer (Person C)

Handoff module for Person B backend integration.

## Quick start

```bash
pip install -r requirements.txt
python -m ml.train_models   # already run; artifacts in ml/models/
```

## Integration (Person B)

```python
from ml.predict import predict, cluster_score

# POST /api/assess — after gathering site features
ml_result = predict({
    "soil_infiltration_rate_mm_hr": features["soil_infiltration_rate_mm_hr"],
    "depth_to_water_table_m": features["depth_to_water_table_m"],
    "open_space_sqm": features["open_space_sqm"],
    "roof_area_sqm": features["roof_area_sqm"],
    "annual_rainfall_mm": features["annual_rainfall_mm"],
    "slope_percent": features["slope_percent"],
    "runoff_coefficient": 0.85,  # optional
})

# GET /api/wards/heatmap — per ward
score = cluster_score({
    "avg_rainfall_mm": ward["avg_rainfall_mm"],
    "avg_groundwater_depth_m": ward["avg_groundwater_depth_m"],
    "built_up_density": ward["built_up_density"],
})
```

See `MODEL_CARD.md` for full documentation and judge Q&A.
