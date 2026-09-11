function SecurityLoading() {
  return (
    <div className="min-h-[400px] flex items-center justify-center">
      <div className="w-full max-w-md rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-8 text-center dashboard-card">
        
        <div className="relative mx-auto w-16 h-16">
          <div className="absolute inset-0 rounded-full border border-cyan-400/20 animate-ping" />
          
          <div className="absolute inset-2 rounded-full border border-cyan-400/30" />
          
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-2xl text-cyan-400 animate-pulse">
              ◈
            </span>
          </div>
        </div>

        <p className="text-xs uppercase tracking-[0.25em] text-cyan-400 mt-6">
          VoxShield Security Engine
        </p>

        <h2 className="text-xl font-semibold mt-2">
          Initializing Security Pipeline
        </h2>

        <p className="text-sm text-slate-500 mt-3">
          Establishing secure connection with voice analysis services...
        </p>

        <div className="mt-6 h-1 rounded-full bg-white/5 overflow-hidden">
          <div className="h-full w-1/2 bg-cyan-400 rounded-full animate-pulse" />
        </div>

        <div className="flex items-center justify-center gap-2 mt-5">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />

          <span className="text-[10px] uppercase tracking-widest text-slate-500">
            Waiting for security data
          </span>
        </div>

      </div>
    </div>
  )
}

export default SecurityLoading