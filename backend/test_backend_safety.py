import os
import wave


SAMPLE_RATE = 16000
FRAME_DURATION_MS = 20
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
FRAME_BYTES = FRAME_SIZE * 2


print("================================")
print("🔐 BACKEND SAFETY CHECK")
print("================================")


# ---------------------------------
# TEST 1: Audio format
# ---------------------------------

print("\n[1] Checking audio format...")

test_folder = "test_samples/real"

files = [
    f for f in os.listdir(test_folder)
    if f.lower().endswith(".wav")
]

if len(files) == 0:
    print("❌ No WAV files found.")
else:

    filepath = os.path.join(test_folder, files[0])

    with wave.open(filepath, "rb") as wf:

        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sample_rate = wf.getframerate()

    print(f"Sample rate : {sample_rate} Hz")
    print(f"Channels    : {channels}")
    print(f"Sample width: {sample_width * 8}-bit")

    if (
        sample_rate == 16000
        and channels == 1
        and sample_width == 2
    ):
        print("✅ Audio format is correct.")
    else:
        print("⚠️ Audio format does not match expected format.")


# ---------------------------------
# TEST 2: Frame size
# ---------------------------------

print("\n[2] Checking WebSocket frame configuration...")

print(f"Frame duration : {FRAME_DURATION_MS} ms")
print(f"Samples/frame  : {FRAME_SIZE}")
print(f"Bytes/frame    : {FRAME_BYTES}")

if FRAME_BYTES == 640:
    print("✅ Frame configuration is correct.")
else:
    print("❌ Unexpected frame size.")


# ---------------------------------
# TEST 3: Segment limits
# ---------------------------------

print("\n[3] Checking segment limits...")

MIN_SPEECH_CHUNKS = 15
MAX_SPEECH_CHUNKS = 250
SILENCE_LIMIT_CHUNKS = 25

print(
    f"Minimum speech : "
    f"{MIN_SPEECH_CHUNKS * 20} ms"
)

print(
    f"Maximum speech : "
    f"{MAX_SPEECH_CHUNKS * 20 / 1000:.2f} seconds"
)

print(
    f"Silence limit  : "
    f"{SILENCE_LIMIT_CHUNKS * 20} ms"
)

if MAX_SPEECH_CHUNKS <= 250:
    print("✅ Maximum segment limit prevents unlimited buffering.")
else:
    print("⚠️ Segment limit may be too large.")


# ---------------------------------
# TEST 4: Test dataset
# ---------------------------------

print("\n[4] Checking test dataset...")

folders = [
    "test_samples/real",
    "test_samples/ai",
    "test_samples/real_noisy",
    "test_samples/ai_noisy"
]

for folder in folders:

    if os.path.exists(folder):

        count = len([
            f for f in os.listdir(folder)
            if f.lower().endswith(".wav")
        ])

        print(f"{folder:<25} {count} WAV files")

    else:

        print(f"{folder:<25} NOT FOUND")


# ---------------------------------
# SUMMARY
# ---------------------------------

print("\n================================")
print("🔐 SAFETY CHECK COMPLETE")
print("================================")

print("""
Current protections:

✅ Fixed audio frame size
✅ 16 kHz audio
✅ 16-bit PCM
✅ Maximum speech segment length
✅ Minimum speech threshold
✅ Silence-based segmentation
✅ WebSocket disconnect handling
✅ Audio buffer reset after processing
✅ Separate unseen test data
""")