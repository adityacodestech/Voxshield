function ThreatIntelligence({ history }) {
  const width = 700
  const height = 240
  const padding = 30

  const maxValue = 100
  const minValue = 0

  const points = history
    .map((value, index) => {
      const x =
        padding +
        (index / Math.max(history.length - 1, 1)) *
          (width - padding * 2)

      const y =
        height -
        padding -
        ((value - minValue) / (maxValue - minValue)) *
          (height - padding * 2)

      return `${x},${y}`
    })
    .join(" ")

  const latestValue = history[history.length - 1] ?? 0

  return (
    <div className="dashboard-card delay-5 rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-5 sm:p-6 relative overflow-hidden">
      
      {/* Background glow */}
      <div className="absolute -top-20 right-10 w-40 h-40 bg-cyan-400/5 blur-3xl rounded-full" />

      <div className="relative z-10">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">
              Threat Intelligence
            </p>

            <h2 className="text-lg sm:text-xl font-semibold mt-1">
              Real-Time Risk Activity
            </h2>
          </div>

          <div className="text-right">
            <p className="text-2xl font-bold text-cyan-400">
              {latestValue}
            </p>

            <p className="text-[10px] uppercase tracking-widest text-slate-500">
              Current Risk
            </p>
          </div>
        </div>

        {/* Graph */}
        <div className="w-full overflow-hidden">
          <svg
            viewBox={`0 0 ${width} ${height}`}
            className="w-full h-[220px]"
            preserveAspectRatio="none"
          >
            {/* Horizontal grid */}
            {[20, 40, 60, 80].map((value) => {
              const y =
                height -
                padding -
                (value / 100) *
                  (height - padding * 2)

              return (
                <line
                  key={value}
                  x1={padding}
                  y1={y}
                  x2={width - padding}
                  y2={y}
                  stroke="rgba(148,163,184,0.08)"
                  strokeWidth="1"
                />
              )
            })}

            {/* Risk line */}
            <polyline
              points={points}
              fill="none"
              stroke="currentColor"
              className="text-cyan-400"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Data points */}
            {history.map((value, index) => {
              const x =
                padding +
                (index / Math.max(history.length - 1, 1)) *
                  (width - padding * 2)

              const y =
                height -
                padding -
                (value / 100) *
                  (height - padding * 2)

              return (
                <circle
                  key={index}
                  cx={x}
                  cy={y}
                  r={index === history.length - 1 ? 6 : 3}
                  fill="currentColor"
                  className={
                    index === history.length - 1
                      ? "text-cyan-300 animate-pulse"
                      : "text-cyan-400"
                  }
                />
              )
            })}
          </svg>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between mt-2">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-60 animate-ping" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-400" />
            </span>

            <span className="text-[10px] uppercase tracking-widest text-cyan-400">
              Live Analysis
            </span>
          </div>

          <span className="text-[10px] text-slate-500">
            Last 12 readings
          </span>
        </div>

      </div>
    </div>
  )
}

export default ThreatIntelligence