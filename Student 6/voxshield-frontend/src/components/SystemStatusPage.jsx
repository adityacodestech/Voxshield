function SystemStatusPage() {
  const systems = [
    {
      name: "Backend API",
      type: "API SERVICE",
      status: "ONLINE",
      detail: "FastAPI security gateway",
      latency: "42 ms",
    },
    {
      name: "WebSocket",
      type: "REAL-TIME CHANNEL",
      status: "ONLINE",
      detail: "Live audio event stream",
      latency: "18 ms",
    },
    {
      name: "Voice Analyzer",
      type: "AI ENGINE",
      status: "ONLINE",
      detail: "Synthetic voice detection",
      latency: "126 ms",
    },
    {
      name: "Risk Engine",
      type: "DECISION ENGINE",
      status: "ONLINE",
      detail: "Threat scoring pipeline",
      latency: "31 ms",
    },
    {
      name: "Blockchain",
      type: "AUDIT LAYER",
      status: "ONLINE",
      detail: "Immutable security ledger",
      latency: "84 ms",
    },
  ]

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="dashboard-card">
        <p className="text-xs uppercase tracking-[0.25em] text-cyan-400">
          VoxShield / Infrastructure
        </p>

        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mt-2">

          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">
              System Status
            </h1>

            <p className="text-sm text-slate-500 mt-2">
              Monitor the health of every component in the security pipeline.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs text-emerald-400">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-50 animate-ping" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400" />
            </span>

            ALL SYSTEMS OPERATIONAL
          </div>

        </div>
      </div>

      {/* Overall Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <div className="dashboard-card delay-1 lg:col-span-2 rounded-2xl border border-emerald-400/10 bg-[#080f1d] p-6">

          <div className="flex items-center justify-between">

            <div>
              <p className="text-xs uppercase tracking-widest text-slate-500">
                Infrastructure Health
              </p>

              <h2 className="text-2xl font-bold mt-2">
                100%
              </h2>

              <p className="text-xs text-slate-500 mt-1">
                All monitored services responding normally
              </p>
            </div>

            <div className="w-16 h-16 rounded-full border-4 border-emerald-400/20 flex items-center justify-center">
              <span className="text-emerald-400 text-xl">
                ✓
              </span>
            </div>

          </div>

          <div className="grid grid-cols-5 gap-2 mt-8">

            {systems.map((system) => (
              <div
                key={system.name}
                className="h-2 rounded-full bg-emerald-400/60 animate-pulse"
              />
            ))}

          </div>

        </div>

        <div className="dashboard-card delay-2 rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6">

          <p className="text-xs uppercase tracking-widest text-slate-500">
            Active Services
          </p>

          <p className="text-4xl font-bold text-cyan-400 mt-4">
            {systems.length}
          </p>

          <p className="text-xs text-slate-500 mt-2">
            Security components online
          </p>

          <div className="flex items-center gap-2 mt-6">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />

            <span className="text-xs text-emerald-400">
              No service interruptions
            </span>
          </div>

        </div>

      </div>

      {/* Services */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

        {systems.map((system, index) => (
          <ServiceCard
            key={system.name}
            system={system}
            index={index}
          />
        ))}

      </div>

      {/* Pipeline */}
      <div className="dashboard-card delay-5 rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6">

        <p className="text-xs uppercase tracking-widest text-slate-500">
          Security Pipeline
        </p>

        <h2 className="text-lg font-semibold mt-1">
          Component Connectivity
        </h2>

        <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3 mt-7">

          <PipelineNode label="CALL" />
          <Connector />
          <PipelineNode label="AUDIO" />
          <Connector />
          <PipelineNode label="AI ENGINE" />
          <Connector />
          <PipelineNode label="RISK" />
          <Connector />
          <PipelineNode label="BLOCKCHAIN" />

        </div>

      </div>

    </div>
  )
}

function ServiceCard({ system, index }) {
  return (
    <div
      className="dashboard-card rounded-2xl border border-white/5 bg-[#080f1d] p-5 hover:border-emerald-400/20 transition-all duration-300"
      style={{ animationDelay: `${index * 80}ms` }}
    >

      <div className="flex items-start justify-between gap-4">

        <div className="flex gap-4">

          <div className="w-11 h-11 rounded-xl border border-emerald-400/10 bg-emerald-400/5 flex items-center justify-center text-emerald-400">
            ✓
          </div>

          <div>
            <p className="text-[9px] uppercase tracking-widest text-cyan-400">
              {system.type}
            </p>

            <h3 className="font-semibold mt-1">
              {system.name}
            </h3>

            <p className="text-xs text-slate-500 mt-1">
              {system.detail}
            </p>
          </div>

        </div>

        <span className="px-2 py-1 rounded bg-emerald-400/5 border border-emerald-400/10 text-[9px] font-bold tracking-widest text-emerald-400">
          {system.status}
        </span>

      </div>

      <div className="flex items-center justify-between mt-5 pt-4 border-t border-white/5">

        <span className="text-[10px] uppercase tracking-widest text-slate-600">
          Response
        </span>

        <span className="font-mono text-xs text-cyan-400">
          {system.latency}
        </span>

      </div>

    </div>
  )
}

function PipelineNode({ label }) {
  return (
    <div className="flex-1 rounded-xl border border-cyan-400/10 bg-cyan-400/5 p-4 text-center">

      <span className="text-[10px] font-bold tracking-widest text-cyan-400">
        {label}
      </span>

      <div className="flex items-center justify-center gap-2 mt-2">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />

        <span className="text-[9px] text-emerald-400">
          READY
        </span>
      </div>

    </div>
  )
}

function Connector() {
  return (
    <div className="hidden md:block text-cyan-400/30 text-xl">
      →
    </div>
  )
}

export default SystemStatusPage