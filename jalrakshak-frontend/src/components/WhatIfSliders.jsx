import { useEffect, useRef, useState } from "react";

export default function WhatIfSliders({ roofArea, openSpace, onChange }) {
  const [local, setLocal] = useState({ roof_area_sqm: roofArea, open_space_sqm: openSpace });
  const timer = useRef(null);

  useEffect(() => {
    setLocal({ roof_area_sqm: roofArea, open_space_sqm: openSpace });
  }, [roofArea, openSpace]);

  function update(next) {
    setLocal(next);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => onChange(next), 500);
  }

  return (
    <div className="bg-card rounded-lg border border-line p-6">
      <p className="text-xs font-medium text-inksoft uppercase tracking-wide mb-4">What if…</p>

      <div className="space-y-5">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-inksoft">Roof area</span>
            <span className="font-mono font-medium">{local.roof_area_sqm} sqm</span>
          </div>
          <input
            type="range"
            min="10"
            max="500"
            value={local.roof_area_sqm}
            onChange={(e) => update({ ...local, roof_area_sqm: Number(e.target.value) })}
            className="w-full accent-rain"
          />
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-inksoft">Open space available</span>
            <span className="font-mono font-medium">{local.open_space_sqm} sqm</span>
          </div>
          <input
            type="range"
            min="0"
            max="200"
            value={local.open_space_sqm}
            onChange={(e) => update({ ...local, open_space_sqm: Number(e.target.value) })}
            className="w-full accent-rain"
          />
        </div>
      </div>
      <p className="text-[11px] text-inksoft/70 mt-3">Results update automatically as you drag.</p>
    </div>
  );
}
