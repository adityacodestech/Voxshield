import { useEffect, useRef, useState } from "react"
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

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"

const WS_URL = API_BASE_URL
  .replace(/^http:/, "ws:")
  .replace(/^https:/, "wss:") + "/ws/audio"

const FRAME_BYTES = 640
const TARGET_SAMPLE_RATE = 16000

function formatDuration(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = Math.floor(totalSeconds % 60)
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`
}

function downsampleBuffer(buffer, inputSampleRate, outputSampleRate) {
  if (inputSampleRate === outputSampleRate) {
    return buffer
  }

  const sampleRateRatio = inputSampleRate / outputSampleRate
  const newLength = Math.round(buffer.length / sampleRateRatio)
  const result = new Float32Array(newLength)

  let offsetResult = 0
  let offsetBuffer = 0

  while (offsetResult < result.length) {
    const nextOffsetBuffer = Math.round(
      (offsetResult + 1) * sampleRateRatio
    )

    let accum = 0
    let count = 0

    for (
      let i = offsetBuffer;
      i < nextOffsetBuffer && i < buffer.length;
      i += 1
    ) {
      accum += buffer[i]
      count += 1
    }

    result[offsetResult] = count > 0 ? accum / count : 0
    offsetResult += 1
    offsetBuffer = nextOffsetBuffer
  }

  return result
}

function floatTo16BitPCM(float32Array) {
  const buffer = new ArrayBuffer(float32Array.length * 2)
  const view = new DataView(buffer)

  for (let i = 0; i < float32Array.length; i += 1) {
    const sample = Math.max(-1, Math.min(1, float32Array[i]))
    const value = sample < 0 ? sample * 0x8000 : sample * 0x7fff
    view.setInt16(i * 2, value, true)
  }

  return new Uint8Array(buffer)
}

function createAlertFromResult(detection, risk) {
  const alerts = []
  const aiProbability = Number(detection?.ai_probability ?? 0)
  const riskScore = Number(risk?.risk_score ?? 0)

  if (aiProbability >= 0.8) {
    alerts.push({
      title: "Synthetic Voice Detected",
      description: `AI-generated voice probability is ${(aiProbability * 100).toFixed(1)}%.`,
      severity: risk?.severity || "HIGH",
      time: "Just now",
    })
  }

  if (riskScore >= 60) {
    alerts.push({
      title: "High Risk Voice Event",
      description: `Security risk score reached ${riskScore}/100.`,
      severity: risk?.severity || "HIGH",
      time: "Just now",
    })
  }

  return alerts
}

function PagePlaceholder({ title, description }) {
  return (
    <div className="dashboard-card">
      <div className="rounded-2xl border border-cyan-400/10 bg-[#080f1d] p-8">
        <p className="text-xs uppercase tracking-[0.25em] text-cyan-400">
          VoxShield Module
        </p>

        <h1 className="text-3xl font-bold mt-3">{title}</h1>

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
  const [securityState, setSecurityState] = useState(
    normalizeSecurityData(initialSecurityState)
  )
  const [activePage, setActivePage] = useState("Overview")
  const [isInitializing, setIsInitializing] = useState(true)
  const [hasSecurityError, setHasSecurityError] = useState(false)
  const [streamStatus, setStreamStatus] = useState("CONNECTING")
  const [streamError, setStreamError] = useState("")

  const websocketRef = useRef(null)
  const audioContextRef = useRef(null)
  const mediaStreamRef = useRef(null)
  const processorRef = useRef(null)
  const sourceRef = useRef(null)
  const audioBufferRef = useRef(new Uint8Array(0))

  useEffect(() => {
    let mounted = true
    let durationTimer = null

    const cleanupAudio = () => {
      if (processorRef.current) {
        processorRef.current.onaudioprocess = null
        processorRef.current.disconnect()
        processorRef.current = null
      }

      if (sourceRef.current) {
        sourceRef.current.disconnect()
        sourceRef.current = null
      }

      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop())
        mediaStreamRef.current = null
      }

      if (audioContextRef.current) {
        audioContextRef.current.close().catch(() => {})
        audioContextRef.current = null
      }

      audioBufferRef.current = new Uint8Array(0)
    }

    const cleanup = () => {
      if (durationTimer) {
        clearInterval(durationTimer)
      }

      cleanupAudio()

      if (websocketRef.current) {
        websocketRef.current.close()
        websocketRef.current = null
      }
    }

    const appendAudioBytes = (bytes) => {
      const previous = audioBufferRef.current
      const combined = new Uint8Array(previous.length + bytes.length)

      combined.set(previous)
      combined.set(bytes, previous.length)

      let offset = 0

      while (
        offset + FRAME_BYTES <= combined.length &&
        websocketRef.current?.readyState === WebSocket.OPEN
      ) {
        websocketRef.current.send(combined.slice(offset, offset + FRAME_BYTES))
        offset += FRAME_BYTES
      }

      audioBufferRef.current = combined.slice(offset)
    }

    const startMicrophone = async () => {
      try {
        if (!navigator.mediaDevices?.getUserMedia) {
          throw new Error("Microphone access is not supported by this browser.")
        }

        setStreamStatus("REQUESTING_MIC")

        const mediaStream = await navigator.mediaDevices.getUserMedia({
          audio: {
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
          },
        })

        if (!mounted) {
          mediaStream.getTracks().forEach((track) => track.stop())
          return
        }

        mediaStreamRef.current = mediaStream

        const audioContext = new AudioContext()
        audioContextRef.current = audioContext

        const source = audioContext.createMediaStreamSource(mediaStream)
        sourceRef.current = source

        const processor = audioContext.createScriptProcessor(4096, 1, 1)
        processorRef.current = processor

        const silentGain = audioContext.createGain()
        silentGain.gain.value = 0

        processor.onaudioprocess = (event) => {
          if (websocketRef.current?.readyState !== WebSocket.OPEN) {
            return
          }

          const input = event.inputBuffer.getChannelData(0)

          const downsampled = downsampleBuffer(
            input,
            audioContext.sampleRate,
            TARGET_SAMPLE_RATE
          )

          const pcmBytes = floatTo16BitPCM(downsampled)
          appendAudioBytes(pcmBytes)
        }

        source.connect(processor)
        processor.connect(silentGain)
        silentGain.connect(audioContext.destination)

        if (audioContext.state === "suspended") {
          await audioContext.resume()
        }

        setSecurityState((previous) => ({
          ...previous,
          microphone: "CONNECTED",
          audioStream: "ACTIVE",
          callStatus: "LIVE",
        }))

        durationTimer = setInterval(() => {
          setSecurityState((previous) => ({
            ...previous,
            callDuration: previous.callDuration + 1,
          }))
        }, 1000)
      } catch (error) {
        if (!mounted) return

        console.error("Microphone error:", error)
        setStreamStatus("ERROR")
        setStreamError(error.message || "Unable to access microphone.")
        setHasSecurityError(true)
      }
    }

    const connectWebSocket = () => {
      try {
        setStreamStatus("CONNECTING")

        const websocket = new WebSocket(WS_URL)
        websocket.binaryType = "arraybuffer"
        websocketRef.current = websocket

        websocket.onopen = () => {
          if (!mounted) return

          setStreamStatus("CONNECTED")
          setHasSecurityError(false)
          setStreamError("")
        }

        websocket.onmessage = (event) => {
          if (!mounted) return

          try {
            const data = JSON.parse(event.data)

            if (data.status === "connected") {
              setStreamStatus("LIVE")
              return
            }

            if (data.status === "error") {
              setStreamStatus("ERROR")
              setStreamError(data.detail || "Audio analysis failed.")
              return
            }

            if (data.status !== "analyzed") {
              return
            }

            const detection = data.detection || {}
            const risk = data.risk || {}
            const audit = data.audit || {}

            const rawAiProbability = Number(
              detection.ai_probability ?? detection.aiProbability ?? 0
            )

            const aiProbability =
              rawAiProbability <= 1
                ? rawAiProbability * 100
                : rawAiProbability

            const riskScore = Number(
              risk.risk_score ?? risk.riskScore ?? 0
            )

            const threatLevel =
              risk.severity ||
              (riskScore >= 81
                ? "CRITICAL"
                : riskScore >= 61
                  ? "HIGH"
                  : riskScore >= 31
                    ? "MEDIUM"
                    : "LOW")

            const newAlerts = createAlertFromResult(detection, risk)

            setSecurityState((previous) => ({
              ...previous,
              aiProbability,
              riskScore,
              threatLevel,
              callStatus: "LIVE",
              microphone: "CONNECTED",
              audioStream: "ACTIVE",
              blockchainStatus:
                audit.status === "recorded"
                  ? "VERIFIED"
                  : audit.status === "unavailable"
                    ? "UNAVAILABLE"
                    : audit.status || "UNKNOWN",
              threatHistory: [
                ...previous.threatHistory.slice(-10),
                riskScore,
              ],
              alerts: [
                ...newAlerts,
                ...previous.alerts,
              ].slice(0, 6),
            }))

            setStreamStatus("LIVE")
          } catch (error) {
            console.error("Invalid backend message:", error)
          }
        }

        websocket.onerror = () => {
          if (!mounted) return

          setStreamStatus("ERROR")
          setStreamError(
            "Unable to connect to the VoxShield audio backend."
          )
        }

        websocket.onclose = () => {
          if (!mounted) return

          setStreamStatus("DISCONNECTED")
        }
      } catch (error) {
        if (!mounted) return

        setStreamStatus("ERROR")
        setStreamError(error.message || "WebSocket connection failed.")
      }
    }

    const timer = setTimeout(async () => {
      if (!mounted) return

      setIsInitializing(false)
      connectWebSocket()
      await startMicrophone()
    }, 1200)

    return () => {
      mounted = false
      clearTimeout(timer)
      cleanup()
    }
  }, [])

  const retryConnection = () => {
    window.location.reload()
  }

  const bannerStatus =
    isInitializing
      ? "LOADING"
      : hasSecurityError
        ? "ERROR"
        : streamStatus === "LIVE" || streamStatus === "CONNECTED"
          ? "ONLINE"
          : "LOADING"

  const bannerMessage =
    isInitializing
      ? "Initializing security services..."
      : hasSecurityError
        ? streamError || "Security pipeline connection interrupted."
        : streamStatus === "LIVE"
          ? "Live microphone analysis and blockchain audit active"
          : "Connecting to live voice security pipeline..."

  return (
    <div className="relative min-h-screen bg-[#050914] text-white flex overflow-hidden">
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
            <SecurityError onRetry={retryConnection} />
          ) : activePage === "Live Calls" ? (
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
          ) : activePage === "Settings" ? (
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
                  status={bannerStatus}
                  message={bannerMessage}
                />
              </div>
            </div>
          )}

          {!isInitializing && !hasSecurityError && activePage === "Overview" && (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
                <div className="dashboard-card delay-1">
                  <VoiceProbability
                    probability={securityState.aiProbability}
                  />
                </div>

                <div className="dashboard-card delay-2">
                  <RiskScore score={securityState.riskScore} />
                </div>

                <div className="dashboard-card delay-3">
                  <ThreatLevel level={securityState.threatLevel} />
                </div>
              </div>

              <div className="mt-5 dashboard-card delay-4">
                <LiveCallCard
                  securityState={{
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
                  <BlockchainAudit
                    securityState={securityState}
                  />
                </div>

                <div className="dashboard-card delay-5">
                  <SecurityTimeline />
                </div>
              </div>

              <div className="mt-5 dashboard-card delay-6">
                <SystemStatus />
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  )
}

export default App

