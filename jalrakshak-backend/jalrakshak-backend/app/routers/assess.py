from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    AssessRequest, AssessResponse, RainfallData, SoilData, GroundwaterData,
    ElevationData, VolumeEstimate, StructureRecommendation,
)
from app.external_apis import get_rainfall, get_soil, get_elevation
from app.crud import nearest_well
from app.calc_engine import harvestable_volume_litres, recommend_structure, classify_feasibility
from app import ml

router = APIRouter(prefix="/api", tags=["assess"])


@router.post("/assess", response_model=AssessResponse)
async def assess(req: AssessRequest, db: Session = Depends(get_db)):
    notes: list[str] = []

    # 1. Rainfall (Open-Meteo, with climatology fallback)
    rainfall = await get_rainfall(req.latitude, req.longitude)
    if "fallback" in rainfall["data_source"]:
        notes.append("Rainfall used a climatology fallback because Open-Meteo was unreachable.")

    # 2. Soil (SoilGrids, with hardcoded Chennai zone fallback)
    soil = await get_soil(req.latitude, req.longitude)
    if "fallback" in soil["data_source"]:
        notes.append("Soil data used the hardcoded Chennai soil-zone fallback table, not live SoilGrids.")

    # 3. Nearest groundwater well (seeded CGWB table + haversine)
    well, distance_km = nearest_well(db, req.latitude, req.longitude)
    groundwater = GroundwaterData(
        nearest_station_name=well.station_name,
        distance_km=round(distance_km, 2),
        depth_to_water_table_m=well.latest_depth_m,
        reading_date=well.reading_date,
        data_source=well.source,
    )
    notes.append(
        "Groundwater depth is from the nearest of 15 seeded CGWB monitoring stations "
        f"({well.station_name}, {distance_km:.1f}km away), not a live India-WRIS query."
    )

    # 4. Elevation (OpenTopoData, with flat default fallback)
    elevation = await get_elevation(req.latitude, req.longitude)
    if "fallback" in elevation["data_source"]:
        notes.append("Elevation used a flat Chennai-average fallback because OpenTopoData was unreachable.")

    # 5. Deterministic calculation engine (always runs, ML never blocks this)
    deterministic_volume = harvestable_volume_litres(
        req.roof_area_sqm, rainfall["annual_total_mm"], req.roof_type.value
    )
    structure = recommend_structure(
        roof_area_sqm=req.roof_area_sqm,
        open_space_type=req.open_space_type.value,
        open_space_area_sqm=req.open_space_area_sqm or 0,
        depth_to_water_table_m=groundwater.depth_to_water_table_m,
        infiltration_rate_mm_hr=soil["infiltration_rate_mm_hr"],
    )
    rule_based_feasibility = classify_feasibility(
        deterministic_volume, soil["infiltration_rate_mm_hr"], groundwater.depth_to_water_table_m
    )

    # 6. ML module (stubbed by default; Person C swaps app/ml.py internals)
    ml_features = {
        "roof_area_sqm": req.roof_area_sqm,
        "roof_type": req.roof_type.value,
        "annual_rainfall_mm": rainfall["annual_total_mm"],
        "infiltration_rate_mm_hr": soil["infiltration_rate_mm_hr"],
        "depth_to_water_table_m": groundwater.depth_to_water_table_m,
        "elevation_m": elevation["elevation_m"],
        "deterministic_volume_litres": deterministic_volume,
    }
    ml_out = ml.predict(ml_features)
    feasibility = ml_out.get("feasibility_classification") or rule_based_feasibility

    volume_estimate = VolumeEstimate(
        deterministic_litres_per_year=deterministic_volume,
        ml_p10_litres_per_year=ml_out["p10_litres_per_year"],
        ml_p50_litres_per_year=ml_out["p50_litres_per_year"],
        ml_p90_litres_per_year=ml_out["p90_litres_per_year"],
        ml_confidence=ml_out["confidence"],
    )

    return AssessResponse(
        input_echo=req,
        rainfall=RainfallData(**rainfall),
        soil=SoilData(**soil),
        groundwater=groundwater,
        elevation=ElevationData(**elevation),
        volume_estimate=volume_estimate,
        structure_recommendation=StructureRecommendation(**structure),
        feasibility_classification=feasibility,
        notes=notes,
    )
