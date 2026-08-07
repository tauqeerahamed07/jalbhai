"""
Deterministic baseline calculation engine, standard CGWB approach.
This MUST always produce a sensible result on its own, with zero
dependency on the ML module - it's the fallback that keeps /api/assess
from ever returning garbage if Person C's model isn't wired in yet.
"""

RUNOFF_COEFFICIENTS = {
    "concrete": 0.85,
    "tiled": 0.75,
    "metal_sheet": 0.90,
    "asbestos": 0.80,
}


def harvestable_volume_litres(roof_area_sqm: float, annual_rainfall_mm: float, roof_type: str) -> float:
    coeff = RUNOFF_COEFFICIENTS.get(roof_type, 0.8)
    # litres = m^2 * mm * coefficient  (1mm rain over 1m^2 = 1 litre)
    return round(roof_area_sqm * annual_rainfall_mm * coeff, 1)


def recommend_structure(
    roof_area_sqm: float,
    open_space_type: str,
    open_space_area_sqm: float,
    depth_to_water_table_m: float,
    infiltration_rate_mm_hr: float,
) -> dict:
    """
    Simple decision tree mirroring CGWB rule-of-thumb dimensioning.
    Runs as the fallback path before/without the ML classifier.
    """
    shallow_water_table = depth_to_water_table_m <= 8.0
    deep_water_table = depth_to_water_table_m > 8.0

    if open_space_type == "linear_strip" and open_space_area_sqm >= 6:
        length_m = min(max(open_space_area_sqm / 1.0, 3), 15)
        return {
            "structure_type": "recharge_trench",
            "dimensions": {"length_m": round(length_m, 1), "width_m": 0.6, "depth_m": 1.5},
            "rationale": (
                "Linear open space available (driveway/boundary strip) - a recharge trench "
                "makes efficient use of a narrow footprint and works well for moderate roof areas."
            ),
        }

    if open_space_type == "large_open_area" and open_space_area_sqm >= 20:
        radius_m = min(max((open_space_area_sqm / 3.14) ** 0.5, 1.5), 4)
        return {
            "structure_type": "percolation_tank",
            "dimensions": {"radius_m": round(radius_m, 1), "depth_m": 2.0},
            "rationale": (
                "A sizeable open area is available, so a percolation tank is recommended - "
                "it handles larger roof catchments better than a small pit or trench."
            ),
        }

    if deep_water_table and open_space_area_sqm < 20:
        depth_m = min(15, max(6, depth_to_water_table_m - 2))
        return {
            "structure_type": "recharge_shaft",
            "dimensions": {"diameter_m": 0.9, "depth_m": round(depth_m, 1)},
            "rationale": (
                f"Water table is relatively deep (~{depth_to_water_table_m:.1f}m) and open space is "
                "limited, so a recharge shaft is used to bypass poorly-permeable surface layers."
            ),
        }

    # Default: recharge pit - the standard choice for shallow water table + small roof/open area.
    depth_m = 1.5 if shallow_water_table else 3.0
    diameter_m = 1.2 if roof_area_sqm < 100 else 1.8
    return {
        "structure_type": "recharge_pit",
        "dimensions": {"diameter_m": diameter_m, "depth_m": depth_m},
        "rationale": (
            "Shallow-to-moderate water table and a modest roof/open-space footprint make a "
            "standard recharge pit the most practical CGWB-recommended structure here."
        ),
    }


def classify_feasibility(annual_volume_litres: float, infiltration_rate_mm_hr: float, depth_to_water_table_m: float) -> str:
    """Very simple rule-based feasibility bucket, used until/unless ML classifier overrides it."""
    if annual_volume_litres < 15000 or infiltration_rate_mm_hr < 4:
        return "marginal"
    if depth_to_water_table_m > 15:
        return "marginal"
    if annual_volume_litres >= 60000 and infiltration_rate_mm_hr >= 10:
        return "highly_feasible"
    return "feasible"
