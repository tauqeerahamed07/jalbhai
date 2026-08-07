const ROOF_TYPES = [
  { value: "concrete", label: "Concrete" },
  { value: "tiled", label: "Tiled" },
  { value: "metal_sheet", label: "Metal sheet" },
  { value: "asbestos", label: "Asbestos" },
];

export default function AssessForm({ form, setForm, onSubmit, disabled, hasPoint }) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
      className="space-y-4"
    >
      <div className="grid grid-cols-2 gap-4">
        <label className="block">
          <span className="text-xs font-medium text-inksoft uppercase tracking-wide">Roof type</span>
          <select
            value={form.roof_type}
            onChange={(e) => setForm((f) => ({ ...f, roof_type: e.target.value }))}
            className="mt-1 w-full rounded-md border border-line bg-card px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rain"
          >
            {ROOF_TYPES.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="text-xs font-medium text-inksoft uppercase tracking-wide">Roof area (sqm)</span>
          <input
            type="number"
            min="1"
            value={form.roof_area_sqm}
            onChange={(e) => setForm((f) => ({ ...f, roof_area_sqm: e.target.value }))}
            placeholder="Draw on map or enter manually"
            className="mt-1 w-full rounded-md border border-line bg-card px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-rain"
          />
        </label>

        <label className="block">
          <span className="text-xs font-medium text-inksoft uppercase tracking-wide">Open space available (sqm)</span>
          <input
            type="number"
            min="0"
            value={form.open_space_sqm}
            onChange={(e) => setForm((f) => ({ ...f, open_space_sqm: e.target.value }))}
            className="mt-1 w-full rounded-md border border-line bg-card px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-rain"
          />
        </label>

        <label className="block">
          <span className="text-xs font-medium text-inksoft uppercase tracking-wide">Number of dwellers (optional)</span>
          <input
            type="number"
            min="0"
            value={form.dwellers}
            onChange={(e) => setForm((f) => ({ ...f, dwellers: e.target.value }))}
            className="mt-1 w-full rounded-md border border-line bg-card px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-rain"
          />
        </label>
      </div>

      <button
        type="submit"
        disabled={disabled || !hasPoint || !form.roof_area_sqm}
        className="w-full rounded-md bg-rain px-4 py-3 font-display font-semibold text-white tracking-wide hover:bg-monsoon transition-colors disabled:opacity-40 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-rain"
      >
        {disabled ? "Assessing…" : "Assess"}
      </button>
      {!hasPoint && (
        <p className="text-xs text-amber">Set a location on the map above before assessing.</p>
      )}
    </form>
  );
}
