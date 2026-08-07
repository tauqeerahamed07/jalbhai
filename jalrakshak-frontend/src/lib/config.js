// Swap USE_MOCK to false and set API_BASE_URL to the deployed backend
// at integration time — that's the only change needed.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
export const USE_MOCK = (import.meta.env.VITE_USE_MOCK ?? "true") === "true";

export const CHENNAI_CENTER = [13.0827, 80.2707];
// Rough bounding box for the Chennai metro area (south, west, north, east)
export const CHENNAI_BOUNDS = {
  south: 12.83,
  west: 79.97,
  north: 13.28,
  east: 80.34,
};
export const CHENNAI_VIEWBOX = `${CHENNAI_BOUNDS.west},${CHENNAI_BOUNDS.north},${CHENNAI_BOUNDS.east},${CHENNAI_BOUNDS.south}`;
