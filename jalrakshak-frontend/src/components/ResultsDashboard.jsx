import { useState } from "react";
import HeaderSummary from "./HeaderSummary";
import PotentialGauge from "./PotentialGauge";
import StructureCard from "./StructureCard";
import GroundwaterChart from "./GroundwaterChart";
import CostCard from "./CostCard";
import WhatIfSliders from "./WhatIfSliders";
import { downloadReport } from "../lib/api";

export default function ResultsDashboard({ result, requestPayload, onWhatIf }) {
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState(null);

  async function handleDownload() {
    setDownloading(true);
    setDownloadError(null);
    try {
      const blob = await downloadReport(requestPayload);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "jalrakshak-report.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setDownloadError(err.message || "Could not generate the report.");
    } finally {
      setDownloading(false);
    }
  }

  return (
    <div className="space-y-5">
      <HeaderSummary location={result.location} rainfall={result.rainfall} />

      <div className="grid sm:grid-cols-2 gap-5">
        <div className="sm:col-span-2">
          <PotentialGauge
            low={result.harvesting_potential.annual_litres_low}
            p50={result.harvesting_potential.annual_litres_p50}
            high={result.harvesting_potential.annual_litres_high}
          />
        </div>
        <StructureCard structure={result.recommended_structure} />
        <GroundwaterChart groundwater={result.groundwater} />
        <CostCard cost={result.cost_estimate} />
        <WhatIfSliders
          roofArea={requestPayload.roof_area_sqm}
          openSpace={requestPayload.open_space_sqm}
          onChange={onWhatIf}
        />
      </div>

      <div>
        <button
          onClick={handleDownload}
          disabled={downloading}
          className="rounded-md border border-deep text-deep px-4 py-2.5 text-sm font-medium hover:bg-deep hover:text-white transition-colors disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-rain"
        >
          {downloading ? "Preparing PDF…" : "Download PDF report"}
        </button>
        {downloadError && <p className="text-xs text-amber mt-2">{downloadError}</p>}
      </div>
    </div>
  );
}
