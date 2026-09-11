import os
import re
import wave
import webrtcvad


# ============================================================
# AUDIO FORMAT
# ============================================================

SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH_BYTES = 2

FRAME_DURATION_MS = 20

FRAME_SIZE = int(
    SAMPLE_RATE * FRAME_DURATION_MS / 1000
)

FRAME_BYTES = FRAME_SIZE * SAMPLE_WIDTH_BYTES


# ============================================================
# SEGMENTATION SETTINGS
# ============================================================

MIN_SPEECH_CHUNKS = 15       # 300 ms
MAX_SPEECH_CHUNKS = 250      # 5 seconds
SILENCE_LIMIT_CHUNKS = 25    # 500 ms

MIN_SEGMENT_DURATION = 0.30


# ============================================================
# STORAGE
# ============================================================

SPEECH_FOLDER = "speech_segments"


# ============================================================
# AUDIO PIPELINE
# ============================================================

class AudioPipeline:

    def __init__(self, vad=None):

        if vad is None:
            vad = webrtcvad.Vad()
            vad.set_mode(2)

        self.vad = vad

        self.speech_buffer = bytearray()

        self.speech_chunks = 0
        self.silence_chunks = 0


    # --------------------------------------------------------
    # PROCESS ONE AUDIO FRAME
    # --------------------------------------------------------

    def process_frame(self, data):

        # Validate frame size
        if len(data) != FRAME_BYTES:

            print(
                f"⚠️ Invalid frame size: "
                f"{len(data)} bytes "
                f"(expected {FRAME_BYTES})"
            )

            return None


        # Run Voice Activity Detection
        try:

            is_speech = self.vad.is_speech(
                data,
                SAMPLE_RATE
            )

        except Exception as error:

            print("❌ VAD error:", error)

            return None


        # ----------------------------------------------------
        # SPEECH FRAME
        # ----------------------------------------------------

        if is_speech:

            self.speech_buffer.extend(data)

            self.speech_chunks += 1

            self.silence_chunks = 0


            # Maximum segment duration reached
            if self.speech_chunks >= MAX_SPEECH_CHUNKS:

                return self._create_segment(
                    "maximum duration"
                )


        # ----------------------------------------------------
        # SILENCE FRAME
        # ----------------------------------------------------

        else:

            # Only count silence after speech started
            if self.speech_chunks > 0:

                self.speech_buffer.extend(data)

                self.silence_chunks += 1


                # Enough silence → finish segment
                if (
                    self.silence_chunks
                    >= SILENCE_LIMIT_CHUNKS
                ):

                    if (
                        self.speech_chunks
                        >= MIN_SPEECH_CHUNKS
                    ):

                        return self._create_segment(
                            "silence detected"
                        )

                    else:

                        print(
                            "⚠️ Speech segment too short - ignored"
                        )

                        self._reset()


        return None


    # --------------------------------------------------------
    # CREATE SPEECH SEGMENT
    # --------------------------------------------------------

    def _create_segment(self, reason):

        if not self.speech_buffer:

            self._reset()

            return None


        audio = bytes(self.speech_buffer)


        duration = (
            len(audio)
            / (SAMPLE_RATE * SAMPLE_WIDTH_BYTES)
        )


        # Reject very short segments
        if duration < MIN_SEGMENT_DURATION:

            print(
                f"⚠️ Segment ignored "
                f"(too short: {duration:.2f}s)"
            )

            self._reset()

            return None


        segment = {

            "audio": audio,

            "duration": duration,

            "reason": reason
        }


        self._reset()


        return segment


    # --------------------------------------------------------
    # RESET PIPELINE STATE
    # --------------------------------------------------------

    def _reset(self):

        self.speech_buffer = bytearray()

        self.speech_chunks = 0

        self.silence_chunks = 0


# ============================================================
# WAV OUTPUT
# ============================================================

def save_wav(audio_data, filename):

    os.makedirs(
        SPEECH_FOLDER,
        exist_ok=True
    )


    filepath = os.path.join(
        SPEECH_FOLDER,
        filename
    )


    with wave.open(filepath, "wb") as wav:

        wav.setnchannels(CHANNELS)

        wav.setsampwidth(
            SAMPLE_WIDTH_BYTES
        )

        wav.setframerate(
            SAMPLE_RATE
        )

        wav.writeframes(audio_data)


    return filepath


# ============================================================
# SEGMENT NUMBER
# ============================================================

def get_next_segment_number():

    os.makedirs(
        SPEECH_FOLDER,
        exist_ok=True
    )


    numbers = []


    for filename in os.listdir(
        SPEECH_FOLDER
    ):

        match = re.match(
            r"speech_(\d+)\.wav$",
            filename
        )


        if match:

            numbers.append(
                int(match.group(1))
            )


    if numbers:

        return max(numbers) + 1


    return 1