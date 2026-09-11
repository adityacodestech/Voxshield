function BlockchainAuditPage({ securityState }) {
  const { riskScore, threatLevel, blockchainStatus, callId } =
    securityState

  const blockHeight = 18472931
  const transactionHash =
    "0x8f2a...91cd"

  const blocks = [
    {
      number: blockHeight - 2,
      status: "CONFIRMED",
      time: "21:52:41",
    },
    {
      number: blockHeight - 1,
      status: "CONFIRMED",
      time: "21:53:12",
    },
    {
      number: blockHeight,
      status: "CURRENT",
      time: "21:53:42",
    },
  ]

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="dashboard-card">
        <p className="text-xs uppercase tracking-[0.25em] text-cyan-400">
          VoxShield / Immutable Security Ledger
        </p>

        <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-5 mt-2">

          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">
              Blockchain Audit
            </h1>

            <p className="text-sm text-slate-500 mt-2 max-w-2xl">
              Tamper-evident recording of security decisions,
              risk scores and incident events.
            </p>
          </div>

          <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-emerald-400/20 bg-emerald-400/5">

            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-50 animate-ping" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400" />
            </span>

            <span className="text-xs text-emerald-400 uppercase tracking-widest">
              {blockchainStatus}
            </span>

          </div>

        </div>
      </div>

      {/* Ledger Summary */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">

        <AuditMetric
          label="Block Height"
          value={blockHeight.toLocaleString()}
        />

        <AuditMetric
          label="Risk Score"
          value={`${riskScore}/100`}
          danger={riskScore >= 70}
        />

        <AuditMetric
          label="Threat Level"
          value={threatLevel}
          danger={threatLevel === "CRITICAL"}
        />

        <AuditMetric
          label="Call Reference"
          value={callId}
        />

      </div>

      {/* Current Transaction */}
      <div className="dashboard-card delay-1 rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6">

        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-5">

          <div>
            <p className="text-xs uppercase tracking-widest text-slate-500">
              Latest Ledger Entry
            </p>

            <h2 className="text-xl font-semibold mt-2">
              Security Decision Recorded
            </h2>

            <p className="text-sm text-slate-500 mt-2">
              Current call risk assessment committed to the audit layer.
            </p>
          </div>

          <div className="px-4 py-3 rounded-xl border border-cyan-400/10 bg-cyan-400/5">

            <p className="text-[9px] uppercase tracking-widest text-slate-500">
              Integrity
            </p>

            <p className="text-sm font-semibold text-cyan-400 mt-1">
              VERIFIED
            </p>

          </div>

        </div>

        {/* Hash */}
        <div className="mt-7 rounded-xl border border-white/5 bg-black/30 p-4">

          <p className="text-[10px] uppercase tracking-widest text-slate-600">
            Transaction Hash
          </p>

          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mt-2">

            <code className="text-xs sm:text-sm text-cyan-400 break-all">
              {transactionHash}
            </code>

            <span className="text-[9px] uppercase tracking-widest text-emerald-400 whitespace-nowrap">
              Immutable Record
            </span>

          </div>

        </div>

      </div>

      {/* Block Chain */}
      <div className="dashboard-card delay-2 rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6">

        <div className="flex items-center justify-between mb-8">

          <div>
            <p className="text-xs uppercase tracking-widest text-slate-500">
              Chain Verification
            </p>

            <h2 className="text-lg font-semibold mt-1">
              Recent Blocks
            </h2>
          </div>

          <span className="text-[10px] text-emerald-400 uppercase tracking-widest">
            Chain Valid
          </span>

        </div>

        <div className="space-y-4">

          {blocks.map((block, index) => (
            <div
              key={block.number}
              className="flex items-center gap-4"
            >

              {/* Node */}
              <div className="flex flex-col items-center">

                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center border ${
                    block.status === "CURRENT"
                      ? "border-cyan-400/30 bg-cyan-400/10 text-cyan-400"
                      : "border-emerald-400/10 bg-emerald-400/5 text-emerald-400"
                  }`}
                >
                  ⬡
                </div>

                {index !== blocks.length - 1 && (
                  <div className="h-5 w-px bg-cyan-400/10 mt-1" />
                )}

              </div>

              {/* Block */}
              <div className="flex-1 rounded-xl border border-white/5 bg-black/20 p-4">

                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">

                  <div>
                    <p className="text-xs text-slate-500">
                      Block
                    </p>

                    <p className="font-mono text-sm text-white mt-1">
                      #{block.number.toLocaleString()}
                    </p>
                  </div>

                  <div className="flex items-center gap-4">

                    <span className="text-[10px] text-slate-600">
                      {block.time}
                    </span>

                    <span
                      className={`text-[9px] font-bold tracking-widest ${
                        block.status === "CURRENT"
                          ? "text-cyan-400"
                          : "text-emerald-400"
                      }`}
                    >
                      {block.status}
                    </span>

                  </div>

                </div>

              </div>

            </div>
          ))}

        </div>

      </div>

      {/* Security Record */}
      <div className="dashboard-card delay-3 rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6">

        <p className="text-xs uppercase tracking-widest text-slate-500">
          Recorded Security Decision
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5">

          <Record
            label="Call"
            value={callId}
          />

          <Record
            label="Risk"
            value={`${riskScore}/100`}
          />

          <Record
            label="Classification"
            value={threatLevel}
          />

        </div>

        <div className="mt-5 flex items-center gap-3 px-4 py-3 rounded-xl border border-emerald-400/10 bg-emerald-400/5">

          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />

          <p className="text-xs text-emerald-400">
            Security record integrity verified
          </p>

        </div>

      </div>

    </div>
  )
}

function AuditMetric({ label, value, danger }) {
  return (
    <div className="dashboard-card rounded-xl border border-white/5 bg-[#080f1d] p-4">

      <p className="text-[10px] uppercase tracking-widest text-slate-500">
        {label}
      </p>

      <p
        className={`text-xl sm:text-2xl font-bold mt-2 ${
          danger ? "text-red-400" : "text-cyan-400"
        }`}
      >
        {value}
      </p>

    </div>
  )
}

function Record({ label, value }) {
  return (
    <div className="rounded-xl border border-white/5 bg-black/20 p-4">

      <p className="text-[10px] uppercase tracking-widest text-slate-600">
        {label}
      </p>

      <p className="font-mono text-sm text-white mt-2">
        {value}
      </p>

    </div>
  )
}

export default BlockchainAuditPage