from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class RoofType(str, Enum):
    concrete = "concrete"
    tiled = "tiled"
    metal_sheet = "metal_sheet"
    asbestos = "asbestos"


class OpenSpaceType(str, Enum):
    none = "none"
    small_yard = "small_yard"       # a few sq m, room for a pit
    linear_strip = "linear_strip"   # driveway/boundary strip, good for a trench
    large_open_area = "large_open_area"  # room for a percolation tank


# ---------- POST /api/assess ----------

class AssessRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    roof_area_sqm: float = Field(..., gt=0)
    roof_type: RoofType
    open_space_type: OpenSpaceType = OpenSpaceType.none
    open_space_area_sqm: Optional[float] = Field(0, ge=0)
    dwellers: Optional[int] = Field(None, ge=1)
    address_label: Optional[str] = None  # free-text label the user typed, echoed back for display


class RainfallData(BaseModel):
    annual_total_mm: float
    monthly_mm: dict  # {"jan": 24.1, "feb": 8.3, ...}
    data_source: str = "Open-Meteo"


class SoilData(BaseModel):
    texture_class: str          # e.g. "sandy", "clay", "loam"
    infiltration_rate_mm_hr: float
    data_source: str            # "SoilGrids" or "Chennai zone fallback table"


class GroundwaterData(BaseModel):
    nearest_station_name: str
    distance_km: float
    depth_to_water_table_m: float
    reading_date: str
    data_source: str = "CGWB public data (synced)"


class ElevationData(BaseModel):
    elevation_m: float
    data_source: str = "OpenTopoData (SRTM 30m)"


class StructureRecommendation(BaseModel):
    structure_type: str          # recharge_pit | recharge_trench | recharge_shaft | percolation_tank
    dimensions: dict             # e.g. {"diameter_m": 1.5, "depth_m": 2.5}
    estimated_cost_inr: Optional[float] = None
    rationale: str


class VolumeEstimate(BaseModel):
    deterministic_litres_per_year: float
    ml_p10_litres_per_year: float
    ml_p50_litres_per_year: float
    ml_p90_litres_per_year: float
    ml_confidence: float  # 0-1


class AssessResponse(BaseModel):
    input_echo: AssessRequest
    rainfall: RainfallData
    soil: SoilData
    groundwater: GroundwaterData
    elevation: ElevationData
    volume_estimate: VolumeEstimate
    structure_recommendation: StructureRecommendation
    feasibility_classification: str  # e.g. "highly_feasible" | "feasible" | "marginal" | "not_recommended"
    notes: List[str] = []  # any fallback/simplification disclaimers surfaced to the UI


# ---------- GET /api/wards/heatmap ----------

class WardScore(BaseModel):
    ward_number: int
    ward_name: str
    centroid: dict          # {"lat": ..., "lng": ...}
    bounding_box: dict      # {"min_lat":..,"max_lat":..,"min_lng":..,"max_lng":..}
    score: float            # 0-100, higher = better RTRWH potential
    score_label: str        # "high" | "medium" | "low"


class WardHeatmapResponse(BaseModel):
    wards: List[WardScore]
    data_source: str = "ml.cluster_score (or formula fallback)"


# ---------- POST /api/report ----------
# Reuses AssessRequest + AssessResponse shape; report endpoint accepts the
# full AssessResponse (so the frontend doesn't need to re-run assessment)
# and streams back a PDF.

class ReportRequest(BaseModel):
    assessment: AssessResponse
