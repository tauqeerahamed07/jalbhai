"""
Thin async clients for the three free, no-key APIs this project depends on.
Every function degrades gracefully (falls back / returns a sane default)
rather than raising, so a flaky third-party API never 500s /api/assess.
"""

import httpx
import logging
from datetime import date, timedelta

from app.soil_fallback import lookup_soil_zone

logger = logging.getLogger("jalrakshak.external_apis")

OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
SOILGRIDS_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"
OPENTOPODATA_URL = "https://api.opentopodata.org/v1/srtm30m"

TIMEOUT = httpx.Timeout(8.0, connect=4.0)


async def get_rainfall(lat: float, lng: float) -> dict:
    """
    Pull ~1 year of historical daily rainfall from Open-Meteo's archive API
    and bucket it into monthly totals + an annual total. Falls back to a
    plausible Chennai rainfall climatology if the API is unreachable.
    """
    end = date.today() - timedelta(days=2)  # archive API needs a couple days' lag
    start = end - timedelta(days=365)
    params = {
        "latitude": lat,
        "longitude": lng,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": "precipitation_sum",
        "timezone": "Asia/Kolkata",
    }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(OPEN_METEO_ARCHIVE, params=params)
            resp.raise_for_status()
            data = resp.json()

        dates = data["daily"]["time"]
        precip = data["daily"]["precipitation_sum"]
        monthly = {}
        for d, p in zip(dates, precip):
            month_key = d[5:7]  # "01".."12"
            monthly[month_key] = monthly.get(month_key, 0.0) + (p or 0.0)

        month_names = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
        monthly_named = {month_names[int(k) - 1]: round(v, 1) for k, v in sorted(monthly.items())}
        annual_total = round(sum(monthly_named.values()), 1)

        return {"annual_total_mm": annual_total, "monthly_mm": monthly_named, "data_source": "Open-Meteo (historical archive)"}

    except Exception as e:
        logger.warning(f"Open-Meteo archive lookup failed, using climatology fallback: {e}")
        # Rough Chennai long-term monthly climatology (mm), NE monsoon-heavy.
        fallback_monthly = {
            "jan": 20, "feb": 8, "mar": 10, "apr": 22, "may": 48, "jun": 55,
            "jul": 85, "aug": 115, "sep": 125, "oct": 275, "nov": 320, "dec": 155,
        }
        return {
            "annual_total_mm": float(sum(fallback_monthly.values())),
            "monthly_mm": fallback_monthly,
            "data_source": "Chennai climatology fallback (Open-Meteo unreachable)",
        }


async def get_soil(lat: float, lng: float) -> dict:
    """
    Try SoilGrids for a texture/infiltration proxy; fall back to the
    hardcoded Chennai soil-zone lookup table if it's slow, errors, or
    the response shape isn't what we expect.
    """
    params = {
        "lon": lng,
        "lat": lat,
        "property": "clay",
        "depth": "0-5cm",
        "value": "mean",
    }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(SOILGRIDS_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        clay_pct = (
            data["properties"]["layers"][0]["depths"][0]["values"]["mean"] / 10.0
        )  # SoilGrids returns g/kg *10; /10 -> approx %

        if clay_pct >= 35:
            texture, infil = "clay", 5.0
        elif clay_pct >= 20:
            texture, infil = "clay_loam", 9.0
        elif clay_pct >= 10:
            texture, infil = "loam", 14.0
        else:
            texture, infil = "sandy_loam", 22.0

        return {"texture_class": texture, "infiltration_rate_mm_hr": infil, "data_source": "SoilGrids"}

    except Exception as e:
        logger.warning(f"SoilGrids lookup failed, using Chennai zone fallback: {e}")
        zone = lookup_soil_zone(lat, lng)
        return {**zone, "data_source": "Chennai soil zone fallback table"}


async def get_elevation(lat: float, lng: float) -> dict:
    """OpenTopoData SRTM 30m elevation lookup, with a flat default fallback."""
    params = {"locations": f"{lat},{lng}"}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(OPENTOPODATA_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
        elevation = data["results"][0]["elevation"]
        return {"elevation_m": float(elevation), "data_source": "OpenTopoData (SRTM 30m)"}
    except Exception as e:
        logger.warning(f"OpenTopoData lookup failed, using flat Chennai default: {e}")
        return {"elevation_m": 6.0, "data_source": "Chennai average elevation fallback (~6m)"}
