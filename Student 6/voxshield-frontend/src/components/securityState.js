export const initialSecurityState = {
  aiProbability: 94.2,
  riskScore: 87,
  threatLevel: "CRITICAL",

  callStatus: "LIVE",
  callId: "VX-28491",
  callDuration: "04:32",

  audioStream: "ACTIVE",
  microphone: "CONNECTED",

  blockchainStatus: "VERIFIED",

  alerts: [
    {
      title: "Synthetic Voice Detected",
      description: "High probability of AI-generated speech",
      severity: "CRITICAL",
      time: "12 sec ago",
    },
    {
      title: "Speaker Mismatch",
      description: "Voice does not match registered speaker",
      severity: "HIGH",
      time: "28 sec ago",
    },
    {
      title: "High-Risk Transaction",
      description: "Sensitive transaction detected during call",
      severity: "HIGH",
      time: "41 sec ago",
    },
  ],
}