import math
from sqlalchemy.orm import Session

from app.db_models import GroundwaterWell, Ward
from app.seed_data import GROUNDWATER_WELLS, wards_with_bbox


def seed_if_empty(db: Session):
    if db.query(GroundwaterWell).count() == 0:
        for row in GROUNDWATER_WELLS:
            db.add(GroundwaterWell(**row, source="CGWB public dashboard (manually synced)"))
    if db.query(Ward).count() == 0:
        for row in wards_with_bbox():
            db.add(Ward(**row))
    db.commit()


def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def nearest_well(db: Session, lat: float, lng: float) -> tuple[GroundwaterWell, float]:
    """
    Plain-Python nearest-neighbour scan. Fine at this table size (10-20 rows).
    If USE_POSTGIS=true and geometry columns are set up, replace this with an
    ST_Distance(ST_MakePoint(...), geom) ORDER BY ... LIMIT 1 query instead.
    """
    wells = db.query(GroundwaterWell).all()
    best, best_dist = None, float("inf")
    for w in wells:
        d = haversine_km(lat, lng, w.latitude, w.longitude)
        if d < best_dist:
            best, best_dist = w, d
    return best, best_dist


def all_wards(db: Session):
    return db.query(Ward).all()
