"""
Train all JalRakshak ML models and persist artifacts to ml/models/.

Run once before integration:
    python -m ml.train_models
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import joblib
import numpy as np
import requests
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"
DATA_DIR = ROOT / "data"

FEATURE_COLUMNS = [
    "soil_infiltration_rate_mm_hr",
    "depth_to_water_table_m",
    "open_space_sqm",
    "roof_area_sqm",
    "annual_rainfall_mm",
    "slope_percent",
]

STRUCTURE_TYPES = [
    "recharge_pit",
    "recharge_trench",
    "recharge_shaft",
    "percolation_tank",
]

DEFAULT_RUNOFF_COEFFICIENT = 0.85

# Approximate Chennai ward / zone table (public estimates + CGWB zone patterns).
CHENNAI_WARDS = [
    {"ward": "Thiruvanmiyur", "avg_rainfall_mm": 1450, "avg_groundwater_depth_m": 4.5, "built_up_density": 0.72},
    {"ward": "Adyar", "avg_rainfall_mm": 1420, "avg_groundwater_depth_m": 5.0, "built_up_density": 0.78},
    {"ward": "Besant Nagar", "avg_rainfall_mm": 1460, "avg_groundwater_depth_m": 4.2, "built_up_density": 0.68},
    {"ward": "T. Nagar", "avg_rainfall_mm": 1380, "avg_groundwater_depth_m": 8.5, "built_up_density": 0.92},
    {"ward": "Anna Nagar", "avg_rainfall_mm": 1360, "avg_groundwater_depth_m": 10.0, "built_up_density": 0.85},
    {"ward": "Ambattur", "avg_rainfall_mm": 1320, "avg_groundwater_depth_m": 12.5, "built_up_density": 0.80},
    {"ward": "Tambaram", "avg_rainfall_mm": 1480, "avg_groundwater_depth_m": 14.0, "built_up_density": 0.65},
    {"ward": "Chromepet", "avg_rainfall_mm": 1450, "avg_groundwater_depth_m": 11.0, "built_up_density": 0.70},
    {"ward": "Porur", "avg_rainfall_mm": 1340, "avg_groundwater_depth_m": 13.0, "built_up_density": 0.75},
    {"ward": "Velachery", "avg_rainfall_mm": 1410, "avg_groundwater_depth_m": 6.5, "built_up_density": 0.82},
    {"ward": "Perambur", "avg_rainfall_mm": 1350, "avg_groundwater_depth_m": 9.0, "built_up_density": 0.88},
    {"ward": "Royapuram", "avg_rainfall_mm": 1370, "avg_groundwater_depth_m": 3.5, "built_up_density": 0.90},
    {"ward": "Mylapore", "avg_rainfall_mm": 1430, "avg_groundwater_depth_m": 5.5, "built_up_density": 0.86},
    {"ward": "Guindy", "avg_rainfall_mm": 1390, "avg_groundwater_depth_m": 7.0, "built_up_density": 0.84},
    {"ward": "Sholinganallur", "avg_rainfall_mm": 1470, "avg_groundwater_depth_m": 8.0, "built_up_density": 0.60},
    {"ward": "Madipakkam", "avg_rainfall_mm": 1400, "avg_groundwater_depth_m": 9.5, "built_up_density": 0.77},
    {"ward": "Ennore", "avg_rainfall_mm": 1330, "avg_groundwater_depth_m": 2.8, "built_up_density": 0.55},
    {"ward": "Manali", "avg_rainfall_mm": 1310, "avg_groundwater_depth_m": 3.0, "built_up_density": 0.50},
]


def cgwB_label(row: dict) -> str:
    """
    CGWB manual-inspired labeling function (documented in MODEL_CARD.md).

    Priority order resolves overlaps; boundary noise is injected at training time.
    """
    wt = row["depth_to_water_table_m"]
    space = row["open_space_sqm"]
    slope = row["slope_percent"]

    if space >= 100 and slope < 8:
        return "percolation_tank"
    if wt >= 15 and space < 20:
        return "recharge_shaft"
    if 30 <= space < 100 and wt < 12:
        return "recharge_trench"
    if wt < 10 and space < 20:
        return "recharge_pit"

    # Secondary rules for ambiguous cases
    if space >= 60:
        return "percolation_tank"
    if wt >= 12:
        return "recharge_shaft"
    if space >= 25:
        return "recharge_trench"
    return "recharge_pit"


def maybe_flip_label(label: str, rng: np.random.Generator) -> str:
    """Inject ~8% boundary noise so classes are not trivially separable."""
    if rng.random() > 0.08:
        return label
    others = [s for s in STRUCTURE_TYPES if s != label]
    return str(rng.choice(others))


def generate_structure_training_data(n_samples: int = 4000, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    rows = []
    labels = []

    for _ in range(n_samples):
        row = {
            "soil_infiltration_rate_mm_hr": float(rng.uniform(5, 50)),
            "depth_to_water_table_m": float(rng.uniform(2, 25)),
            "open_space_sqm": float(rng.uniform(5, 200)),
            "roof_area_sqm": float(rng.uniform(30, 500)),
            "annual_rainfall_mm": float(rng.uniform(800, 1600)),
            "slope_percent": float(rng.uniform(0, 15)),
        }
        label = maybe_flip_label(cgwB_label(row), rng)
        rows.append([row[c] for c in FEATURE_COLUMNS])
        labels.append(label)

    return np.array(rows, dtype=float), np.array(labels)


def train_structure_classifier() -> dict:
    X, y = generate_structure_training_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    accuracy = float(accuracy_score(y_test, y_pred))
    report = classification_report(y_test, y_pred, output_dict=True)

    joblib.dump(clf, MODELS_DIR / "structure_classifier.joblib")

    metrics = {"accuracy": accuracy, "classification_report": report}
    with open(MODELS_DIR / "structure_classifier_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Structure classifier accuracy: {accuracy:.3f}")
    return metrics


def fetch_chennai_annual_rainfall() -> list[float]:
    cache_path = DATA_DIR / "chennai_annual_rainfall.json"
    if cache_path.exists():
        with open(cache_path, encoding="utf-8") as f:
            data = json.load(f)
            return data["annual_totals_mm"]

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        "?latitude=13.08&longitude=80.27"
        "&start_date=2015-01-01&end_date=2025-12-31"
        "&daily=precipitation_sum"
        "&timezone=Asia%2FKolkata"
    )
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    payload = response.json()
    dates = payload["daily"]["time"]
    daily_mm = payload["daily"]["precipitation_sum"]

    annual: dict[int, float] = {}
    for date_str, mm in zip(dates, daily_mm):
        year = int(date_str[:4])
        annual[year] = annual.get(year, 0.0) + (mm or 0.0)

    totals = [annual[y] for y in sorted(annual)]
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump({"annual_totals_mm": totals, "years": sorted(annual.keys())}, f, indent=2)

    print(f"Fetched {len(totals)} years of Chennai rainfall: {totals}")
    return totals


def build_rainfall_volume_artifact() -> dict:
    annual_totals = fetch_chennai_annual_rainfall()
    arr = np.array(annual_totals, dtype=float)

    artifact = {
        "annual_totals_mm": annual_totals,
        "p10_rainfall_mm": float(np.percentile(arr, 10)),
        "p50_rainfall_mm": float(np.percentile(arr, 50)),
        "p90_rainfall_mm": float(np.percentile(arr, 90)),
        "default_runoff_coefficient": DEFAULT_RUNOFF_COEFFICIENT,
        "source": "Open-Meteo ERA5 archive (13.08N, 80.27E, 2015-2025)",
    }

    with open(MODELS_DIR / "rainfall_volume.json", "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)

    return artifact


def ward_recharge_potential_score(row: dict) -> float:
    """Reference score for cluster ordering (higher = better recharge potential)."""
    rainfall_norm = (row["avg_rainfall_mm"] - 1300) / (1500 - 1300)
    depth_norm = 1 - (row["avg_groundwater_depth_m"] - 2) / (15 - 2)
    density_norm = 1 - row["built_up_density"]
    return float(np.clip(0.4 * rainfall_norm + 0.35 * depth_norm + 0.25 * density_norm, 0, 1))


def train_ward_clustering() -> dict:
    ward_rows = CHENNAI_WARDS
    X = np.array(
        [
            [
                w["avg_rainfall_mm"],
                w["avg_groundwater_depth_m"],
                w["built_up_density"],
            ]
            for w in ward_rows
        ],
        dtype=float,
    )

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # Map clusters to 0-1 scores by mean reference potential (discovered tiers).
    cluster_scores: dict[int, float] = {}
    for cluster_id in range(4):
        members = [ward_rows[i] for i, lbl in enumerate(labels) if lbl == cluster_id]
        cluster_scores[cluster_id] = float(np.mean([ward_recharge_potential_score(m) for m in members]))

    # Normalize cluster scores to 0-1 range
    scores = np.array(list(cluster_scores.values()))
    min_s, max_s = scores.min(), scores.max()
    normalized = {int(k): float((v - min_s) / (max_s - min_s + 1e-9)) for k, v in cluster_scores.items()}

    ward_output = []
    for ward, lbl in zip(ward_rows, labels):
        ward_output.append(
            {
                **ward,
                "cluster": int(lbl),
                "cluster_score": normalized[int(lbl)],
            }
        )

    artifact = {
        "wards": ward_output,
        "cluster_score_map": normalized,
        "feature_names": ["avg_rainfall_mm", "avg_groundwater_depth_m", "built_up_density"],
    }

    joblib.dump(kmeans, MODELS_DIR / "ward_kmeans.joblib")
    joblib.dump(scaler, MODELS_DIR / "ward_scaler.joblib")
    with open(MODELS_DIR / "ward_clustering.json", "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)

    print("Ward clusters:", normalized)
    return artifact


def main() -> None:
    random.seed(42)
    np.random.seed(42)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Training structure classifier...")
    train_structure_classifier()

    print("Building rainfall volume artifact...")
    build_rainfall_volume_artifact()

    print("Training ward clustering...")
    train_ward_clustering()

    print("All models saved to", MODELS_DIR)


if __name__ == "__main__":
    main()
