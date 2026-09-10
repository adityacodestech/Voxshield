import queue
import sys

import numpy as np
import sounddevice as sd
import webrtcvad


# -----------------------------
# Audio configuration
# -----------------------------

SAMPLE_RATE = 16000       # 16 kHz
CHANNELS = 1              # Mono
FRAME_DURATION_MS = 20    # 20 ms frames

# Number of samples in one 20 ms frame
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)

# Queue for transferring microphone audio
audio_queue = queue.Queue()

# WebRTC VAD
vad = webrtcvad.Vad()

# VAD aggressiveness:
# 0 = least aggressive
# 3 = most aggressive
vad.set_mode(2)


# -----------------------------
# Microphone callback
# -----------------------------

def audio_callback(indata, frames, time, status):

    if status:
        print("Audio status:", status, file=sys.stderr)

    # Put microphone data into the queue
    audio_queue.put(indata.copy())


# -----------------------------
# Main program
# -----------------------------

def main():

    print("Starting microphone...")
    print("Speak into your microphone.")
    print("Press Ctrl+C to stop.\n")

    try:

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=FRAME_SIZE,
            callback=audio_callback
        ):

            while True:

                # Get one frame from microphone
                audio_frame = audio_queue.get()

                # Convert NumPy array → raw PCM bytes
                pcm_bytes = audio_frame.tobytes()

                # Ask VAD whether speech exists
                is_speech = vad.is_speech(
                    pcm_bytes,
                    SAMPLE_RATE
                )

                if is_speech:
                    print("🗣️  SPEECH")
                else:
                    print("🔇  SILENCE / NON-SPEECH")


    except KeyboardInterrupt:

        print("\nStopping microphone...")


if __name__ == "__main__":
    main()