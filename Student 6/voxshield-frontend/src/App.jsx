import { useEffect, useState } from "react"
import Sidebar from "./components/Sidebar"
import Header from "./components/Header"
import SystemStatus from "./components/SystemStatus"
import VoiceProbability from "./components/VoiceProbability"
import RiskScore from "./components/RiskScore"
import ThreatLevel from "./components/ThreatLevel"
import LiveCallCard from "./components/LiveCallCard"
import AlertsPanel from "./components/AlertsPanel"
import RecommendedAction from "./components/RecommendedAction"
import BlockchainAudit from "./components/BlockchainAudit"
import SecurityTimeline from "./components/SecurityTimeline"
import { initialSecurityState } from "./data/securityState"
import ThreatIntelligence from "./components/ThreatIntelligence"
import LiveCallsPage from "./components/LiveCallsPage"
import ThreatDetectionPage from "./components/ThreatDetectionPage"
import AlertsPage from "./components/AlertsPage"
import SecurityEventsPage from "./components/SecurityEventsPage"
import BlockchainAuditPage from "./components/BlockchainAuditPage"
import SystemStatusPage from "./components/SystemStatusPage"
import SettingsPage from "./components/SettingsPage"
import SystemStatusBanner from "./components/SystemStatusBanner"
import SecurityLoading from "./components/SecurityLoading"
import SecurityError from "./components/SecurityError"
import { normalizeSecurityData } from "./data/securityAdapter"
import {
  getMockScenario,
} from "./data/mockSecurityStream"

function formatDuration(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`
}
function PagePlaceholder({ title, description }) {
  return (
    <div className="dashboard-card">

      <div className="rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-8">

        <p className="text-xs uppercase tracking-[0.25em] text-cyan-400">
          VoxShield Module
        </p>

        <h1 className="text-3xl font-bold mt-3">
          {title}
        </h1>

        <p className="text-sm text-slate-500 mt-3 max-w-xl">
          {description}
        </p>

        <div className="mt-8 flex items-center gap-3">

          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />

          <span className="text-xs text-cyan-400 uppercase tracking-wider">
            Module Ready
          </span>

        </div>

      </div>

    </div>
  )
}
function App() {
  console.log("Mock scenario 1:", getMockScenario(0))
console.log("Mock scenario 2:", getMockScenario(1))
console.log("Mock scenario 3:", getMockScenario(2))
console.log("Mock scenario 4:", getMockScenario(3))
console.log("Mock scenario 5:", getMockScenario(4))
console.log("Mock scenario 6:", getMockScenario(5))
  const [securityState, setSecurityState] = useState(
    normalizeSecurityData(initialSecurityState)
  )
  const [activePage, setActivePage] = useState("Overview")
  const [isInitializing, setIsInitializing] = useState(true)
  const [hasSecurityError, setHasSecurityError] = useState(false)
  useEffect(() => {
  let scenarioIndex = 0

  const interval = setInterval(() => {
    const scenario = getMockScenario(scenarioIndex)

    const normalizedScenario =
      normalizeSecurityData(scenario)

    setSecurityState((previous) => ({
      ...previous,
      ...normalizedScenario,
      callDuration: previous.callDuration + 3,
    }))

    scenarioIndex += 1
  }, 3000)

  return () => clearInterval(interval)
}, [])

useEffect(() => {
  const timer = setTimeout(() => {
    setIsInitializing(false)
  }, 1200)

  return () => clearTimeout(timer)
}, [])

  return (
    <div className="relative min-h-screen bg-[#050914] text-white flex overflow-hidden">
      {/* Animated Cyber Environment */}
      <div className="pointer-events-none fixed inset-0 cyber-grid opacity-40" />
      <div className="pointer-events-none fixed -top-40 left-1/3 w-[500px] h-[500px] rounded-full bg-cyan-400/5 blur-[120px] ambient-glow" />
      <div className="pointer-events-none fixed -bottom-40 right-1/4 w-[450px] h-[450px] rounded-full bg-violet-500/5 blur-[120px] ambient-glow" />
      <div className="pointer-events-none fixed inset-x-0 top-0 h-[2px] bg-cyan-400/20 blur-sm scan-line" />
      <Sidebar 
      activePage={activePage}
      onNavigate={setActivePage}
      />

      <main className="flex-1 min-w-0">

        <Header />

        <section className="p-4 sm:p-6 lg:p-8">
  {isInitializing ? (
  <SecurityLoading />
) : hasSecurityError ? (
  <SecurityError
    onRetry={() => setHasSecurityError(false)}
  />
) :activePage === "Live Calls" ? (
  <LiveCallsPage securityState={securityState} />
) : activePage === "Threat Detection" ? (
  <ThreatDetectionPage securityState={securityState} />
) : activePage === "Alerts" ? (
  <AlertsPage alerts={securityState.alerts} />
) : activePage === "Security Events" ? (
  <SecurityEventsPage securityState={securityState} />
) : activePage === "Blockchain Audit" ? (
  <BlockchainAuditPage securityState={securityState} />
) : activePage === "System Status" ? (
  <SystemStatusPage />
): activePage === "Settings" ? (
  <SettingsPage />
) : activePage !== "Overview" ? (
  <PagePlaceholder
    title={activePage}
    description={`The ${activePage} module is ready for integration with the VoxShield security pipeline.`}
  />
) : (

          <div className="mb-8">

            <p className="text-xs uppercase tracking-[0.25em] text-cyan-400">
              Threat Monitoring
            </p>

            <h1 className="text-2xl sm:text-3xl font-bold mt-2">
              Security Overview
            </h1>
            <div className="flex items-center gap-2 mt-4">
              <span className="relative flex h-2.5 w-2.5">
                <span className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60 animate-ping" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400" />
              </span>
              <span className="text-[10px] uppercase tracking-widest text-emerald-400">
                Live threat monitoring active
              </span>
            </div>

            <p className="text-xs sm:text-sm text-slate-500 mt-2">
              Monitor live voice threats and impersonation attempts.
            </p>  

            <div className="mt-6">
  <SystemStatusBanner
    status={
      isInitializing
        ? "LOADING"
        : hasSecurityError
          ? "ERROR"
          : "ONLINE"
    }
    message={
      isInitializing
        ? "Initializing security services..."
        : hasSecurityError
          ? "Security pipeline connection interrupted."
          : "All security services operational"
    }
  />
</div>

            

          </div>
            )}
          {/* Security Metrics */}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            <div className="dashboard-card delay-1">
              <VoiceProbability
              probability={securityState.aiProbability}
              />
            </div>
            <div className="dashboard-card delay-2">
              <RiskScore
                score={securityState.riskScore}
              />
            </div>
            <div className="dashboard-card delay-3">
              <ThreatLevel
                level={securityState.threatLevel}
              />
            </div>

          </div>
          {/* Live Call */}
          <div className="mt-5 dashboard-card delay-4">
            <LiveCallCard securityState={{
              ...securityState,
              callDuration: formatDuration(securityState.callDuration),
            }}
            />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-5">

            <div className="dashboard-card delay-5">
            <AlertsPanel alerts={securityState.alerts} />
            </div>
            <div className="dashboard-card delay-6">
              <RecommendedAction />
            </div>
            <ThreatIntelligence
  history={securityState.threatHistory}
/>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-5">
            <div className="dashboard-card delay-4">
              <BlockchainAudit />
            </div>
            <div className="dashboard-card delay-5">
              <SecurityTimeline />
            </div>
          </div>
          <div className="mt-5 dashboard-card delay-6">
            <SystemStatus />
          </div>

        </section>

      </main>

    </div>
  )
}

export default App