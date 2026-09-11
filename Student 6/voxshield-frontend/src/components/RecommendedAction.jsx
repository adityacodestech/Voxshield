import { useState } from "react"

function RecommendedAction() {
  const [status, setStatus] = useState("RECOMMENDED")

  const handleBlock = () => {
    setStatus("BLOCKED")
  }

  const handleVerify = () => {
    setStatus("VERIFICATION REQUIRED")
  }

  return (
    <div className="rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6">

      <div className="flex items-center justify-between">

        <div>
          <p className="text-xs uppercase tracking-widest text-slate-500">
            Automated Response
          </p>

          <h2 className="text-lg font-semibold mt-2">
            Recommended Action
          </h2>
        </div>

        <span className="text-xs text-amber-400 bg-amber-400/10 border border-amber-400/20 px-3 py-1 rounded-lg">
          {status}
        </span>

      </div>

      {/* Recommendation */}
      <div className="mt-7 rounded-xl border border-red-400/10 bg-red-400/[0.03] p-5">

        <div className="flex items-start gap-4">

          <div className="w-11 h-11 shrink-0 rounded-xl bg-red-400/10 border border-red-400/20 flex items-center justify-center text-red-400 text-xl">
            !
          </div>

          <div>

            <h3 className="font-semibold text-red-300">
              Block suspicious transaction
            </h3>

            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              AI voice probability and impersonation risk exceed
              the configured security threshold.
            </p>

          </div>

        </div>

      </div>

      {/* Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-5">

        <button
          onClick={handleBlock}
          className="py-3 rounded-xl bg-red-400/10 border border-red-400/20 text-red-400 text-sm font-medium hover:bg-red-400/20 active:scale-[0.98] transition-all"
        >
          BLOCK CALL
        </button>

        <button
          onClick={handleVerify}
          className="py-3 rounded-xl bg-cyan-400/10 border border-cyan-400/20 text-cyan-400 text-sm font-medium hover:bg-cyan-400/20 active:scale-[0.98] transition-all"
        >
          VERIFY USER
        </button>

      </div>

      {status === "BLOCKED" && (
        <div className="mt-4 rounded-lg bg-emerald-400/10 border border-emerald-400/20 p-3 text-center text-xs text-emerald-400">
          ✓ Call blocked successfully
        </div>
      )}

      {status === "VERIFICATION REQUIRED" && (
        <div className="mt-4 rounded-lg bg-cyan-400/10 border border-cyan-400/20 p-3 text-center text-xs text-cyan-400">
          Identity verification initiated
        </div>
      )}

    </div>
  )
}

export default RecommendedAction