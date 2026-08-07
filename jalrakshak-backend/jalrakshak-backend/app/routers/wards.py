from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import WardHeatmapResponse, WardScore
from app.crud import all_wards
from app.external_apis import get_rainfall
from app.soil_fallback import lookup_soil_zone
from app import ml

router = APIRouter(prefix="/api", tags=["wards"])


def _score_label(score: float) -> str:
    if score >= 65:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


@router.get("/wards/heatmap", response_model=WardHeatmapResponse)
async def wards_heatmap(db: Session = Depends(get_db)):
    wards = all_wards(db)
    out = []
    for w in wards:
        # Use the same soil fallback + a cheap rainfall lookup per ward centroid.
        # (Wards are static, so this endpoint is a good candidate for the
        # optional APScheduler cache job later - live-calling per request is
        # fine for a demo with ~15 wards.)
        rainfall = await get_rainfall(w.centroid_lat, w.centroid_lng)
        soil = lookup_soil_zone(w.centroid_lat, w.centroid_lng)

        score = ml.cluster_score({
            "annual_rainfall_mm": rainfall["annual_total_mm"],
            "infiltration_rate_mm_hr": soil["infiltration_rate_mm_hr"],
            "depth_to_water_table_m": 8.0,  # ward-level generic assumption; per-well lookup would be more precise
        })

        out.append(WardScore(
            ward_number=w.ward_number,
            ward_name=w.ward_name,
            centroid={"lat": w.centroid_lat, "lng": w.centroid_lng},
            bounding_box={
                "min_lat": w.min_lat, "max_lat": w.max_lat,
                "min_lng": w.min_lng, "max_lng": w.max_lng,
            },
            score=score,
            score_label=_score_label(score),
        ))

    return WardHeatmapResponse(wards=out)
