function SecurityError({
  title = "Security Services Unavailable",
  message = "Unable to establish a connection with the VoxShield security pipeline.",
  onRetry,
}) {
  return (
    <div className="min-h-[400px] flex items-center justify-center">
      <div className="w-full max-w-lg rounded-2xl border border-red-400/10 bg-[#080f1d] p-8 text-center dashboard-card">

        <div className="relative mx-auto w-16 h-16">
          <div className="absolute inset-0 rounded-full border border-red-400/10" />

          <div className="absolute inset-2 rounded-full border border-red-400/20" />

          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-2xl text-red-400">
              !
            </span>
          </div>
        </div>

        <p className="text-xs uppercase tracking-[0.25em] text-red-400 mt-6">
          VoxShield Security Engine
        </p>

        <h2 className="text-xl font-semibold mt-2">
          {title}
        </h2>

        <p className="text-sm text-slate-500 mt-3 max-w-md mx-auto">
          {message}
        </p>

        <div className="mt-6 flex items-center justify-center gap-2">
          <span className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />

          <span className="text-[10px] uppercase tracking-widest text-red-400">
            Connection Interrupted
          </span>
        </div>

        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-6 px-5 py-2.5 rounded-lg border border-cyan-400/20 bg-cyan-400/5 text-xs uppercase tracking-widest text-cyan-400 hover:bg-cyan-400/10 transition-all duration-300"
          >
            Retry Connection
          </button>
        )}

      </div>
    </div>
  )
}

export default SecurityError