from pathlib import Path
import tempfile
import uuid
import wave
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from inference.detector import detect_voice
from risk_engine import get_risk_result

from backend_student5.app.services.audio_pipeline import (
    create_audio_pipeline,
)

router = APIRouter()


def save_segment_as_wav(audio_data: bytes) -> Path:
    """
    Convert raw 16-bit mono 16 kHz PCM audio into a temporary WAV file.
    """

    temp_dir = Path(tempfile.gettempdir()) / "voxshield_segments"
    temp_dir.mkdir(parents=True, exist_ok=True)

    filename = f"segment_{uuid.uuid4().hex}.wav"
    filepath = temp_dir / filename

    with wave.open(str(filepath), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(audio_data)

    return filepath


def build_risk_result(detection: dict) -> dict:
    """
    Connect Student 1's AI probability to Student 3's risk engine.

    Until the speaker-verification, caller-risk, transaction-risk,
    and behavioral-risk modules are connected, those inputs use
    neutral values.
    """

    ai_probability = float(detection["ai_probability"])

    return get_risk_result(
        ai_probability=ai_probability,
        speaker_mismatch=0.0,
        caller_risk=0.0,
        transaction_risk=0.0,
        behavioral_risk=0.0,
    )


async def analyze_segment(audio_data: bytes):
    """
    Run Student 1 detection and Student 3 risk analysis.

    The model is synchronous, so it runs in a worker thread to avoid
    blocking the WebSocket event loop.
    """

    filepath = save_segment_as_wav(audio_data)

    try:
        detection = await asyncio.to_thread(
            detect_voice,
            str(filepath),
        )

        risk = build_risk_result(detection)

        return detection, risk

    finally:
        filepath.unlink(missing_ok=True)


@router.websocket("/ws/audio")
async def audio_stream(websocket: WebSocket):
    await websocket.accept()

    pipeline = create_audio_pipeline()

    try:
        await websocket.send_json({
            "status": "connected",
            "message": "VoxShield audio stream connected",
        })

        while True:
            frame = await websocket.receive_bytes()

            segment = pipeline.process_frame(frame)

            if segment is None:
                continue

            try:
                detection, risk = await analyze_segment(
                    segment["audio"]
                )

                await websocket.send_json({
                    "status": "analyzed",

                    "segment": {
                        "duration": segment["duration"],
                        "reason": segment["reason"],
                    },

                    "detection": detection,

                    "risk": risk,

                    "audit": None,
                })

            except Exception as exc:
                await websocket.send_json({
                    "status": "error",
                    "detail": f"Audio analysis failed: {str(exc)}",
                })

    except WebSocketDisconnect:
        print("Audio WebSocket disconnected")