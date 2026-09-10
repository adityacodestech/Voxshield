import queue
import sys

import numpy as np
import sounddevice as sd
import webrtcvad


# ==========================================
# CONFIGURATION
# ==========================================

SAMPLE_RATE = 16000
CHANNELS = 1

FRAME_DURATION_MS = 20
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)

# Number of milliseconds of speech to collect
WINDOW_DURATION_MS = 1000

# Number of 20 ms frames in 1 second
FRAMES_PER_WINDOW = WINDOW_DURATION_MS // FRAME_DURATION_MS


# ==========================================
# QUEUE
# ==========================================

audio_queue = queue.Queue()


# ==========================================
# VAD
# ==========================================

vad = webrtcvad.Vad()

# 0 = less aggressive
# 3 = more aggressive
vad.set_mode(2)


# ==========================================
# MICROPHONE CALLBACK
# ==========================================

def audio_callback(indata, frames, time, status):

    if status:
        print("Audio status:", status, file=sys.stderr)

    audio_queue.put(indata.copy())


# ==========================================
# PROCESS A COMPLETE SPEECH WINDOW
# ==========================================

def process_speech_window(frames):

    # Combine all frames
    audio = np.concatenate(frames, axis=0)

    print("\n================================")
    print("Speech window detected!")
    print("Samples:", len(audio))
    print("Duration:", len(audio) / SAMPLE_RATE, "seconds")
    print("================================\n")

    # This is where Student 1's
    # AI voice detector will be called.

    return audio


# ==========================================
# MAIN
# ==========================================

def main():

    print("AI Voice Detection Audio Pipeline")
    print("----------------------------------")
    print("Sample rate:", SAMPLE_RATE)
    print("Frame size:", FRAME_SIZE, "samples")
    print("Frame duration:", FRAME_DURATION_MS, "ms")
    print("Analysis window:", WINDOW_DURATION_MS, "ms")
    print("\nSpeak into your microphone.")
    print("Press Ctrl+C to stop.\n")


    speech_frames = []

    try:

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=FRAME_SIZE,
            callback=audio_callback
        ):

            while True:

                # Get next 20 ms frame
                frame = audio_queue.get()

                # Convert to raw PCM bytes
                pcm_bytes = frame.tobytes()

                # Run VAD
                speech = vad.is_speech(
                    pcm_bytes,
                    SAMPLE_RATE
                )

                if speech:

                    print("🗣️", end=" ", flush=True)

                    speech_frames.append(frame)

                    # Have we collected 1 second?
                    if len(speech_frames) >= FRAMES_PER_WINDOW:

                        audio = process_speech_window(
                            speech_frames
                        )

                        # Clear buffer
                        speech_frames = []

                else:

                    print(".", end="", flush=True)


    except KeyboardInterrupt:

        print("\n\nPipeline stopped.")


if __name__ == "__main__":
    main()