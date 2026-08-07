from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base


class GroundwaterWell(Base):
    """
    Seeded from public CGWB / India-WRIS Chennai monitoring station data.
    Plain lat/lng + Python haversine is used for "nearest well" lookup -
    no PostGIS required. If USE_POSTGIS=true and you've got a geometry
    column set up, swap the query in crud.py for an ST_Distance query instead.
    """
    __tablename__ = "groundwater_wells"

    id = Column(Integer, primary_key=True, index=True)
    station_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    latest_depth_m = Column(Float, nullable=False)  # depth to water table, metres below ground level
    reading_date = Column(String, nullable=False)   # ISO date string of the reading, e.g. "2024-05-15"
    source = Column(String, default="CGWB public dashboard (manually synced)")


class Ward(Base):
    """
    Chennai ward centroids + rough bounding-box polygons for the heatmap.
    Bounding boxes are intentionally approximate for demo purposes -
    swap for real GIS shapefiles later if precision matters.
    """
    __tablename__ = "wards"

    id = Column(Integer, primary_key=True, index=True)
    ward_number = Column(Integer, nullable=False)
    ward_name = Column(String, nullable=False)
    centroid_lat = Column(Float, nullable=False)
    centroid_lng = Column(Float, nullable=False)
    # bounding box corners (min/max lat/lng) - a crude stand-in for a real polygon
    min_lat = Column(Float, nullable=False)
    max_lat = Column(Float, nullable=False)
    min_lng = Column(Float, nullable=False)
    max_lng = Column(Float, nullable=False)
