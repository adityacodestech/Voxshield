function VoiceProbability({ probability = 94.2 }) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-cyan-500/10 bg-[#080f1d] p-6">

      <div className="absolute -top-20 -right-20 w-40 h-40 bg-cyan-400/5 rounded-full blur-3xl" />

      <div className="relative">

        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-widest text-slate-500">
              Voice Analysis
            </p>

            <h2 className="text-lg font-semibold mt-2">
              AI Voice Probability
            </h2>
          </div>

          <span className="text-xs px-2 py-1 rounded-md bg-red-400/10 text-red-400 border border-red-400/20">
            SYNTHETIC
          </span>
        </div>

        {/* Gauge */}
        <div className="flex justify-center py-8">

          <div
            className="relative w-36 h-36 rounded-full flex items-center justify-center"
            style={{
              background: `conic-gradient(#22d3ee ${probability}%, #172033 ${probability}% 100%)`,
            }}
          >

            <div className="absolute w-28 h-28 rounded-full bg-[#080f1d] flex flex-col items-center justify-center">

              <span className="text-3xl font-bold text-cyan-400">
                {probability}%
              </span>

              <span className="text-[10px] text-slate-500 uppercase">
                AI Generated
              </span>

            </div>

          </div>

        </div>

        <div className="border-t border-white/5 pt-4">
          <p className="text-xs text-slate-400">
            High confidence synthetic voice pattern detected.
          </p>
        </div>

      </div>
    </div>
  )
}

export default VoiceProbability