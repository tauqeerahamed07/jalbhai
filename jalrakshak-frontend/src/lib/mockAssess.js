// Mock implementations — remove or ignore once the real backend is live.
// Feature-flagged via VITE_USE_MOCK in config.js.

const WARDS = [
  { ward: "Ward 118 – Adyar", district: "Chennai", rain: 1380 },
  { ward: "Ward 65 – T. Nagar", district: "Chennai", rain: 1340 },
  { ward: "Ward 142 – Velachery", district: "Chennai", rain: 1290 },
  { ward: "Ward 23 – Perambur", district: "Chennai", rain: 1410 },
  { ward: "Ward 88 – Mylapore", district: "Chennai", rain: 1360 },
];

const ROOF_RUNOFF_COEFF = {
  concrete: 0.85,
  tiled: 0.75,
  metal_sheet: 0.9,
  asbestos: 0.8,
};

const WELL_NAMES = [
  "Adyar PWD Piezometer",
  "Velachery Observation Well",
  "Guindy CGWB Well",
  "Perambur Monitoring Well",
];

function pick(arr, seed) {
  return arr[Math.floor(seed) % arr.length];
}

function seedFrom(payload) {
  const s = `${payload.lat},${payload.lng},${payload.roof_area_sqm}`;
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return h;
}

export function mockAssess(payload) {
  const delay = 400;
  return new Promise((resolve) => {
    setTimeout(() => {
      const seed = seedFrom(payload);
      const rng = () => {
        // simple deterministic pseudo-random from seed, mutated
        const x = Math.sin(seed + resolve.__t || 0) * 10000;
        return x - Math.floor(x);
      };

      const wardInfo = pick(WARDS, seed);
      const roofArea = Number(payload.roof_area_sqm) || 80;
      const openSpace = Number(payload.open_space_sqm) || 20;
      const coeff = ROOF_RUNOFF_COEFF[payload.roof_type] || 0.8;
      const rainfall = wardInfo.rain + (seed % 40) - 20;

      const p50 = Math.round(roofArea * (rainfall / 1000) * coeff * 1000);
      const low = Math.round(p50 * 0.82);
      const high = Math.round(p50 * 1.18);

      const capableForPit = openSpace >= 10;
      const structureType = capableForPit ? "recharge_pit" : "recharge_shaft";
      const label = capableForPit ? "Recharge Pit" : "Recharge Shaft";
      const depth = capableForPit ? 2.5 : 6;
      const length = capableForPit ? Math.min(2 + openSpace / 40, 3.5) : 1;
      const width = capableForPit ? Math.min(1.5 + openSpace / 60, 2.5) : 1;
      const storageCapacity = Math.round(length * width * depth * 1000 * 0.35);

      const trend = Array.from({ length: 8 }).map((_, i) => {
        const year = 2018 + i;
        const base = 8.5 + (seed % 10) * 0.3;
        const depthM = +(base - i * 0.15 + Math.sin(i + seed) * 0.3).toFixed(2);
        return { date: `${year}-06-01`, depth_m: Math.max(depthM, 2) };
      });

      const costPerLitreCapacity = 3.2;
      const totalCost = Math.round(15000 + storageCapacity * costPerLitreCapacity);
      const waterTariffSavingPerYear = Math.round(p50 * 0.00006 * 1000 * 12) / 12 + p50 * 0.00004;
      const annualSaving = Math.max(Math.round(p50 * 0.00005), 800);
      const payback = +(totalCost / annualSaving).toFixed(1);

      resolve({
        location: {
          ward: wardInfo.ward,
          district: wardInfo.district,
          lat: payload.lat,
          lng: payload.lng,
        },
        rainfall: { annual_mm: rainfall },
        harvesting_potential: {
          annual_litres_p50: p50,
          annual_litres_low: low,
          annual_litres_high: high,
        },
        recommended_structure: {
          type: structureType,
          label,
          dimensions: {
            length_m: +length.toFixed(1),
            width_m: +width.toFixed(1),
            depth_m: +depth.toFixed(1),
          },
          storage_capacity_litres: storageCapacity,
          confidence: openSpace >= 15 ? "high" : openSpace >= 8 ? "medium" : "low",
        },
        groundwater: {
          nearest_well: {
            name: pick(WELL_NAMES, seed),
            distance_km: +(0.4 + (seed % 30) / 10).toFixed(1),
          },
          trend,
        },
        cost_estimate: {
          total_cost_inr: totalCost,
          payback_period_years: payback,
        },
      });
    }, delay);
  });
}

export function mockHeatmap() {
  return new Promise((resolve) => {
    setTimeout(() => {
      const base = [13.06, 80.24];
      const wards = WARDS.map((w, i) => {
        const cLat = base[0] + (i - 2) * 0.045 + (i % 2 === 0 ? 0.01 : -0.01);
        const cLng = base[1] + (i - 2) * 0.04;
        const score = +((i * 37 + 20) % 100 / 100).toFixed(2);
        const polygon = [
          [cLat - 0.018, cLng - 0.02],
          [cLat - 0.018, cLng + 0.02],
          [cLat + 0.018, cLng + 0.02],
          [cLat + 0.018, cLng - 0.02],
        ];
        return {
          ward_id: `W${i + 1}`,
          ward_name: w.ward,
          score,
          centroid: { lat: cLat, lng: cLng },
          polygon,
        };
      });
      resolve(wards);
    }, 400);
  });
}

export function mockReportBlob() {
  return new Promise((resolve) => {
    setTimeout(() => {
      const text =
        "JalRakshak Assessment Report\n\nThis is a placeholder report generated in mock mode.\nConnect the real backend to receive a formatted PDF.";
      resolve(new Blob([text], { type: "application/pdf" }));
    }, 400);
  });
}
