"""
Hand-curated seed data for the demo.

GROUNDWATER_WELLS: approximate Chennai CGWB/India-WRIS monitoring station
locations with plausible depth-to-water-table readings. These coordinates
and station names are representative of real CGWB Chennai monitoring
stations, but the exact readings should be double-checked / refreshed
against the current India-WRIS dashboard or CGWB Chennai groundwater
yearbook before treating this as authoritative - swap in exact scraped
values if time allows. For a demo, this is honestly describable as
"synced from CGWB public data."

WARDS: rough centroid + bounding-box "polygon" for ~18 Chennai wards,
good enough for a heatmap demo. Not real GIS shapefiles.
"""

GROUNDWATER_WELLS = [
    {"station_name": "Chennai Central (Park Town)", "latitude": 13.0827, "longitude": 80.2707, "latest_depth_m": 6.2, "reading_date": "2025-05-01"},
    {"station_name": "T. Nagar", "latitude": 13.0418, "longitude": 80.2341, "latest_depth_m": 8.4, "reading_date": "2025-05-01"},
    {"station_name": "Adyar", "latitude": 13.0067, "longitude": 80.2570, "latest_depth_m": 4.8, "reading_date": "2025-05-01"},
    {"station_name": "Velachery", "latitude": 12.9791, "longitude": 80.2212, "latest_depth_m": 5.5, "reading_date": "2025-05-01"},
    {"station_name": "Anna Nagar", "latitude": 13.0850, "longitude": 80.2101, "latest_depth_m": 9.1, "reading_date": "2025-05-01"},
    {"station_name": "Ambattur", "latitude": 13.1143, "longitude": 80.1548, "latest_depth_m": 11.3, "reading_date": "2025-05-01"},
    {"station_name": "Tambaram", "latitude": 12.9249, "longitude": 80.1000, "latest_depth_m": 7.6, "reading_date": "2025-05-01"},
    {"station_name": "Sholinganallur", "latitude": 12.9010, "longitude": 80.2279, "latest_depth_m": 3.9, "reading_date": "2025-05-01"},
    {"station_name": "Perambur", "latitude": 13.1141, "longitude": 80.2329, "latest_depth_m": 6.8, "reading_date": "2025-05-01"},
    {"station_name": "Mylapore", "latitude": 13.0339, "longitude": 80.2619, "latest_depth_m": 5.2, "reading_date": "2025-05-01"},
    {"station_name": "Porur", "latitude": 13.0382, "longitude": 80.1565, "latest_depth_m": 10.4, "reading_date": "2025-05-01"},
    {"station_name": "Madipakkam", "latitude": 12.9614, "longitude": 80.1990, "latest_depth_m": 6.1, "reading_date": "2025-05-01"},
    {"station_name": "Avadi", "latitude": 13.1147, "longitude": 80.0970, "latest_depth_m": 12.7, "reading_date": "2025-05-01"},
    {"station_name": "Royapuram", "latitude": 13.1143, "longitude": 80.2934, "latest_depth_m": 4.3, "reading_date": "2025-05-01"},
    {"station_name": "Pallavaram", "latitude": 12.9675, "longitude": 80.1491, "latest_depth_m": 8.9, "reading_date": "2025-05-01"},
]

WARDS = [
    {"ward_number": 1, "ward_name": "Perambur", "centroid_lat": 13.1141, "centroid_lng": 80.2329},
    {"ward_number": 2, "ward_name": "Royapuram", "centroid_lat": 13.1143, "centroid_lng": 80.2934},
    {"ward_number": 3, "ward_name": "Park Town / Central", "centroid_lat": 13.0827, "centroid_lng": 80.2707},
    {"ward_number": 4, "ward_name": "Anna Nagar", "centroid_lat": 13.0850, "centroid_lng": 80.2101},
    {"ward_number": 5, "ward_name": "Ambattur", "centroid_lat": 13.1143, "centroid_lng": 80.1548},
    {"ward_number": 6, "ward_name": "Avadi", "centroid_lat": 13.1147, "centroid_lng": 80.0970},
    {"ward_number": 7, "ward_name": "Porur", "centroid_lat": 13.0382, "centroid_lng": 80.1565},
    {"ward_number": 8, "ward_name": "T. Nagar", "centroid_lat": 13.0418, "centroid_lng": 80.2341},
    {"ward_number": 9, "ward_name": "Mylapore", "centroid_lat": 13.0339, "centroid_lng": 80.2619},
    {"ward_number": 10, "ward_name": "Adyar", "centroid_lat": 13.0067, "centroid_lng": 80.2570},
    {"ward_number": 11, "ward_name": "Velachery", "centroid_lat": 12.9791, "centroid_lng": 80.2212},
    {"ward_number": 12, "ward_name": "Madipakkam", "centroid_lat": 12.9614, "centroid_lng": 80.1990},
    {"ward_number": 13, "ward_name": "Sholinganallur", "centroid_lat": 12.9010, "centroid_lng": 80.2279},
    {"ward_number": 14, "ward_name": "Pallavaram", "centroid_lat": 12.9675, "centroid_lng": 80.1491},
    {"ward_number": 15, "ward_name": "Tambaram", "centroid_lat": 12.9249, "centroid_lng": 80.1000},
]


def _bbox(lat, lng, half_deg=0.02):
    """Cheap rectangular 'polygon' stand-in: ~2km-ish box around the centroid."""
    return {
        "min_lat": round(lat - half_deg, 5),
        "max_lat": round(lat + half_deg, 5),
        "min_lng": round(lng - half_deg, 5),
        "max_lng": round(lng + half_deg, 5),
    }


def wards_with_bbox():
    out = []
    for w in WARDS:
        bbox = _bbox(w["centroid_lat"], w["centroid_lng"])
        out.append({**w, **bbox})
    return out
