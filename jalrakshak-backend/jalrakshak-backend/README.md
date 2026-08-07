# JalRakshak Backend

RTRWH/AR assessment API for Chennai, India. FastAPI + Postgres.

## Quick start

```bash
pip install -r requirements.txt --break-system-packages   # or use a venv
cp .env.example .env
# edit .env -> set DATABASE_URL to your Supabase or Neon Postgres connection string
uvicorn main:app --reload
```

Server comes up on `http://localhost:8000`. Interactive docs at `/docs`.
On first boot it auto-creates tables and seeds the groundwater-well and
ward tables if they're empty — no manual migration step needed.

**Tested in this sandbox:** all three endpoints run end-to-end against a
local SQLite fallback DB (outbound calls to the real free APIs are blocked
in *this* sandbox, so I verified the fallback paths — climatology, soil
zone table, flat elevation — fire correctly and the response still comes
back well-formed). Point `DATABASE_URL` at real Postgres and it should
behave identically, just with live Open-Meteo/SoilGrids/OpenTopoData data
where reachable.

**One fix worth knowing about:** WeasyPrint 62.3 pulls in a newer `pydyf`
by default that breaks PDF rendering (`AttributeError: 'super' object has
no attribute 'transform'`). `requirements.txt` pins `pydyf==0.11.0` to fix
this — don't `pip install --upgrade` weasyprint/pydyf independently.

## What's real vs. hardcoded (be upfront about this at demo time)

| Data | Source | Fallback trigger |
|---|---|---|
| Rainfall | Live Open-Meteo archive API call | Chennai monthly climatology if API errors/unreachable |
| Soil | Live SoilGrids call (clay % -> texture bucket) | 6-zone hardcoded Chennai bounding-box table |
| Groundwater | **Always** a seeded 15-row table of approximate CGWB station coords + one depth reading each, nearest by haversine | n/a — this was intentionally never wired to a live India-WRIS scrape per the build plan |
| Elevation | Live OpenTopoData call | Flat 6m Chennai-average default |
| Ward heatmap | 15 hardcoded ward centroids + crude ~2km bounding boxes (not real polygons), scored via `ml.cluster_score()` | n/a |

Every `/api/assess` response includes a `notes` array that tells you, per
response, which of the above fell back — surface that in the UI so it's
transparent rather than silently wrong.

⚠️ The groundwater well coordinates/readings are representative
placeholders, not verified against a live CGWB export — swap in the real
scraped values before treating any specific depth reading as accurate.

## API contract

### `POST /api/assess`

Request:
```json
{
  "latitude": 13.0067,
  "longitude": 80.2570,
  "roof_area_sqm": 120,
  "roof_type": "concrete",        // concrete | tiled | metal_sheet | asbestos
  "open_space_type": "small_yard",// none | small_yard | linear_strip | large_open_area
  "open_space_area_sqm": 10,
  "dwellers": 5,                  // optional
  "address_label": "Adyar, Chennai" // optional, echoed back for display
}
```

Response: see `app/schemas.py::AssessResponse` — includes `rainfall`,
`soil`, `groundwater`, `elevation`, `volume_estimate` (deterministic +
ML P10/P50/P90 + confidence), `structure_recommendation`,
`feasibility_classification`, and `notes`.

### `GET /api/wards/heatmap`

No params. Returns `{"wards": [...]}`, one entry per ward with centroid,
bounding box, and a 0–100 `score` (+ `score_label`: high/medium/low).

### `POST /api/report`

Request body: `{"assessment": <the full AssessResponse object>}` — i.e.
call `/api/assess` first, then pass its exact response straight into
`/api/report`. Returns a PDF file (`application/pdf`, streamed).

## Swapping in the real ML model (Person C)

Everything routes through `app/ml.py`. Replace the **bodies** of
`predict(features)` and `cluster_score(ward_features)` with real model
calls — keep the signatures and return shapes exactly as documented in
that file's docstrings, and nothing else in the codebase needs to change.
Flip `USE_REAL_ML=true` in `.env` once it's wired in (the stub raises
`NotImplementedError` if that flag is on but you haven't filled in the
real logic yet, so it's obvious if the flag gets flipped too early).

## Priority order this was built in (per the build plan)

1. `/api/assess` returning correct JSON shape with rainfall + fallback
   soil/groundwater + deterministic calc (safety net — works with zero
   ML). ✅ done, tested.
2. `/api/wards/heatmap` with hardcoded wards + formula/ML score. ✅ done.
3. `/api/report` PDF generation. ✅ done, tested, sample PDF renders cleanly.

## Explicitly skipped (per scope)

No auth, no request logging/analytics, no rate limiting, no Docker. Run
directly with `uvicorn`. CORS is wide open (`allow_origins=["*"]`) so
Person A's frontend can hit this from anywhere during the demo.

## Optional: scheduled Open-Meteo sync

Not implemented — per the build plan this is a "nice to have if time
allows." Calling Open-Meteo live per-request (with fallback) is what's
built. If you want to add it: `apscheduler` is already in
`requirements.txt`, unused — a job that re-pulls rainfall for the 15 ward
centroids every N hours and caches results would be the natural addition,
purely as a latency/rate-limit optimization for `/api/wards/heatmap`.
