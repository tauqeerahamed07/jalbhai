export default function HeaderSummary({ location, rainfall }) {
  return (
    <div className="bg-deep text-white rounded-lg p-6 flex flex-wrap items-center justify-between gap-4">
      <div>
        <p className="text-xs uppercase tracking-wide text-white/60">Site</p>
        <p className="font-display text-xl font-semibold mt-0.5">{location.ward}</p>
        <p className="text-sm text-white/70">{location.district}</p>
      </div>
      <div className="text-right">
        <p className="text-xs uppercase tracking-wide text-white/60">Annual rainfall</p>
        <p className="font-display text-3xl font-bold mt-0.5">{rainfall.annual_mm} <span className="text-base font-medium text-white/70">mm</span></p>
      </div>
    </div>
  );
}
