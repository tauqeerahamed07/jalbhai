"""Smoke tests for JalRakshak ML handoff module.

Run from project root:
    python test_ml.py
"""

from ml.predict import predict, cluster_score


def test_predict_residential():
    result = predict(
        {
            "soil_infiltration_rate_mm_hr": 25.0,
            "depth_to_water_table_m": 8.0,
            "open_space_sqm": 45.0,
            "roof_area_sqm": 120.0,
            "annual_rainfall_mm": 1400.0,
            "slope_percent": 2.0,
        }
    )
    assert result["structure_type"] in {
        "recharge_pit",
        "recharge_trench",
        "recharge_shaft",
        "percolation_tank",
    }
    assert 0 <= result["confidence"] <= 1
    assert result["annual_litres_p10"] <= result["annual_litres_p50"] <= result["annual_litres_p90"]
    assert "dimensions" in result
    print("PASS predict (residential):", result["structure_type"], f"conf={result['confidence']}")


def test_predict_percolation_tank():
    result = predict(
        {
            "soil_infiltration_rate_mm_hr": 30.0,
            "depth_to_water_table_m": 6.0,
            "open_space_sqm": 150.0,
            "roof_area_sqm": 200.0,
            "annual_rainfall_mm": 1450.0,
            "slope_percent": 1.0,
        }
    )
    assert result["structure_type"] == "percolation_tank"
    print("PASS predict (large open space): percolation_tank")


def test_cluster_score():
    score = cluster_score(
        {
            "avg_rainfall_mm": 1400,
            "avg_groundwater_depth_m": 7.0,
            "built_up_density": 0.75,
        }
    )
    assert 0 <= score <= 1
    print(f"PASS cluster_score: {score}")


def test_missing_features():
    try:
        predict({"roof_area_sqm": 100})
        raise AssertionError("Should have raised ValueError")
    except ValueError as exc:
        assert "Missing required features" in str(exc)
        print("PASS validation: missing features rejected")


if __name__ == "__main__":
    test_predict_residential()
    test_predict_percolation_tank()
    test_cluster_score()
    test_missing_features()
    print("\nAll tests passed.")
