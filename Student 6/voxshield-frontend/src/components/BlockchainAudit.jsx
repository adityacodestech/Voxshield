function BlockchainAudit() {
  const blocks = [
    { label: "CALL", value: "#18490" },
    { label: "ANALYSIS", value: "#18491" },
    { label: "RISK", value: "#18492" },
  ]

  return (
    <div className="rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6">

      <div className="flex items-center justify-between">

        <div>
          <p className="text-xs uppercase tracking-widest text-slate-500">
            Immutable Ledger
          </p>

          <h2 className="text-lg font-semibold mt-2">
            Blockchain Audit
          </h2>
        </div>

        <span className="px-3 py-1 rounded-lg bg-emerald-400/10 border border-emerald-400/20 text-xs text-emerald-400">
          VERIFIED
        </span>

      </div>

      {/* Chain */}
      <div className="flex items-center justify-between mt-8">

        {blocks.map((block, index) => (
          <div key={block.label} className="flex items-center flex-1">

            <div className="flex flex-col items-center">

              <div className="w-12 h-12 rounded-xl bg-cyan-400/10 border border-cyan-400/20 flex items-center justify-center text-cyan-400">
                ⬡
              </div>

              <p className="text-[10px] text-slate-500 mt-2">
                {block.label}
              </p>

              <p className="text-[10px] text-cyan-400 mt-1">
                {block.value}
              </p>

            </div>

            {index < blocks.length - 1 && (
              <div className="h-px flex-1 bg-cyan-400/20 mx-3" />
            )}

          </div>
        ))}

      </div>

      {/* Transaction */}
      <div className="mt-8 space-y-3">

        <AuditRow
          label="Block Height"
          value="#18,492"
        />

        <AuditRow
          label="Transaction Hash"
          value="0x8F3A...91CD"
        />

        <AuditRow
          label="Ledger Integrity"
          value="VALID"
          success
        />

      </div>

    </div>
  )
}

function AuditRow({ label, value, success }) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-white/5 bg-white/[0.02] px-4 py-3">

      <span className="text-xs text-slate-500">
        {label}
      </span>

      <span
        className={`text-xs font-medium ${
          success ? "text-emerald-400" : "text-slate-300"
        }`}
      >
        {value}
      </span>

    </div>
  )
}

export default BlockchainAudit