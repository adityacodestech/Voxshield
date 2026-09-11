function Header() {
  return (
    <header className="h-20 border-b border-cyan-500/10 bg-[#070c18]/80 backdrop-blur-xl flex items-center justify-between px-4 sm:px-6 lg:px-8">

      {/* Left side */}
      <div className="flex items-center gap-3">

        {/* Mobile logo */}
        <div className="md:hidden w-9 h-9 rounded-lg bg-cyan-400/10 border border-cyan-400/20 flex items-center justify-center text-cyan-400">
          ◈
        </div>

        <div>
          <p className="text-[10px] sm:text-xs text-cyan-400 uppercase tracking-widest">
            Security Command Center
          </p>

          <h2 className="text-base sm:text-xl font-semibold mt-1">
            Real-Time Voice Protection
          </h2>
        </div>

      </div>

      {/* Right side */}
      <div className="flex items-center gap-3 sm:gap-6">

        {/* Connection */}
        <div className="hidden sm:flex items-center gap-2 text-xs text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          Secure Connection
        </div>

        {/* User */}
        <div className="flex items-center gap-2 sm:gap-3">

          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-cyan-400/10 border border-cyan-400/20 flex items-center justify-center text-cyan-400">
            A
          </div>

          <div className="hidden sm:block">
            <p className="text-xs font-medium text-white">
              Security Operator
            </p>

            <p className="text-[10px] text-slate-500">
              SOC Analyst
            </p>
          </div>

        </div>

      </div>

    </header>
  )
}

export default Header