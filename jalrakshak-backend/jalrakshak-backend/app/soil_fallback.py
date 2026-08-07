"""
Fallback soil-zone lookup used if the SoilGrids API is slow/unreachable
or its response is awkward to parse under time pressure.

Rough bounding boxes for 6 broad Chennai soil zones (coastal sandy belt,
inland clay/alluvium, etc.). These are simplifications of the real,
much more granular soil map - good enough for a demo infiltration proxy,
NOT a substitute for a real soil survey. Note this in report footers.
"""

CHENNAI_SOIL_ZONES = [
    {  # East coastal strip - sandy
        "name": "coastal_sandy",
        "min_lat": 12.85, "max_lat": 13.20, "min_lng": 80.24, "max_lng": 80.35,
        "texture_class": "sandy",
        "infiltration_rate_mm_hr": 30.0,
    },
    {  # North Chennai / Ennore - sandy-clay mix
        "name": "north_sandy_clay",
        "min_lat": 13.10, "max_lat": 13.25, "min_lng": 80.10, "max_lng": 80.30,
        "texture_class": "sandy_clay_loam",
        "infiltration_rate_mm_hr": 15.0,
    },
    {  # Central Chennai - loamy
        "name": "central_loam",
        "min_lat": 12.98, "max_lat": 13.10, "min_lng": 80.18, "max_lng": 80.27,
        "texture_class": "loam",
        "infiltration_rate_mm_hr": 12.0,
    },
    {  # South Chennai (Adyar-Velachery belt) - clay loam
        "name": "south_clay_loam",
        "min_lat": 12.90, "max_lat": 13.00, "min_lng": 80.15, "max_lng": 80.27,
        "texture_class": "clay_loam",
        "infiltration_rate_mm_hr": 8.0,
    },
    {  # Western suburbs (Porur/Ambattur/Avadi) - inland clay
        "name": "west_inland_clay",
        "min_lat": 13.00, "max_lat": 13.15, "min_lng": 80.05, "max_lng": 80.18,
        "texture_class": "clay",
        "infiltration_rate_mm_hr": 5.0,
    },
    {  # Far south (Tambaram/Sholinganallur belt) - sandy loam
        "name": "far_south_sandy_loam",
        "min_lat": 12.80, "max_lat": 12.92, "min_lng": 80.05, "max_lng": 80.23,
        "texture_class": "sandy_loam",
        "infiltration_rate_mm_hr": 18.0,
    },
]

DEFAULT_ZONE = {
    "texture_class": "loam",
    "infiltration_rate_mm_hr": 10.0,
}


def lookup_soil_zone(lat: float, lng: float) -> dict:
    for zone in CHENNAI_SOIL_ZONES:
        if zone["min_lat"] <= lat <= zone["max_lat"] and zone["min_lng"] <= lng <= zone["max_lng"]:
            return {"texture_class": zone["texture_class"], "infiltration_rate_mm_hr": zone["infiltration_rate_mm_hr"]}
    return DEFAULT_ZONE
