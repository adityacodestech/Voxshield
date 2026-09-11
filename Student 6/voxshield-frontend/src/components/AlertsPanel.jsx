function AlertsPanel({ alerts }) {
  return (
    <div className="rounded-2xl border border-red-400/10 bg-[#080f1d] p-6">

      <div className="flex items-center justify-between mb-6">

        <div>
          <p className="text-xs uppercase tracking-widest text-slate-500">
            Threat Monitoring
          </p>

          <h2 className="text-lg font-semibold mt-2">
            Active Security Alerts
          </h2>
        </div>

        <span className="px-3 py-1 rounded-lg bg-red-400/10 border border-red-400/20 text-xs text-red-400">
          {alerts.length} ACTIVE
        </span>

      </div>

      <div className="space-y-3">

        {alerts.map((alert, index) => (
          <div
            key={index}
            className="group rounded-xl border border-white/5 bg-white/[0.02] p-4 hover:border-red-400/20 transition-all"
          >

            <div className="flex gap-3">

              <div className="w-9 h-9 shrink-0 rounded-lg bg-red-400/10 border border-red-400/10 flex items-center justify-center text-red-400">
                !
              </div>

              <div className="flex-1 min-w-0">

                <div className="flex flex-wrap items-center justify-between gap-2">

                  <h3 className="text-sm font-medium text-white">
                    {alert.title}
                  </h3>

                  <span className="text-[9px] px-2 py-1 rounded bg-red-400/10 text-red-400">
                    {alert.severity}
                  </span>

                </div>

                <p className="text-xs text-slate-500 mt-1">
                  {alert.description}
                </p>

                <p className="text-[10px] text-slate-600 mt-2">
                  Detected {alert.time}
                </p>

              </div>

            </div>

          </div>
        ))}

      </div>

    </div>
  )
}

export default AlertsPanel