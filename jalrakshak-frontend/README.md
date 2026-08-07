# JalRakshak — frontend

Rooftop Rainwater Harvesting & Artificial Recharge assessment tool for Chennai.

## Run it

```bash
npm install
npm run dev
```

Runs against **mock data** by default (`VITE_USE_MOCK=true`), simulating a 400ms API delay so
loading states are visible.

## Swap in the real backend

Copy `.env.example` to `.env` and set:

```
VITE_API_BASE_URL=https://your-deployed-backend
VITE_USE_MOCK=false
```

That's the only change needed — `src/lib/api.js` handles the rest. The exact request/response
shape both modes agree on is documented at the top of that file.

## Structure

- `src/lib/api.js` — mock/real fetch switch, the API contract
- `src/lib/mockAssess.js` — deterministic mock responses (`/api/assess`, `/api/wards/heatmap`, `/api/report`)
- `src/components/LocationMap.jsx` — Nominatim search, click-to-pin, `leaflet-draw` roof polygon → Turf.js area
- `src/components/AssessForm.jsx` — roof type / open space / dwellers inputs
- `src/components/ResultsDashboard.jsx` — composes the results cards + PDF download
- `src/components/PotentialGauge.jsx`, `StructureCard.jsx`, `GroundwaterChart.jsx`, `CostCard.jsx`, `WhatIfSliders.jsx` — result cards
- `src/components/HeatmapView.jsx` — ward-level potential heatmap tab

## Design

Civic/instrument aesthetic — deep teal + rain-blue on a cool off-white, Space Grotesk for
headline numbers and data, Inter for body/UI, IBM Plex Mono for coordinates and dimensions.
Recurring motif: dimension-line ticks and a graduated "rain gauge" bar for the headline litres
number, and blueprint-style SVG cross-sections for the recommended structure — reads as a field
survey instrument rather than a generic dashboard.
