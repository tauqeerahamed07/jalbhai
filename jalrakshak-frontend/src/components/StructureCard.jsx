const CONFIDENCE_STYLES = {
  high: "bg-leaf/15 text-leaf",
  medium: "bg-amber/15 text-amber",
  low: "bg-inksoft/15 text-inksoft",
};

export default function StructureCard({ structure }) {
  const { label, dimensions, storage_capacity_litres, confidence } = structure;
  const { length_m, width_m, depth_m } = dimensions;

  // simple proportional cross-section box
  const boxW = 180;
  const boxH = Math.min(60 + depth_m * 18, 140);

  return (
    <div className="bg-card rounded-lg border border-line p-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-inksoft uppercase tracking-wide">Recommended structure</p>
          <p className="font-display text-2xl font-semibold text-ink mt-1">{label}</p>
        </div>
        <span className={`shrink-0 rounded-full px-2.5 py-1 text-[11px] font-medium uppercase tracking-wide ${CONFIDENCE_STYLES[confidence] || CONFIDENCE_STYLES.medium}`}>
          {confidence} confidence
        </span>
      </div>

      <div className="mt-5 flex flex-col sm:flex-row gap-5 items-center">
        <svg viewBox="0 0 260 170" className="w-full max-w-[220px]" role="img" aria-label={`Cross section of ${label}`}>
          {/* ground line */}
          <line x1="10" y1="30" x2="250" y2="30" stroke="#4c5d58" strokeWidth="1.5" />
          <line x1="0" y1="30" x2="10" y2="20" stroke="#4c5d58" strokeWidth="1" />
          <line x1="10" y1="30" x2="20" y2="20" stroke="#4c5d58" strokeWidth="1" />
          <line x1="20" y1="30" x2="30" y2="20" stroke="#4c5d58" strokeWidth="1" />

          {/* pit box */}
          <rect
            x={(260 - boxW) / 2}
            y="30"
            width={boxW}
            height={boxH}
            fill="#1f9db8"
            fillOpacity="0.12"
            stroke="#0e4749"
            strokeWidth="2"
          />
          {/* fill texture */}
          {Array.from({ length: 5 }).map((_, i) => (
            <line
              key={i}
              x1={(260 - boxW) / 2 + 8}
              y1={40 + i * ((boxH - 20) / 4)}
              x2={(260 - boxW) / 2 + boxW - 8}
              y2={40 + i * ((boxH - 20) / 4)}
              stroke="#0e4749"
              strokeOpacity="0.15"
              strokeWidth="1"
            />
          ))}

          {/* width dimension */}
          <line x1={(260 - boxW) / 2} y1={boxH + 42} x2={(260 - boxW) / 2 + boxW} y2={boxH + 42} stroke="#4c5d58" strokeWidth="1" />
          <text x="130" y={boxH + 56} textAnchor="middle" fontSize="11" fontFamily="IBM Plex Mono, monospace" fill="#4c5d58">
            {width_m} m
          </text>

          {/* depth dimension */}
          <line x1={(260 - boxW) / 2 - 12} y1="30" x2={(260 - boxW) / 2 - 12} y2={30 + boxH} stroke="#4c5d58" strokeWidth="1" />
          <text
            x={(260 - boxW) / 2 - 20}
            y={30 + boxH / 2}
            textAnchor="middle"
            fontSize="11"
            fontFamily="IBM Plex Mono, monospace"
            fill="#4c5d58"
            transform={`rotate(-90 ${(260 - boxW) / 2 - 20} ${30 + boxH / 2})`}
          >
            {depth_m} m
          </text>

          {/* length label */}
          <text x="130" y="16" textAnchor="middle" fontSize="11" fontFamily="IBM Plex Mono, monospace" fill="#4c5d58">
            L {length_m} m
          </text>
        </svg>

        <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm w-full">
          <div>
            <dt className="text-inksoft text-xs uppercase tracking-wide">Length × Width</dt>
            <dd className="font-mono">{length_m} × {width_m} m</dd>
          </div>
          <div>
            <dt className="text-inksoft text-xs uppercase tracking-wide">Depth</dt>
            <dd className="font-mono">{depth_m} m</dd>
          </div>
          <div className="col-span-2">
            <dt className="text-inksoft text-xs uppercase tracking-wide">Storage capacity</dt>
            <dd className="font-mono text-base font-medium text-deep">
              {new Intl.NumberFormat("en-IN").format(storage_capacity_litres)} L
            </dd>
          </div>
        </dl>
      </div>
    </div>
  );
}
