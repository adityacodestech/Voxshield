function ThreatLevel({ level = "CRITICAL" }) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-red-400/20 bg-[#0b0c17] p-6">

      <div className="absolute inset-0 bg-red-500/[0.02]" />

      <div className="relative">

        <div className="flex items-center justify-between">

          <div>
            <p className="text-xs uppercase tracking-widest text-slate-500">
              Threat Classification
            </p>

            <h2 className="text-lg font-semibold mt-2">
              Current Threat Level
            </h2>
          </div>

          <div className="relative">

            <span className="absolute inset-0 rounded-full bg-red-400/30 animate-ping" />

            <span className="relative block w-3 h-3 rounded-full bg-red-400" />

          </div>

        </div>

        <div className="flex flex-col items-center justify-center py-9">

          <div className="relative w-32 h-32 flex items-center justify-center">

            <div className="absolute inset-0 rounded-full border border-red-400/20 animate-pulse" />

            <div className="absolute inset-3 rounded-full border border-red-400/10" />

            <div className="w-16 h-16 rounded-full bg-red-400/10 border border-red-400/30 flex items-center justify-center">

              <span className="text-red-400 text-2xl">
                !
              </span>

            </div>

          </div>

          <h3 className="text-3xl font-black tracking-[0.2em] text-red-400 mt-5">
            {level}
          </h3>

        </div>

        <div className="border-t border-white/5 pt-4">

          <p className="text-xs text-red-300/70">
            Immediate security intervention recommended.
          </p>

        </div>

      </div>

    </div>
  )
}

export default ThreatLevel