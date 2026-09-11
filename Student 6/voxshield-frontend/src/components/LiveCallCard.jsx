function LiveCallCard({securityState}) {
  const bars = [
    18, 32, 48, 28, 55, 72, 42, 30,
    64, 82, 52, 36, 70, 45, 26, 58,
    76, 40, 62, 30, 50, 68, 34, 24,
    56, 78, 44, 32, 66, 48, 28, 60
  ]

  return (
    <div className="relative overflow-hidden rounded-2xl border border-cyan-400/20 bg-[#080f1d] p-6">

      {/* Background glow */}
      <div className="absolute -top-32 left-1/3 w-72 h-72 bg-cyan-400/5 rounded-full blur-3xl" />

      <div className="relative">

        {/* Header */}
        <div className="flex items-center justify-between">

          <div className="flex items-center gap-3">

            <div className="relative">

              <span className="absolute inset-0 rounded-full bg-red-400/30 animate-ping" />

              <span className="relative block w-3 h-3 rounded-full bg-red-400" />

            </div>

            <div>
              <p className="text-xs uppercase tracking-widest text-red-400">
                {securityState.callStatus}
              </p>

              <h2 className="text-lg font-semibold mt-1">
                Live Call Protection
              </h2>
            </div>

          </div>

          <span className="px-3 py-1 rounded-lg bg-emerald-400/10 border border-emerald-400/20 text-xs text-emerald-400">
            ENCRYPTED
          </span>

        </div>

        {/* Call information */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mt-7">

          <CallInfo
            label="Call ID"
            value="{securityState.callId}"
          />

          <CallInfo
            label="Duration"
            value="{securityState.callDuration}"
          />

          <CallInfo
            label="Audio Stream"
            value="{securityState.audioStream}"
          />

          <CallInfo
            label="Microphone"
            value="{securityState.microphone}"
          />

        </div>

        {/* Waveform */}
        <div className="mt-8 rounded-xl border border-white/5 bg-black/20 px-5 py-7">

          <div className="flex items-center justify-between mb-5">

            <p className="text-xs text-slate-500 uppercase tracking-widest">
              Real-Time Audio Stream
            </p>

            <div className="flex items-center gap-2 text-[10px] text-emerald-400">
              <span className="waveform-bar w-1.5 rounded-full bg-cyan-400/70" />
              RECEIVING AUDIO
            </div>

          </div>

          <div className="h-20 flex items-center justify-center gap-1">

            {bars.map((height, index) => (
              <div
                key={index}
                className="w-1.5 rounded-full bg-cyan-400/70 animate-pulse"
                style={{
                  height: `${height}%`,
                  animationDelay: `${index * 70}ms`,
                  animationDuration: `${700 + (index % 4) * 150}ms`,
                }}
              />
            ))}

          </div>

        </div>

        {/* Bottom status */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mt-5">

          <div className="flex items-center gap-2">

            <span className="text-xs text-slate-500">
              Security monitoring:
            </span>

            <span className="text-xs text-cyan-400">
              ACTIVE
            </span>

          </div>

          <div className="text-xs text-slate-600">
            Voice analysis running continuously
          </div>

        </div>

      </div>

    </div>
  )
}

function CallInfo({ label, value }) {
  return (
    <div className="rounded-lg border border-white/5 bg-white/[0.02] p-3">

      <p className="text-[10px] uppercase tracking-wider text-slate-600">
        {label}
      </p>

      <p className="text-xs font-medium text-slate-300 mt-2">
        {value}
      </p>

    </div>
  )
}

export default LiveCallCard