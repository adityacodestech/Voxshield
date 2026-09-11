function SecurityTimeline() {
  const events = [
    {
      time: "20:51:42",
      title: "Live call started",
      description: "Secure audio stream established",
      type: "SYSTEM",
    },
    {
      time: "20:52:06",
      title: "AI voice analysis completed",
      description: "94.2% synthetic voice probability",
      type: "DETECTION",
    },
    {
      time: "20:52:18",
      title: "Speaker mismatch detected",
      description: "Voice identity verification failed",
      type: "WARNING",
    },
    {
      time: "20:52:31",
      title: "Risk score escalated",
      description: "Impersonation risk reached 87/100",
      type: "CRITICAL",
    },
    {
      time: "20:52:35",
      title: "Security response recommended",
      description: "Transaction should be blocked",
      type: "ACTION",
    },
  ]

  return (
    <div className="rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6">

      <div className="mb-7">

        <p className="text-xs uppercase tracking-widest text-slate-500">
          Event Stream
        </p>

        <h2 className="text-lg font-semibold mt-2">
          Security Activity
        </h2>

      </div>

      <div className="relative">

        {/* Timeline line */}
        <div className="absolute left-[7px] top-2 bottom-2 w-px bg-cyan-400/10" />

        <div className="space-y-6">

          {events.map((event, index) => (
            <div key={index} className="relative flex gap-4">

              {/* Dot */}
              <div className="relative z-10 mt-1.5 w-3.5 h-3.5 rounded-full bg-[#080f1d] border border-cyan-400/50 flex-shrink-0">

                <div className="absolute inset-1 rounded-full bg-cyan-400" />

              </div>

              {/* Content */}
              <div className="flex-1">

                <div className="flex flex-wrap items-center justify-between gap-2">

                  <h3 className="text-sm font-medium text-slate-200">
                    {event.title}
                  </h3>

                  <span className="text-[9px] text-slate-600">
                    {event.time}
                  </span>

                </div>

                <p className="text-xs text-slate-500 mt-1">
                  {event.description}
                </p>

                <span className="inline-block text-[9px] text-cyan-400/70 mt-2">
                  {event.type}
                </span>

              </div>

            </div>
          ))}

        </div>

      </div>

    </div>
  )
}

export default SecurityTimeline