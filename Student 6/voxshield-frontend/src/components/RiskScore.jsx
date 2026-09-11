function RiskScore({ score = 87 }) {
  return (
    <div className="rounded-2xl border border-cyan-500/10 bg-[#080f1d] p-6">

      <p className="text-xs uppercase tracking-widest text-slate-500">
        Security Assessment
      </p>

      <h2 className="text-lg font-semibold mt-2">
        Impersonation Risk
      </h2>

      <div className="flex items-end gap-2 mt-8">

        <span className="text-6xl font-bold text-red-400">
          {score}
        </span>

        <span className="text-sm text-slate-500 mb-2">
          / 100
        </span>

      </div>

      <div className="mt-6">

        <div className="flex justify-between text-xs mb-2">
          <span className="text-slate-500">
            Risk level
          </span>

          <span className="text-red-400">
            HIGH
          </span>
        </div>

        <div className="h-2 bg-slate-800 rounded-full overflow-hidden">

          <div
            className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-yellow-400 to-red-400"
            style={{ width: `${score}%` }}
          />

        </div>

      </div>

      <div className="grid grid-cols-2 gap-3 mt-6">

        <Indicator label="Voice Pattern" value="MATCHED" />
        <Indicator label="Speaker ID" value="MISMATCH" />
        <Indicator label="Behavior" value="SUSPICIOUS" />
        <Indicator label="Transaction" value="HIGH RISK" />

      </div>

    </div>
  )
}

function Indicator({ label, value }) {
  return (
    <div className="rounded-lg bg-white/[0.02] border border-white/5 p-3">

      <p className="text-[10px] uppercase text-slate-600">
        {label}
      </p>

      <p className="text-xs text-slate-300 mt-1">
        {value}
      </p>

    </div>
  )
}

export default RiskScore