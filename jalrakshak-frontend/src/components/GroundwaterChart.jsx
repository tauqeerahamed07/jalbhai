import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function GroundwaterChart({ groundwater }) {
  const { nearest_well, trend } = groundwater;
  const data = trend.map((t) => ({ year: t.date.slice(0, 4), depth: t.depth_m }));

  return (
    <div className="bg-card rounded-lg border border-line p-6">
      <p className="text-xs font-medium text-inksoft uppercase tracking-wide">Groundwater trend</p>
      <p className="text-sm text-ink mt-1">
        Nearest well: <span className="font-medium">{nearest_well.name}</span>{" "}
        <span className="text-inksoft font-mono">({nearest_well.distance_km} km away)</span>
      </p>

      <div className="h-56 mt-4 -ml-2">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 12, bottom: 0, left: 0 }}>
            <CartesianGrid stroke="#d9e3dd" vertical={false} />
            <XAxis dataKey="year" tick={{ fontSize: 11, fontFamily: "IBM Plex Mono, monospace", fill: "#4c5d58" }} axisLine={{ stroke: "#d9e3dd" }} tickLine={false} />
            <YAxis
              reversed
              tick={{ fontSize: 11, fontFamily: "IBM Plex Mono, monospace", fill: "#4c5d58" }}
              axisLine={false}
              tickLine={false}
              label={{ value: "Depth (m)", angle: -90, position: "insideLeft", fontSize: 11, fill: "#4c5d58" }}
            />
            <Tooltip
              formatter={(v) => [`${v} m`, "Depth to water"]}
              contentStyle={{ fontFamily: "Inter, sans-serif", fontSize: 12, borderRadius: 6, borderColor: "#d9e3dd" }}
            />
            <Line type="monotone" dataKey="depth" stroke="#0e4749" strokeWidth={2} dot={{ r: 3, fill: "#1f9db8" }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="text-[11px] text-inksoft/70 mt-1">Depth to water table, lower on the axis = closer to surface.</p>
    </div>
  );
}
