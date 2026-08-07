function fmt(n) {
  return new Intl.NumberFormat("en-IN").format(Math.round(n));
}

export default function PotentialGauge({ low, p50, high }) {
  const min = low * 0.9;
  const max = high * 1.1;
  const pct = (v) => ((v - min) / (max - min)) * 100;

  return (
    <div className="bg-card rounded-lg border border-line p-6">
      <p className="text-xs font-medium text-inksoft uppercase tracking-wide">Annual harvesting potential</p>
      <p className="font-display text-5xl sm:text-6xl font-bold text-deep mt-1 leading-none">
        {fmt(p50)} <span className="text-2xl font-medium text-inksoft align-top">L</span>
      </p>
      <p className="text-sm text-inksoft mt-2 font-mono">
        {fmt(low)} – {fmt(high)} L depending on rainfall year
      </p>

      {/* Graduated gauge bar — like a rain gauge / measuring cylinder */}
      <div className="mt-5 relative">
        <div className="h-3 rounded-full bg-gradient-to-r from-rain/20 via-rain/50 to-rain w-full relative overflow-hidden">
          <div
            className="absolute top-0 bottom-0 bg-deep/80"
            style={{ left: `${pct(low)}%`, width: `${pct(high) - pct(low)}%` }}
          />
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-ink"
            style={{ left: `${pct(p50)}%` }}
            aria-hidden
          />
        </div>
        <div className="flex justify-between mt-1.5 text-[10px] font-mono text-inksoft/70">
          <span>{fmt(min)} L</span>
          <span>{fmt(max)} L</span>
        </div>
      </div>
    </div>
  );
}
