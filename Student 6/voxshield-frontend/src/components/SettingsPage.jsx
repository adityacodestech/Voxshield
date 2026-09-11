import { useState } from "react"

function SettingsPage() {
  const [aiThreshold, setAiThreshold] = useState(80)
  const [riskThreshold, setRiskThreshold] = useState(70)

  const [realTimeAlerts, setRealTimeAlerts] = useState(true)
  const [soundAlerts, setSoundAlerts] = useState(true)
  const [autoBlock, setAutoBlock] = useState(true)
  const [highSensitivity, setHighSensitivity] = useState(true)

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="dashboard-card">
        <div className="rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-6 sm:p-8">
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-400">
            Security Configuration
          </p>

          <h1 className="text-2xl sm:text-3xl font-bold mt-2">
            System Settings
          </h1>

          <p className="text-sm text-slate-500 mt-2 max-w-2xl">
            Configure VoxShield detection sensitivity, threat thresholds,
            alerts, and automated security responses.
          </p>
        </div>
      </div>

      {/* Detection Settings */}
      <section className="dashboard-card delay-1 rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-5 sm:p-6">

        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-cyan-400/10 flex items-center justify-center text-cyan-400">
            ◈
          </div>

          <div>
            <h2 className="font-semibold">Detection Engine</h2>
            <p className="text-xs text-slate-500">
              Configure AI voice detection behavior
            </p>
          </div>
        </div>

        <div className="space-y-7">

          {/* AI Threshold */}
          <SliderSetting
            title="AI Voice Detection Threshold"
            description="Minimum probability required to classify audio as synthetic."
            value={aiThreshold}
            min={50}
            max={99}
            onChange={setAiThreshold}
          />

          {/* Risk Threshold */}
          <SliderSetting
            title="High Risk Threshold"
            description="Risk score at which a call enters the high-risk state."
            value={riskThreshold}
            min={40}
            max={95}
            onChange={setRiskThreshold}
          />

          {/* Sensitivity */}
          <ToggleSetting
            title="High Sensitivity Mode"
            description="Increase detection sensitivity for suspicious voice patterns."
            enabled={highSensitivity}
            onToggle={() => setHighSensitivity(!highSensitivity)}
          />

        </div>
      </section>

      {/* Alert Settings */}
      <section className="dashboard-card delay-2 rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-5 sm:p-6">

        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-violet-400/10 flex items-center justify-center text-violet-400">
            !
          </div>

          <div>
            <h2 className="font-semibold">Alert Management</h2>
            <p className="text-xs text-slate-500">
              Control security notifications
            </p>
          </div>
        </div>

        <div className="space-y-5">

          <ToggleSetting
            title="Real-Time Security Alerts"
            description="Display threat notifications immediately when detected."
            enabled={realTimeAlerts}
            onToggle={() => setRealTimeAlerts(!realTimeAlerts)}
          />

          <ToggleSetting
            title="Sound Alerts"
            description="Play an audio notification when a critical threat is detected."
            enabled={soundAlerts}
            onToggle={() => setSoundAlerts(!soundAlerts)}
          />

        </div>
      </section>

      {/* Automated Response */}
      <section className="dashboard-card delay-3 rounded-2xl border border-red-400/10 bg-[#080f1d] p-5 sm:p-6">

        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-red-400/10 flex items-center justify-center text-red-400">
            !
          </div>

          <div>
            <h2 className="font-semibold">Automated Response</h2>
            <p className="text-xs text-slate-500">
              Configure automated threat prevention
            </p>
          </div>
        </div>

        <ToggleSetting
          title="Automatically Block Critical Threats"
          description="Block sensitive transactions when the risk engine detects a critical threat."
          enabled={autoBlock}
          onToggle={() => setAutoBlock(!autoBlock)}
          danger
        />

      </section>

      {/* Current Configuration */}
      <section className="dashboard-card delay-4 rounded-2xl border border-emerald-400/10 bg-[#080f1d] p-5 sm:p-6">

        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="font-semibold">Active Configuration</h2>
            <p className="text-xs text-slate-500 mt-1">
              Current frontend security configuration
            </p>
          </div>

          <span className="px-3 py-1 rounded-full bg-emerald-400/10 text-emerald-400 text-[10px] uppercase tracking-wider">
            Active
          </span>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">

          <ConfigCard
            label="AI Threshold"
            value={`${aiThreshold}%`}
          />

          <ConfigCard
            label="Risk Threshold"
            value={riskThreshold}
          />

          <ConfigCard
            label="Sensitivity"
            value={highSensitivity ? "HIGH" : "NORMAL"}
          />

          <ConfigCard
            label="Auto Block"
            value={autoBlock ? "ON" : "OFF"}
          />

        </div>
      </section>

    </div>
  )
}


function SliderSetting({
  title,
  description,
  value,
  min,
  max,
  onChange,
}) {
  return (
    <div>

      <div className="flex items-start justify-between gap-4 mb-3">

        <div>
          <h3 className="text-sm font-medium">
            {title}
          </h3>

          <p className="text-xs text-slate-500 mt-1">
            {description}
          </p>
        </div>

        <span className="text-cyan-400 font-bold text-lg">
          {value}%
        </span>

      </div>

      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="w-full accent-cyan-400 cursor-pointer"
      />

      <div className="flex justify-between text-[10px] text-slate-600 mt-1">
        <span>{min}%</span>
        <span>{max}%</span>
      </div>

    </div>
  )
}


function ToggleSetting({
  title,
  description,
  enabled,
  onToggle,
  danger = false,
}) {
  return (
    <div className="flex items-center justify-between gap-4">

      <div>
        <h3 className="text-sm font-medium">
          {title}
        </h3>

        <p className="text-xs text-slate-500 mt-1 max-w-xl">
          {description}
        </p>
      </div>

      <button
        onClick={onToggle}
        className={`
          relative w-12 h-6 rounded-full shrink-0 transition-all duration-300
          ${enabled
            ? danger
              ? "bg-red-400/70"
              : "bg-cyan-400/70"
            : "bg-slate-700"
          }
        `}
      >
        <span
          className={`
            absolute top-1 w-4 h-4 rounded-full bg-white
            transition-all duration-300
            ${enabled ? "left-7" : "left-1"}
          `}
        />
      </button>

    </div>
  )
}


function ConfigCard({ label, value }) {
  return (
    <div className="rounded-xl border border-white/5 bg-black/20 p-4">

      <p className="text-[10px] uppercase tracking-wider text-slate-600">
        {label}
      </p>

      <p className="text-lg font-bold text-slate-200 mt-2">
        {value}
      </p>

    </div>
  )
}


export default SettingsPage