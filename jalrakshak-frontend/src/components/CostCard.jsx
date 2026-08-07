function inr(n) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);
}

export default function CostCard({ cost }) {
  return (
    <div className="bg-card rounded-lg border border-line p-6">
      <p className="text-xs font-medium text-inksoft uppercase tracking-wide">Cost &amp; payback</p>
      <div className="mt-3 grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-inksoft">Estimated cost</p>
          <p className="font-display text-2xl font-semibold text-ink font-mono">{inr(cost.total_cost_inr)}</p>
        </div>
        <div>
          <p className="text-xs text-inksoft">Payback period</p>
          <p className="font-display text-2xl font-semibold text-leaf font-mono">{cost.payback_period_years} yrs</p>
        </div>
      </div>
    </div>
  );
}
