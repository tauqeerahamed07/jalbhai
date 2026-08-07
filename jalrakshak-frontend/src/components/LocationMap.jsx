import { useEffect, useRef, useState, useCallback } from "react";
import L from "leaflet";
import "leaflet-draw";
import * as turf from "@turf/turf";
import "../lib/leafletIcons";
import { CHENNAI_CENTER, CHENNAI_VIEWBOX } from "../lib/config";

export default function LocationMap({ onPointSet, onAreaComputed, drawEnabled, onToggleDraw }) {
  const mapElRef = useRef(null);
  const mapRef = useRef(null);
  const markerRef = useRef(null);
  const drawnLayerRef = useRef(null);
  const drawControlRef = useRef(null);

  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [point, setPoint] = useState(null);
  const onToggleDrawRef = useRef(onToggleDraw);
  onToggleDrawRef.current = onToggleDraw;

  const placePoint = useCallback(
    (lat, lng) => {
      const map = mapRef.current;
      if (!map) return;
      if (markerRef.current) map.removeLayer(markerRef.current);
      markerRef.current = L.marker([lat, lng]).addTo(map);
      map.setView([lat, lng], 16);
      setPoint({ lat, lng });
      onPointSet?.({ lat, lng });
    },
    [onPointSet]
  );

  // init map
  useEffect(() => {
    if (mapRef.current) return;
    const map = L.map(mapElRef.current, {
      center: CHENNAI_CENTER,
      zoom: 12,
      minZoom: 10,
      maxZoom: 19,
    });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);
    drawnLayerRef.current = drawnItems;

    map.on("click", (e) => {
      if (drawControlRef.current) return; // ignore plain clicks while drawing
      placePoint(e.latlng.lat, e.latlng.lng);
    });

    map.on(L.Draw.Event.CREATED, (e) => {
      drawnItems.clearLayers();
      drawnItems.addLayer(e.layer);
      const geojson = e.layer.toGeoJSON();
      const areaSqm = turf.area(geojson);
      onAreaComputed?.(Math.round(areaSqm));
      onToggleDrawRef.current?.(false);
    });

    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // toggle draw control
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    if (drawEnabled && !drawControlRef.current) {
      const control = new L.Control.Draw({
        draw: {
          polygon: {
            shapeOptions: { color: "#1f9db8", weight: 2, fillOpacity: 0.15 },
            allowIntersection: false,
            showArea: true,
          },
          polyline: false,
          rectangle: false,
          circle: false,
          circlemarker: false,
          marker: false,
        },
        edit: { featureGroup: drawnLayerRef.current, remove: true },
      });
      map.addControl(control);
      drawControlRef.current = control;
      // auto-start polygon draw
      new L.Draw.Polygon(map, control.options.draw.polygon).enable();
    } else if (!drawEnabled && drawControlRef.current) {
      map.removeControl(drawControlRef.current);
      drawControlRef.current = null;
    }
  }, [drawEnabled]);

  async function handleSearch(e) {
    e.preventDefault();
    if (!query.trim()) return;
    setSearching(true);
    setSearchResults([]);
    try {
      const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(
        query
      )}&format=json&bounded=1&viewbox=${CHENNAI_VIEWBOX}&limit=5`;
      const res = await fetch(url, { headers: { Accept: "application/json" } });
      const data = await res.json();
      setSearchResults(data);
      if (data.length === 1) {
        placePoint(parseFloat(data[0].lat), parseFloat(data[0].lon));
        setSearchResults([]);
      }
    } catch {
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  }

  function selectResult(r) {
    placePoint(parseFloat(r.lat), parseFloat(r.lon));
    setSearchResults([]);
    setQuery(r.display_name.split(",")[0]);
  }

  return (
    <div className="space-y-3">
      <form onSubmit={handleSearch} className="relative flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search an address or landmark in Chennai"
          className="w-full rounded-md border border-line bg-card px-3 py-2 text-sm font-body placeholder:text-inksoft/60 focus:outline-none focus:ring-2 focus:ring-rain"
        />
        <button
          type="submit"
          className="shrink-0 rounded-md bg-deep px-4 py-2 text-sm font-medium text-white hover:bg-ink transition-colors focus:outline-none focus:ring-2 focus:ring-rain"
        >
          {searching ? "…" : "Search"}
        </button>
        {searchResults.length > 0 && (
          <ul className="absolute top-full left-0 z-[1000] mt-1 w-full rounded-md border border-line bg-card shadow-lg max-h-48 overflow-auto">
            {searchResults.map((r) => (
              <li key={r.place_id}>
                <button
                  type="button"
                  onClick={() => selectResult(r)}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-paper border-b border-line last:border-0"
                >
                  {r.display_name}
                </button>
              </li>
            ))}
          </ul>
        )}
      </form>

      <div
        ref={mapElRef}
        className="h-72 sm:h-96 w-full rounded-md border border-line overflow-hidden"
        role="application"
        aria-label="Map for selecting the assessment site"
      />

      <div className="flex items-center justify-between gap-3 flex-wrap">
        <p className="text-xs text-inksoft font-mono">
          {point ? `${point.lat.toFixed(5)}, ${point.lng.toFixed(5)}` : "Click the map or search to set a location"}
        </p>
        <button
          type="button"
          disabled={!point}
          onClick={() => onToggleDraw(!drawEnabled)}
          className="rounded-md border border-deep text-deep disabled:opacity-40 disabled:cursor-not-allowed px-3 py-1.5 text-sm font-medium hover:bg-deep hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-rain"
        >
          {drawEnabled ? "Finish drawing roof" : "Draw your roof"}
        </button>
      </div>
    </div>
  );
}
