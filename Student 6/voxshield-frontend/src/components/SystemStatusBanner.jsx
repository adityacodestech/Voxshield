function SystemStatusBanner({
  status = "ONLINE",
  message = "All security services operational",
}) {
  const statusConfig = {
    ONLINE: {
      color: "emerald",
      label: "SYSTEM OPERATIONAL",
    },
    LOADING: {
      color: "amber",
      label: "SYSTEM INITIALIZING",
    },
    ERROR: {
      color: "red",
      label: "SYSTEM ERROR",
    },
  }

  const config = statusConfig[status] || statusConfig.ERROR

  const colorClasses = {
    emerald: {
      border: "border-emerald-400/10",
      background: "bg-emerald-400/5",
      dot: "bg-emerald-400",
      text: "text-emerald-400",
    },
    amber: {
      border: "border-amber-400/10",
      background: "bg-amber-400/5",
      dot: "bg-amber-400",
      text: "text-amber-400",
    },
    red: {
      border: "border-red-400/10",
      background: "bg-red-400/5",
      dot: "bg-red-400",
      text: "text-red-400",
    },
  }

  const colors = colorClasses[config.color]

  return (
    <div
      className={`
        flex flex-col sm:flex-row
        sm:items-center sm:justify-between
        gap-3 px-4 py-3 rounded-xl
        border ${colors.border}
        ${colors.background}
      `}
    >
      <div className="flex items-center gap-3">
        <span className="relative flex h-2.5 w-2.5">
          <span
            className={`
              absolute inline-flex h-full w-full
              rounded-full opacity-50
              ${colors.dot}
              ${status === "LOADING" ? "animate-ping" : ""}
            `}
          />

          <span
            className={`
              relative inline-flex
              rounded-full h-2.5 w-2.5
              ${colors.dot}
            `}
          />
        </span>

        <span
          className={`
            text-[10px] font-semibold
            uppercase tracking-widest
            ${colors.text}
          `}
        >
          {config.label}
        </span>
      </div>

      <span className="text-xs text-slate-500">
        {message}
      </span>
    </div>
  )
}

export default SystemStatusBanner