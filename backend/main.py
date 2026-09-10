import os
import re
import json
import wave

import joblib
import pandas as pd
import webrtcvad

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from detector import analyze_audio
from risk_engine import calculate_risk
from prevention_engine import get_prevention_action
from speaker_verification import verify_speaker


# ============================================================
# APP CONFIGURATION
# ============================================================

app = FastAPI()

SPEECH_FOLDER = "speech_segments"
MODEL_FILE = "voice_detector.pkl"

SAMPLE_RATE = 16000

# Browser sends:
# 16 kHz
# 16-bit PCM
# Mono
# 20 ms chunks
FRAME_DURATION_MS = 20

FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
FRAME_BYTES = FRAME_SIZE * 2


# ============================================================
# CREATE SPEECH FOLDER
# ============================================================

os.makedirs(SPEECH_FOLDER, exist_ok=True)


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

model_data = joblib.load(MODEL_FILE)

model = model_data["model"]
features = model_data["features"]

print("================================")
print("🤖 VOICE DETECTION MODEL LOADED")
print("================================")
print("Features:", features)


# ============================================================
# WEBRTC VAD
# ============================================================

vad = webrtcvad.Vad()

# 0 = least aggressive
# 3 = most aggressive
vad.set_mode(2)


# ============================================================
# AUTOMATIC SEGMENT NUMBERING
# ============================================================

def get_next_segment_number():

    numbers = []

    for filename in os.listdir(SPEECH_FOLDER):

        match = re.match(r"speech_(\d+)\.wav$", filename)

        if match:
            numbers.append(int(match.group(1)))

    if numbers:
        return max(numbers) + 1

    return 1


segment_counter = get_next_segment_number()

print(f"📁 Next speech segment: speech_{segment_counter:03d}.wav")


# ============================================================
# SAVE WAV FILE
# ============================================================

def save_wav(audio_data, filename):

    filepath = os.path.join(SPEECH_FOLDER, filename)

    with wave.open(filepath, "wb") as wf:

        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)

        wf.writeframes(audio_data)

    return filepath


# ============================================================
# PROCESS SPEECH SEGMENT
# ============================================================

async def process_speech_segment(
    websocket,
    audio,
    chunks,
    reason,
    segment_number
):

    global segment_counter

    if not audio:
        return

    duration = len(audio) / (SAMPLE_RATE * 2)

    # Ignore extremely short segments
    if duration < 0.3:

        print(
            f"⚠️ Segment {segment_number} ignored "
            f"(too short: {duration:.2f}s)"
        )

        return

    filename = f"speech_{segment_number:03d}.wav"

    filepath = save_wav(audio, filename)

    print("\n================================")
    print("🎤 SPEECH SEGMENT SAVED")
    print("================================")

    print(f"📁 File: {filepath}")
    print(f"⏱️ Duration: {duration:.2f} seconds")
    print(f"🔢 Segment: {segment_number}")
    print(f"🛑 Reason: {reason}")


    # ========================================================
    # AUDIO FEATURE EXTRACTION
    # ========================================================

    try:

        feature_data = analyze_audio(filepath)

        X = pd.DataFrame([feature_data])[features]

    except Exception as e:

        print("❌ Feature extraction error:", e)

        return


    # ========================================================
    # MACHINE LEARNING PREDICTION
    # ========================================================

    try:

        prediction = model.predict(X)[0]

        probabilities = model.predict_proba(X)[0]

        real_score = float(probabilities[0] * 100)

        ai_score = float(probabilities[1] * 100)

        predicted_label = "AI" if prediction == 1 else "REAL"

    except Exception as e:

        print("❌ Model prediction error:", e)

        return


    print("\n================================")
    print("🤖 AI VOICE DETECTION")
    print("================================")

    print(f"Prediction : {predicted_label}")
    print(f"Human Score: {real_score:.1f}%")
    print(f"AI Score   : {ai_score:.1f}%")


    # ========================================================
    # SPEAKER VERIFICATION
    # ========================================================

    try:

        speaker_result = verify_speaker(filepath)

        speaker_match_score = float(
            speaker_result["speaker_match_score"]
        )

        speaker_match = bool(
            speaker_result["speaker_match"]
        )

        speaker_reason = speaker_result["reason"]

    except Exception as e:

        print("❌ Speaker verification error:", e)

        # If speaker verification fails,
        # do not stop the complete voice detector.
        speaker_match_score = 0.0
        speaker_match = False
        speaker_reason = "Speaker verification unavailable."


    print("\n================================")
    print("👤 SPEAKER VERIFICATION")
    print("================================")

    print(
        f"Speaker Match Score : "
        f"{speaker_match_score:.2f}%"
    )

    print(
        f"Speaker Match       : "
        f"{speaker_match}"
    )

    print(
        f"Reason              : "
        f"{speaker_reason}"
    )


    # ========================================================
    # RISK ENGINE
    # ========================================================

    risk = calculate_risk(ai_score, speaker_match)

    risk_level = risk["risk_level"]

    print("\n================================")
    print("⚠️ RISK ASSESSMENT")
    print("================================")

    print(f"Risk Level : {risk_level}")
    print(f"Risk Action: {risk['action']}")
    print(f"Message    : {risk['message']}")


    # ========================================================
    # PREVENTION ENGINE
    # ========================================================

    prevention = get_prevention_action(risk_level)

    print("\n================================")
    print("🛡️ PREVENTION DECISION")
    print("================================")

    print(f"Action      : {prevention['action']}")
    print(f"Status      : {prevention['status']}")
    print(f"Description : {prevention['description']}")


    # ========================================================
    # FINAL RESULT
    # ========================================================

    result = {

        "prediction": predicted_label,

        "real_score": round(real_score, 2),

        "ai_score": round(ai_score, 2),

        "speaker_match_score":
            round(speaker_match_score, 2),

        "speaker_match":
            speaker_match,

        "speaker_reason":
            speaker_reason,

        "risk_level":
            risk_level,

        "action":
            risk["action"],

        "status":
            prevention["status"],

        "message":
            risk["message"],

        "prevention_description":
            prevention["description"],

        "segment":
            segment_number,

        "duration":
            round(duration, 2),

        "reason":
            reason
    }


    # ========================================================
    # SEND RESULT TO FRONTEND
    # ========================================================

    try:

        await websocket.send_text(
            json.dumps(result)
        )

        print("\n📤 Result sent to browser:")

        print(
            json.dumps(
                result,
                indent=2
            )
        )

    except Exception as e:

        print("❌ Could not send result:", e)


# ============================================================
# WEBSOCKET AUDIO ENDPOINT
# ============================================================

@app.websocket("/ws/audio")
async def websocket_audio(websocket: WebSocket):

    global segment_counter

    await websocket.accept()

    print("\n================================")
    print("🔌 WEBSOCKET CONNECTED")
    print("================================")


    # ========================================================
    # SPEECH BUFFER
    # ========================================================

    speech_buffer = bytearray()

    speech_chunks = 0

    silence_chunks = 0


    # ========================================================
    # SEGMENT SETTINGS
    # ========================================================

    MIN_SPEECH_CHUNKS = 15

    MAX_SPEECH_CHUNKS = 250

    SILENCE_LIMIT_CHUNKS = 25


    try:

        while True:

            data = await websocket.receive_bytes()


            # ------------------------------------------------
            # Validate frame size
            # ------------------------------------------------

            if len(data) != FRAME_BYTES:

                print(
                    f"⚠️ Unexpected frame size: "
                    f"{len(data)} bytes"
                )

                continue


            # ------------------------------------------------
            # VAD
            # ------------------------------------------------

            try:

                is_speech = vad.is_speech(
                    data,
                    SAMPLE_RATE
                )

            except Exception as e:

                print("❌ VAD error:", e)

                continue


            # =================================================
            # SPEECH DETECTED
            # =================================================

            if is_speech:

                speech_buffer.extend(data)

                speech_chunks += 1

                silence_chunks = 0


                # ---------------------------------------------
                # Maximum segment length
                # ---------------------------------------------

                if speech_chunks >= MAX_SPEECH_CHUNKS:

                    await process_speech_segment(
                        websocket,
                        bytes(speech_buffer),
                        speech_chunks,
                        "maximum duration",
                        segment_counter
                    )

                    segment_counter += 1

                    speech_buffer = bytearray()

                    speech_chunks = 0

                    silence_chunks = 0


            # =================================================
            # SILENCE
            # =================================================

            else:

                if speech_chunks > 0:

                    speech_buffer.extend(data)

                    silence_chunks += 1


                    # -----------------------------------------
                    # End speech after enough silence
                    # -----------------------------------------

                    if (
                        silence_chunks
                        >= SILENCE_LIMIT_CHUNKS
                    ):

                        if (
                            speech_chunks
                            >= MIN_SPEECH_CHUNKS
                        ):

                            await process_speech_segment(
                                websocket,
                                bytes(speech_buffer),
                                speech_chunks,
                                "silence detected",
                                segment_counter
                            )

                            segment_counter += 1

                        else:

                            print(
                                "⚠️ Speech segment "
                                "too short - ignored"
                            )


                        speech_buffer = bytearray()

                        speech_chunks = 0

                        silence_chunks = 0


    except WebSocketDisconnect:

        print("\n================================")
        print("🔌 WEBSOCKET DISCONNECTED")
        print("================================")


    except Exception as e:

        print("\n❌ WebSocket error:")
        print(e)