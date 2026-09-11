function Sidebar({ activePage, onNavigate }) {
  const navigation = [
    {
      section: "Command Center",
      items: [
        { icon: "⌂", label: "Overview" },
        { icon: "◉", label: "Live Calls" },
        { icon: "◈", label: "Threat Detection" },
        { icon: "!", label: "Alerts" },
        { icon: "◷", label: "Security Events" },
        { icon: "⬡", label: "Blockchain Audit" },
      ],
    },
    {
      section: "System",
      items: [
        { icon: "✓", label: "System Status" },
        { icon: "⚙", label: "Settings" },
      ],
    },
  ]

  return (
    <aside className="hidden md:flex w-64 min-h-screen border-r border-cyan-500/10 bg-[#070c18] p-5 flex-col shrink-0">

      {/* Logo */}
      <div className="mb-10">
        <div className="flex items-center gap-3">

          <div className="w-10 h-10 rounded-xl bg-cyan-400/10 border border-cyan-400/30 flex items-center justify-center text-cyan-400 text-xl">
            ◈
          </div>

          <div>
            <h1 className="text-lg font-bold tracking-widest text-white">
              VOXSHIELD
            </h1>

            <p className="text-[10px] text-cyan-400 tracking-wider">
              VOICE SECURITY
            </p>
          </div>

        </div>
      </div>

      {/* Navigation */}
      <nav className="space-y-7">

        {navigation.map((group) => (
          <div key={group.section}>

            <p className="text-[10px] uppercase tracking-widest text-slate-500 mb-3">
              {group.section}
            </p>

            <div className="space-y-1">

              {group.items.map((item) => (
                <NavItem
                  key={item.label}
                  icon={item.icon}
                  label={item.label}
                  active={activePage === item.label}
                  onClick={() => onNavigate(item.label)}
                />
              ))}

            </div>

          </div>
        ))}

      </nav>

      {/* Bottom status */}
      <div className="mt-auto">

        <div className="rounded-xl border border-emerald-400/20 bg-emerald-400/5 p-4">

          <div className="flex items-center gap-2">

            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />

            <span className="text-xs font-medium text-emerald-400">
              SYSTEM ONLINE
            </span>

          </div>

          <p className="text-[10px] text-slate-500 mt-2">
            All security modules operational
          </p>

        </div>

      </div>

    </aside>
  )
}

function NavItem({ icon, label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`
        w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
        text-sm cursor-pointer transition-all duration-300
        text-left
        ${
          active
            ? "bg-cyan-400/10 text-cyan-400 border border-cyan-400/10 shadow-[0_0_20px_rgba(34,211,238,0.04)]"
            : "text-slate-400 hover:text-white hover:bg-white/5"
        }
      `}
    >
      <span className="w-5 text-center">
        {icon}
      </span>

      <span>{label}</span>

      {active && (
        <span className="ml-auto w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
      )}
    </button>
  )
}

export default Sidebar