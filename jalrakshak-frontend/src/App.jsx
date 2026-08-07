import { useState, useCallback } from "react";
import LocationMap from "./components/LocationMap";
import AssessForm from "./components/AssessForm";
import ResultsDashboard from "./components/ResultsDashboard";
import HeatmapView from "./components/HeatmapView";
import { assess } from "./lib/api";

const initialForm = {
  roof_type: "concrete",
  roof_area_sqm: "",
  open_space_sqm: "",
  dwellers: "",
};

export default function App() {
  const [tab, setTab] = useState("assess");
  const [point, setPoint] = useState(null);
  const [drawEnabled, setDrawEnabled] = useState(false);
  const [form, setForm] = useState(initialForm);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [lastPayload, setLastPayload] = useState(null);

  const buildPayload = useCallback(
    (overrides = {}) => ({
      lat: point?.lat,
      lng: point?.lng,
      roof_type: form.roof_type,
      roof_area_sqm: Number(overrides.roof_area_sqm ?? form.roof_area_sqm) || 0,
      open_space_sqm: Number(overrides.open_space_sqm ?? form.open_space_sqm) || 0,
      dwellers: form.dwellers ? Number(form.dwellers) : undefined,
    }),
    [point, form]
  );

  async function runAssess(overrides = {}) {
    if (!point) return;
    const payload = buildPayload(overrides);
    setLoading(true);
    setError(null);
    try {
      const data = await assess(payload);
      setResult(data);
      setLastPayload(payload);
    } catch (err) {
      setError(err.message || "Couldn't reach the assessment service. Check your connection and try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleWhatIf(next) {
    setForm((f) => ({ ...f, roof_area_sqm: next.roof_area_sqm, open_space_sqm: next.open_space_sqm }));
    runAssess(next);
  }

  return (
    <div className="min-h-screen bg-paper">
      <header className="border-b border-line bg-card">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-5 flex items-center justify-between">
          <div>
            <p className="font-display text-xl font-bold text-deep tracking-tight">JalRakshak</p>
            <p className="text-xs text-inksoft">Rooftop Rainwater Harvesting &amp; Recharge Assessment · Chennai</p>
          </div>
          <nav className="flex gap-1 bg-paper rounded-md p-1 border border-line">
            <button
              onClick={() => setTab("assess")}
              className={`px-3 py-1.5 text-sm rounded-md font-medium transition-colors ${
                tab === "assess" ? "bg-deep text-white" : "text-inksoft hover:text-ink"
              }`}
            >
              Assess
            </button>
            <button
              onClick={() => setTab("heatmap")}
              className={`px-3 py-1.5 text-sm rounded-md font-medium transition-colors ${
                tab === "heatmap" ? "bg-deep text-white" : "text-inksoft hover:text-ink"
              }`}
            >
              Ward heatmap
            </button>
          </nav>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {tab === "assess" ? (
          <div className="grid lg:grid-cols-2 gap-8">
            <section className="space-y-6">
              <div>
                <h2 className="font-display text-sm font-semibold uppercase tracking-wide text-inksoft mb-3">
                  1. Locate the site
                </h2>
                <LocationMap
                  onPointSet={setPoint}
                  onAreaComputed={(sqm) => setForm((f) => ({ ...f, roof_area_sqm: sqm }))}
                  drawEnabled={drawEnabled}
                  onToggleDraw={setDrawEnabled}
                />
              </div>
              <div className="tick-rule" />
              <div>
                <h2 className="font-display text-sm font-semibold uppercase tracking-wide text-inksoft mb-3">
                  2. Roof &amp; site details
                </h2>
                <AssessForm
                  form={form}
                  setForm={setForm}
                  onSubmit={() => runAssess()}
                  disabled={loading}
                  hasPoint={!!point}
                />
                {error && (
                  <div className="mt-4 rounded-md border border-amber/40 bg-amber/10 px-4 py-3 text-sm text-amber">
                    {error}
                  </div>
                )}
              </div>
            </section>

            <section>
              <h2 className="font-display text-sm font-semibold uppercase tracking-wide text-inksoft mb-3">
                3. Results
              </h2>
              {loading && !result && (
                <div className="rounded-lg border border-line bg-card p-10 text-center">
                  <p className="text-sm text-inksoft font-mono">Running assessment…</p>
                </div>
              )}
              {!loading && !result && !error && (
                <div className="rounded-lg border border-dashed border-line p-10 text-center">
                  <p className="text-sm text-inksoft">
                    Set a location, fill in roof details, and press Assess to see the harvesting potential for this
                    site.
                  </p>
                </div>
              )}
              {result && lastPayload && (
                <ResultsDashboard result={result} requestPayload={lastPayload} onWhatIf={handleWhatIf} />
              )}
            </section>
          </div>
        ) : (
          <div>
            <h2 className="font-display text-sm font-semibold uppercase tracking-wide text-inksoft mb-3">
              Ward-level potential
            </h2>
            <HeatmapView
              onWardSelect={(w) => {
                setPoint({ lat: w.centroid.lat, lng: w.centroid.lng });
                setTab("assess");
              }}
            />
          </div>
        )}
      </main>

      <footer className="max-w-5xl mx-auto px-4 sm:px-6 pb-8">
        <p className="text-[11px] text-inksoft/60">
          Estimates are indicative, based on rainfall and soil data, and should be verified by a site survey.
        </p>
      </footer>
    </div>
  );
}
