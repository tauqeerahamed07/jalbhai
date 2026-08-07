import { API_BASE_URL, USE_MOCK } from "./config";
import { mockAssess, mockHeatmap, mockReportBlob } from "./mockAssess";

// ---- Contract ----------------------------------------------------------
// POST /api/assess
//   body: { lat, lng, roof_area_sqm, open_space_sqm, roof_type, dwellers? }
//   -> {
//        location: { ward, district, lat, lng },
//        rainfall: { annual_mm },
//        harvesting_potential: { annual_litres_p50, annual_litres_low, annual_litres_high },
//        recommended_structure: { type, label, dimensions:{length_m,width_m,depth_m},
//                                  storage_capacity_litres, confidence },
//        groundwater: { nearest_well: { name, distance_km }, trend: [{date, depth_m}] },
//        cost_estimate: { total_cost_inr, payback_period_years }
//      }
// GET /api/wards/heatmap
//   -> [{ ward_id, ward_name, score(0-1), centroid:{lat,lng}, polygon:[[lat,lng],...] }]
// POST /api/report  (same body as /api/assess) -> PDF file blob
// -------------------------------------------------------------------------

export async function assess(payload) {
  if (USE_MOCK) return mockAssess(payload);
  const res = await fetch(`${API_BASE_URL}/api/assess`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Assessment failed (${res.status})`);
  return res.json();
}

export async function fetchHeatmap() {
  if (USE_MOCK) return mockHeatmap();
  const res = await fetch(`${API_BASE_URL}/api/wards/heatmap`);
  if (!res.ok) throw new Error(`Heatmap fetch failed (${res.status})`);
  return res.json();
}

export async function downloadReport(payload) {
  if (USE_MOCK) return mockReportBlob(payload);
  const res = await fetch(`${API_BASE_URL}/api/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Report generation failed (${res.status})`);
  return res.blob();
}
