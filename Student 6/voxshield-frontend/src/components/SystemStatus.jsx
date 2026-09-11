function SystemStatus() {
  const systems = [
    {
      name: "Backend API",
      status: "ONLINE",
      detail: "FastAPI",
    },
    {
      name: "WebSocket",
      status: "ONLINE",
      detail: "Real-time stream",
    },
    {
      name: "Voice Analyzer",
      status: "ONLINE",
      detail: "AI detection",
    },
    {
      name: "Risk Engine",
      status: "ONLINE",
      detail: "Risk scoring",
    },
    {
      name: "Blockchain",
      status: "ONLINE",
      detail: "Audit ledger",
    },
  ]

  return (
    <div className="rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6">

      <div className="flex items-center justify-between mb-6">

        <div>
          <p className="text-xs uppercase tracking-widest text-slate-500">
            Infrastructure
          </p>

          <h2 className="text-lg font-semibold mt-2">
            System Status
          </h2>
        </div>

        <div className="flex items-center gap-2 text-xs text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          ALL SYSTEMS OPERATIONAL
        </div>

      </div>

      <div className="space-y-2">

        {systems.map((system) => (
          <div
            key={system.name}
            className="flex items-center justify-between rounded-xl border border-white/5 bg-white/[0.02] px-4 py-3 hover:bg-white/[0.04] transition-all"
          >

            <div className="flex items-center gap-3">

              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />

              <div>
                <p className="text-sm text-slate-200">
                  {system.name}
                </p>

                <p className="text-[10px] text-slate-600">
                  {system.detail}
                </p>
              </div>

            </div>

            <span className="text-[10px] font-medium text-emerald-400">
              {system.status}
            </span>

          </div>
        ))}

      </div>

    </div>
  )
}

export default SystemStatus