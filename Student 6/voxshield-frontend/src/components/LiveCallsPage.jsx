function LiveCallsPage({ securityState }) {
  const {
    aiProbability,
    riskScore,
    threatLevel,
    callStatus,
    callId,
    callDuration,
    audioStream,
    microphone,
    speakerMatch,
  } = securityState
    const speakerStatus =
    speakerMatch === null
      ? "UNKNOWN"
      : speakerMatch
        ? "MATCH"
        : "MISMATCH"

  return (
    <div className="space-y-6">

      {/* Page Header */}
      <div className="dashboard-card">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-cyan-400">
              VoxShield / Live Monitoring
            </p>

            <h1 className="text-2xl sm:text-3xl font-bold mt-2">
              Live Call Analysis
            </h1>

            <p className="text-sm text-slate-500 mt-2">
              Real-time voice intelligence and impersonation detection.
            </p>
          </div>

          <div className="flex items-center gap-2 px-3 py-2 rounded-lg border border-emerald-400/20 bg-emerald-400/5">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60 animate-ping" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400" />
            </span>

            <span className="text-xs text-emerald-400 uppercase tracking-wider">
              {callStatus}
            </span>
          </div>
        </div>
      </div>

      {/* Main Call Card */}
      <div className="dashboard-card delay-1 rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-5 sm:p-7">

        <div className="flex flex-col lg:flex-row gap-8">

          {/* Left */}
          <div className="flex-1">

            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-xl border border-cyan-400/20 bg-cyan-400/5 flex items-center justify-center text-2xl">
                ◉
              </div>

              <div>
                <p className="text-xs text-slate-500 uppercase tracking-widest">
                  Active Call
                </p>

                <h2 className="text-xl font-semibold mt-1">
                  {callId}
                </h2>
              </div>
            </div>

            {/* Duration */}
            <div className="mt-8">
              <p className="text-xs text-slate-500 uppercase tracking-widest">
                Call Duration
              </p>

              <p className="text-4xl font-mono font-bold text-cyan-400 mt-2">
                {callDuration}
              </p>
            </div>

            {/* Waveform */}
            <div className="mt-8 h-24 flex items-center justify-center gap-1.5 rounded-xl border border-white/5 bg-black/20 overflow-hidden">

              {Array.from({ length: 36 }).map((_, index) => (
                <span
                  key={index}
                  className="waveform-bar w-1 rounded-full bg-cyan-400/70"
                  style={{
                    height: `${20 + ((index * 17) % 55)}px`,
                    animationDelay: `${index * 35}ms`,
                  }}
                />
              ))}

            </div>

            <div className="flex items-center gap-3 mt-4">
              <span className="relative flex h-2.5 w-2.5">
                <span className="absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-60 animate-ping" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-400" />
              </span>

              <span className="text-xs text-cyan-400 uppercase tracking-widest">
                Audio stream analyzing
              </span>
            </div>
          </div>

          {/* Right Metrics */}
          <div className="lg:w-80 grid grid-cols-2 lg:grid-cols-1 gap-4">

            <Metric
              label="AI Voice Probability"
              value={`${aiProbability}%`}
              description="Synthetic voice likelihood"
            />

            <Metric
              label="Risk Score"
              value={`${riskScore}/100`}
              description="Current impersonation risk"
            />

            <Metric
              label="Threat Level"
              value={threatLevel}
              description="Current security classification"
            />

          </div>
        </div>
      </div>

      {/* Connection Status */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">

        <ConnectionCard
          title="Audio Stream"
          value={audioStream}
          detail="Incoming call audio"
        />

        <ConnectionCard
          title="Microphone"
          value={microphone}
          detail="Capture interface"
        />

      </div>

    </div>
  )
}

function Metric({ label, value, description }) {
  return (
    <div className="rounded-xl border border-white/5 bg-black/20 p-4 hover:border-cyan-400/20 transition-all duration-300">

      <p className="text-[10px] uppercase tracking-widest text-slate-500">
        {label}
      </p>

      <p className="text-2xl font-bold text-white mt-2">
        {value}
      </p>

      <p className="text-xs text-slate-600 mt-1">
        {description}
      </p>

    </div>
  )
}

function ConnectionCard({ title, value, detail }) {
  return (
    <div className="rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-5">

      <div className="flex items-center justify-between">

        <div>
          <p className="text-xs uppercase tracking-widest text-slate-500">
            {title}
          </p>

          <p className="text-lg font-semibold mt-2">
            {detail}
          </p>
        </div>

        <div className="text-right">
          <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-400/5 border border-emerald-400/10">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-emerald-400">
              {value}
            </span>
          </span>
        </div>

      </div>

    </div>
  )
}

export default LiveCallsPage