import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "../lib/leafletIcons";
import { fetchHeatmap } from "../lib/api";
import { CHENNAI_CENTER } from "../lib/config";

// light -> dark teal ramp for low -> high potential
function colorForScore(score) {
  const stops = [
    { s: 0, c: [232, 240, 236] },
    { s: 0.5, c: [79, 157, 179] },
    { s: 1, c: [11, 32, 28] },
  ];
  let a = stops[0], b = stops[stops.length - 1];
  for (let i = 0; i < stops.length - 1; i++) {
    if (score >= stops[i].s && score <= stops[i + 1].s) {
      a = stops[i];
      b = stops[i + 1];
      break;
    }
  }
  const t = (score - a.s) / (b.s - a.s || 1);
  const c = a.c.map((v, i) => Math.round(v + (b.c[i] - v) * t));
  return `rgb(${c[0]},${c[1]},${c[2]})`;
}

export default function HeatmapView({ onWardSelect }) {
  const elRef = useRef(null);
  const mapRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const map = L.map(elRef.current, { center: CHENNAI_CENTER, zoom: 11 });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);
    mapRef.current = map;

    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchHeatmap()
      .then((wards) => {
        if (cancelled) return;
        wards.forEach((w) => {
          const latlngs = w.polygon.map(([lat, lng]) => [lat, lng]);
          const poly = L.polygon(latlngs, {
            color: "#0e4749",
            weight: 1,
            fillColor: colorForScore(w.score),
            fillOpacity: 0.75,
          }).addTo(map);
          poly.bindTooltip(`${w.ward_name} — score ${w.score}`, { sticky: true });
          poly.on("click", () => onWardSelect?.(w));
        });
      })
      .catch((err) => !cancelled && setError(err.message || "Could not load the heatmap."))
      .finally(() => !cancelled && setLoading(false));

    return () => {
      cancelled = true;
      map.remove();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-3">
      <div className="relative">
        <div ref={elRef} className="h-[28rem] w-full rounded-md border border-line overflow-hidden" />
        {loading && (
          <div className="absolute inset-0 bg-paper/80 flex items-center justify-center rounded-md">
            <p className="text-sm text-inksoft font-mono">Loading ward data…</p>
          </div>
        )}
        {error && !loading && (
          <div className="absolute inset-0 bg-paper/90 flex items-center justify-center rounded-md">
            <p className="text-sm text-amber font-medium">{error}</p>
          </div>
        )}
      </div>

      <div className="flex items-center gap-3">
        <span className="text-xs text-inksoft">Low potential</span>
        <div className="h-2 flex-1 max-w-xs rounded-full" style={{ background: "linear-gradient(90deg, #e8f0ec, #4f9db3, #0b201c)" }} />
        <span className="text-xs text-inksoft">High potential</span>
      </div>
    </div>
  );
}
