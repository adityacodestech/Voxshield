import { useState } from "react"

function AlertsPage({ alerts }) {
  const activeAlerts = Array.isArray(alerts) ? alerts : []
  const [filter, setFilter] = useState("ALL")

  const filteredAlerts =
    filter === "ALL"
      ? activeAlerts
      : activeAlerts.filter((alert) => alert.severity === filter)

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="dashboard-card">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">

          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-cyan-400">
              VoxShield / Security Operations
            </p>

            <h1 className="text-2xl sm:text-3xl font-bold mt-2">
              Security Alerts
            </h1>

            <p className="text-sm text-slate-500 mt-2">
              Active threats detected across the voice security pipeline.
            </p>
          </div>

          <div className="px-4 py-3 rounded-xl border border-red-400/20 bg-red-400/5">
            <p className="text-2xl font-bold text-red-400">
              {activeAlerts.length}
            </p>

            <p className="text-[10px] uppercase tracking-widest text-slate-500">
              Active Alerts
            </p>
          </div>

        </div>
      </div>

      {/* Filters */}
      <div className="dashboard-card delay-1 flex flex-wrap gap-2">

        {["ALL", "CRITICAL", "HIGH"].map((level) => (
          <button
            key={level}
            onClick={() => setFilter(level)}
            className={`px-4 py-2 rounded-lg text-xs uppercase tracking-wider transition-all duration-300 ${
              filter === level
                ? "bg-cyan-400/10 text-cyan-400 border border-cyan-400/20"
                : "text-slate-500 border border-white/5 hover:text-white hover:bg-white/5"
            }`}
          >
            {level}
          </button>
        ))}

      </div>

      {/* Alert Feed */}
      <div className="space-y-3">

        {filteredAlerts.map((alert, index) => (
          <AlertCard
            key={`${alert.title}-${index}`}
            alert={alert}
            index={index}
          />
        ))}

        {filteredAlerts.length === 0 && (
          <div className="rounded-2xl border border-white/5 bg-[#080f1d] p-10 text-center">
            <p className="text-sm text-slate-500">
              No alerts match this filter.
            </p>
          </div>
        )}

      </div>

      {/* Security Event Stream */}
      <div className="dashboard-card delay-4 rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6">

        <div className="flex items-center justify-between">

          <div>
            <p className="text-xs uppercase tracking-widest text-slate-500">
              Event Stream
            </p>

            <h2 className="text-lg font-semibold mt-1">
              Security Activity
            </h2>
          </div>

          <span className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            LIVE
          </span>

        </div>

        <div className="mt-6 space-y-5">

          <Event
            time="NOW"
            title="Risk engine updated"
            detail="Composite risk score recalculated"
          />

          <Event
            time="12 SEC"
            title="Synthetic voice detected"
            detail="AI voice probability exceeded threshold"
            danger
          />

          <Event
            time="28 SEC"
            title="Speaker mismatch"
            detail="Registered speaker confidence dropped"
            danger
          />

          <Event
            time="41 SEC"
            title="Transaction risk detected"
            detail="Sensitive operation identified"
            danger
          />

        </div>

      </div>

    </div>
  )
}

function AlertCard({ alert, index }) {
  const isCritical = alert.severity === "CRITICAL"

  return (
    <div
      className="dashboard-card rounded-2xl border border-white/5 bg-[#080f1d] p-5 hover:border-red-400/20 transition-all duration-300"
      style={{ animationDelay: `${index * 100}ms` }}
    >

      <div className="flex gap-4">

        {/* Severity indicator */}
        <div className="flex flex-col items-center">

          <span
            className={`relative flex h-3 w-3 ${
              isCritical ? "animate-pulse" : ""
            }`}
          >
            <span
              className={`absolute inline-flex h-full w-full rounded-full opacity-40 ${
                isCritical ? "bg-red-400" : "bg-orange-400"
              }`}
            />

            <span
              className={`relative inline-flex rounded-full h-3 w-3 ${
                isCritical ? "bg-red-400" : "bg-orange-400"
              }`}
            />
          </span>

          <span className="w-px flex-1 bg-white/5 mt-3" />

        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">

          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">

            <h3 className="font-semibold">
              {alert.title}
            </h3>

            <span
              className={`w-fit px-2 py-1 rounded text-[9px] font-bold tracking-widest ${
                isCritical
                  ? "bg-red-400/10 text-red-400 border border-red-400/10"
                  : "bg-orange-400/10 text-orange-400 border border-orange-400/10"
              }`}
            >
              {alert.severity}
            </span>

          </div>

          <p className="text-sm text-slate-500 mt-2">
            {alert.description}
          </p>

          <div className="flex items-center gap-2 mt-4">
            <span className="text-[10px] text-slate-600 uppercase tracking-wider">
              Detected
            </span>

            <span className="text-[10px] text-cyan-400">
              {alert.time}
            </span>
          </div>

        </div>

      </div>

    </div>
  )
}

function Event({ time, title, detail, danger }) {
  return (
    <div className="flex gap-4">

      <div className="flex flex-col items-center">

        <span
          className={`w-2.5 h-2.5 rounded-full mt-1 ${
            danger
              ? "bg-red-400 animate-pulse"
              : "bg-cyan-400"
          }`}
        />

        <span className="w-px flex-1 bg-white/5 mt-2" />

      </div>

      <div className="pb-2">

        <div className="flex items-center gap-3">
          <span className="text-[9px] font-mono text-cyan-400">
            {time}
          </span>

          <h3 className="text-sm font-medium">
            {title}
          </h3>
        </div>

        <p className="text-xs text-slate-600 mt-1">
          {detail}
        </p>

      </div>

    </div>
  )
}

export default AlertsPage