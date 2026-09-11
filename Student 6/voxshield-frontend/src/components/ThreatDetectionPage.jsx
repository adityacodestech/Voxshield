function ThreatDetectionPage({ securityState }) {
  const { aiProbability, riskScore, threatLevel } = securityState

  const humanProbability = Number(
    (100 - aiProbability).toFixed(1)
  )

  const speakerMatch = securityState.speakerMatch
  const speakerConfidence =
  speakerMatch === null
    ? 0
    : speakerMatch
      ? 92
      : 18

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="dashboard-card">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-400">
            VoxShield / AI Security Engine
          </p>

          <h1 className="text-2xl sm:text-3xl font-bold mt-2">
            Threat Detection
          </h1>

          <p className="text-sm text-slate-500 mt-2 max-w-2xl">
            Multi-signal analysis of the active voice stream for
            synthetic speech and impersonation indicators.
          </p>
        </div>
      </div>

      {/* Main AI Analysis */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">

        {/* AI Probability */}
        <div className="dashboard-card delay-1 rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6">

          <p className="text-xs uppercase tracking-widest text-slate-500">
            AI Voice Probability
          </p>

          <div className="flex items-center justify-center py-8">
            <div
              className="relative w-40 h-40 rounded-full flex items-center justify-center"
              style={{
                background: `conic-gradient(#22d3ee ${aiProbability}%, rgba(255,255,255,0.05) 0)`,
              }}
            >
              <div className="absolute inset-[10px] rounded-full bg-[#080f1d] flex flex-col items-center justify-center">
                <span className="text-3xl font-bold text-cyan-400">
                  {aiProbability}%
                </span>

                <span className="text-[9px] uppercase tracking-widest text-slate-500">
                  Synthetic
                </span>
              </div>
            </div>
          </div>

          <div className="flex justify-between text-xs">
            <span className="text-slate-500">
              Human
            </span>

            <span className="text-slate-300">
              {humanProbability}%
            </span>
          </div>

          <div className="h-1.5 bg-white/5 rounded-full mt-2 overflow-hidden">
            <div
              className="h-full bg-cyan-400 transition-all duration-700"
              style={{ width: `${humanProbability}%` }}
            />
          </div>

        </div>

        {/* Speaker Analysis */}
        <div className="dashboard-card delay-2 rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6">

          <p className="text-xs uppercase tracking-widest text-slate-500">
            Speaker Analysis
          </p>

          <div className="mt-8">

            <div className="flex justify-between items-end">
              <div>
                <p className="text-3xl font-bold">
                  {speakerMatch === null
  ? "N/A"
  : speakerMatch
    ? "MATCH"
    : "MISMATCH"}
                </p>

                <p className="text-xs text-slate-500 mt-1">
                  Speaker match confidence
                </p>
              </div>

              <span
  className={
    speakerMatch === null || speakerMatch
      ? "text-xs text-emerald-400"
      : "text-xs text-red-400"
  }
>
  {speakerMatch === null
    ? "UNKNOWN"
    : speakerMatch
      ? "MATCH"
      : "MISMATCH"}
</span>
            </div>

            <div className="h-3 bg-white/5 rounded-full mt-6 overflow-hidden">
              <div
                className="h-full bg-red-400 transition-all duration-700"
                style={{ width: `${speakerConfidence}%` }}
              />
            </div>

            <div className="grid grid-cols-2 gap-3 mt-6">

              <Signal
                label="Voiceprint"
                value="MISMATCH"
                danger
              />

              <Signal
                label="Pitch Pattern"
                value="ANOMALY"
                danger
              />

            </div>

          </div>
        </div>

        {/* Risk Engine */}
        <div className="dashboard-card delay-3 rounded-2xl border border-red-400/10 bg-[#080f1d] p-6">

          <p className="text-xs uppercase tracking-widest text-slate-500">
            Risk Engine
          </p>

          <div className="mt-8">

            <p className="text-5xl font-bold text-red-400">
              {riskScore}
            </p>

            <p className="text-xs text-slate-500 mt-2">
              Composite threat score / 100
            </p>

            <div className="h-2 bg-white/5 rounded-full mt-6 overflow-hidden">
              <div
                className="h-full bg-red-400 transition-all duration-700"
                style={{ width: `${riskScore}%` }}
              />
            </div>

            <div className="flex items-center justify-between mt-5">
              <span className="text-xs text-slate-500">
                Threat classification
              </span>

              <span className="text-xs font-semibold text-red-400">
                {threatLevel}
              </span>
            </div>

          </div>
        </div>

      </div>

      {/* Detection Signals */}
      <div className="dashboard-card delay-4 rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6">

        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-xs uppercase tracking-widest text-slate-500">
              Detection Signals
            </p>

            <h2 className="text-lg font-semibold mt-1">
              Voice Integrity Analysis
            </h2>
          </div>

          <span className="flex items-center gap-2 text-xs text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            ENGINE ACTIVE
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

          <DetectionSignal
            title="Spectral Analysis"
            status="ANOMALY"
            detail="Synthetic artifacts detected"
            danger
          />

          <DetectionSignal
            title="Prosody Analysis"
            status="SUSPICIOUS"
            detail="Unnatural speech pattern"
            danger
          />

          <DetectionSignal
            title="Speaker Verification"
            status="FAILED"
            detail="Voiceprint mismatch"
            danger
          />

          <DetectionSignal
            title="Audio Integrity"
            status="MONITORING"
            detail="Stream quality normal"
          />

        </div>
      </div>

      {/* Analysis Pipeline */}
      <div className="dashboard-card delay-5 rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6">

        <p className="text-xs uppercase tracking-widest text-slate-500">
          Analysis Pipeline
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mt-6">

          <PipelineStep
            number="01"
            title="Audio Capture"
            status="ACTIVE"
          />

          <PipelineStep
            number="02"
            title="Feature Extraction"
            status="ACTIVE"
          />

          <PipelineStep
            number="03"
            title="AI Detection"
            status="ACTIVE"
          />

          <PipelineStep
            number="04"
            title="Risk Classification"
            status={threatLevel}
          />

        </div>
      </div>

    </div>
  )
}

function Signal({ label, value, danger }) {
  return (
    <div className="rounded-lg border border-white/5 bg-black/20 p-3">
      <p className="text-[9px] uppercase tracking-widest text-slate-500">
        {label}
      </p>

      <p className={`text-xs font-semibold mt-2 ${
        danger ? "text-red-400" : "text-emerald-400"
      }`}>
        {value}
      </p>
    </div>
  )
}

function DetectionSignal({ title, status, detail, danger }) {
  return (
    <div className="rounded-xl border border-white/5 bg-black/20 p-4 hover:border-cyan-400/20 transition-all duration-300">

      <div className="flex items-center justify-between">
        <p className="text-sm font-medium">
          {title}
        </p>

        <span className={`w-2 h-2 rounded-full ${
          danger ? "bg-red-400 animate-pulse" : "bg-emerald-400"
        }`} />
      </div>

      <p className={`text-xs font-semibold mt-4 ${
        danger ? "text-red-400" : "text-emerald-400"
      }`}>
        {status}
      </p>

      <p className="text-[11px] text-slate-500 mt-1">
        {detail}
      </p>

    </div>
  )
}

function PipelineStep({ number, title, status }) {
  return (
    <div className="relative rounded-xl border border-white/5 bg-black/20 p-4">

      <span className="text-[10px] text-cyan-400 font-mono">
        {number}
      </span>

      <p className="text-sm font-medium mt-3">
        {title}
      </p>

      <div className="flex items-center gap-2 mt-3">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />

        <span className="text-[10px] uppercase tracking-widest text-emerald-400">
          {status}
        </span>
      </div>

    </div>
  )
}

export default ThreatDetectionPage