# JalRakshak ML Model Card

Last updated: 2026-08-07  
Owner: Person C (Data Science & ML)

## Overview

This module provides three lightweight models for the JalRakshak RTRWH/AR assessment tool (Chennai, India):

1. **Structure type classifier** — recommends recharge structure type from site features.
2. **Harvestable volume quantiles** — P10/P50/P90 annual harvest range using historical rainfall variability.
3. **Ward recharge potential clustering** — 0–1 score per ward from KMeans tiers.

**Integration:** Person B imports `predict()` and `cluster_score()` from `ml/predict.py`. Models are pre-trained; no retraining at request time.

---

## Model 1: Structure Type Classifier

| Field | Value |
|---|---|
| **Algorithm** | `RandomForestClassifier` (200 trees, balanced class weights) |
| **Output** | One of `recharge_pit`, `recharge_trench`, `recharge_shaft`, `percolation_tank` + confidence (max class probability) |
| **Validation** | 80/20 stratified hold-out split |

### Input features

| Feature | Typical range (Chennai) |
|---|---|
| `soil_infiltration_rate_mm_hr` | 5–50 mm/hr |
| `depth_to_water_table_m` | 2–25 m |
| `open_space_sqm` | 5–200 sqm |
| `roof_area_sqm` | 30–500 sqm |
| `annual_rainfall_mm` | 800–1600 mm |
| `slope_percent` | 0–15 % |

### Training data (honest disclosure)

**Not** real-world labeled construction outcomes. Training labels were generated from **CGWB manual-inspired rules** (expert system distillation):

- Shallow water table (&lt;10 m) + small space (&lt;20 sqm) → **recharge pit**
- Linear/moderate open space (30–100 sqm) → **recharge trench**
- Deep water table (&gt;15 m) + very limited space (&lt;20 sqm) → **recharge shaft**
- Large open space (&gt;100 sqm) + gentle slope → **percolation tank**

~4,000 synthetic rows sampled from realistic ranges; **~8% label noise** injected at boundaries so classes overlap slightly (not trivially separable).

### Validation metric

See `ml/models/structure_classifier_metrics.json`. Current hold-out **accuracy: 0.911** (91.1% on 800-sample test split).

### Limitations

- Rules are approximations of CGWB guidance, not a full manual parse.
- Should be retrained on observed project outcomes when available.

---

## Model 2: Harvestable Volume (P10 / P50 / P90)

| Field | Value |
|---|---|
| **Method** | Empirical quantiles from historical annual rainfall (not a single deterministic point estimate) |
| **Formula** | `roof_area_sqm × annual_rainfall_mm(year) × runoff_coefficient` per year, then P10/P50/P90 across years |
| **Default runoff coefficient** | 0.85 (concrete/RCC; override via `runoff_coefficient` in `predict()`) |

### Data source

Open-Meteo ERA5 archive API:

`https://archive-api.open-meteo.com/v1/archive?latitude=13.08&longitude=80.27&start_date=2015-01-01&end_date=2025-12-31&daily=precipitation_sum`

Cached at `ml/data/chennai_annual_rainfall.json`.

### Why quantiles?

Chennai annual rainfall varies year to year. A single `roof × mean rainfall × coefficient` number is misleading for planning. P10/P50/P90 gives a **realistic range** judges can trust.

### Validation

Not a supervised ML model — **no accuracy metric**. Sanity check: P50 should align with `roof_area × median_annual_rainfall × runoff_coefficient`.

---

## Model 3: Ward Recharge Potential Clustering

| Field | Value |
|---|---|
| **Algorithm** | `KMeans` (k=4) on standardized ward features |
| **Output** | Cluster tier mapped to **0–1 score** (higher = better recharge potential) |
| **Wards** | 18 Chennai zones (manual table in `ml/train_models.py`) |

### Input features (per ward)

| Feature | Description |
|---|---|
| `avg_rainfall_mm` | Zone rainfall estimate |
| `avg_groundwater_depth_m` | Shallow = better for recharge |
| `built_up_density` | 0–1 proxy (lower = more open/permeable area) |

Clusters are ordered by mean reference potential so tiers read as low → high recharge potential.

### Validation

Unsupervised — **silhouette not required for demo**. Ward scores are interpretable via cluster membership and align with hydrological intuition (e.g. Ennore/Manali coastal shallow water table → higher tiers).

---

## API Handoff

```python
from ml.predict import predict, cluster_score

predict({
    "soil_infiltration_rate_mm_hr": 25.0,
    "depth_to_water_table_m": 8.0,
    "open_space_sqm": 45.0,
    "roof_area_sqm": 120.0,
    "annual_rainfall_mm": 1400.0,
    "slope_percent": 2.0,
})

cluster_score({
    "avg_rainfall_mm": 1400,
    "avg_groundwater_depth_m": 7.0,
    "built_up_density": 0.75,
})
```

### `predict()` response shape

```json
{
  "structure_type": "recharge_trench",
  "confidence": 0.87,
  "dimensions": {"length_m": 18.0, "width_m": 1.2, "depth_m": 1.76},
  "annual_litres_p10": 85000.0,
  "annual_litres_p50": 102000.0,
  "annual_litres_p90": 118000.0
}
```

---

## Retraining

```bash
pip install -r requirements.txt
python -m ml.train_models
```

Artifacts written to `ml/models/`.

---

## Explicitly skipped (per spec)

- Deep learning
- Hyperparameter tuning beyond defaults
- Cross-validation beyond single train/test split

---

## How to answer judges: "How do you know this is accurate?"

1. **Classifier:** Distills published CGWB structure-selection logic into a model that generalizes at boundaries; hold-out accuracy reported in metrics JSON. Honest that labels are rule-derived, not thousands of field outcomes.
2. **Volume range:** Uses **11 years of real Chennai rainfall** from Open-Meteo; quantiles reflect actual inter-annual variability.
3. **Ward scores:** Unsupervised clustering on public zone estimates; tiers discovered from data, not a single hardcoded formula.
