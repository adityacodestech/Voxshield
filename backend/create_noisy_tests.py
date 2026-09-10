import os
import wave
import numpy as np


INPUT_REAL = "test_samples/real"
INPUT_AI = "test_samples/ai"

OUTPUT_REAL = "test_samples/real_noisy"
OUTPUT_AI = "test_samples/ai_noisy"

os.makedirs(OUTPUT_REAL, exist_ok=True)
os.makedirs(OUTPUT_AI, exist_ok=True)


def add_noise(input_file, output_file, noise_level=0.015):
    with wave.open(input_file, "rb") as wf:
        params = wf.getparams()
        frames = wf.readframes(wf.getnframes())

    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)

    # Generate background noise
    noise = np.random.normal(
        0,
        32767 * noise_level,
        len(audio)
    )

    noisy_audio = audio + noise

    # Keep values inside 16-bit audio range
    noisy_audio = np.clip(noisy_audio, -32768, 32767)

    noisy_audio = noisy_audio.astype(np.int16)

    with wave.open(output_file, "wb") as wf:
        wf.setparams(params)
        wf.writeframes(noisy_audio.tobytes())


def process_folder(input_folder, output_folder, prefix):
    files = [
        f for f in os.listdir(input_folder)
        if f.lower().endswith(".wav")
    ]

    files.sort()

    for i, filename in enumerate(files, start=1):

        input_file = os.path.join(input_folder, filename)
        output_file = os.path.join(
            output_folder,
            f"{prefix}_noisy_{i:02d}.wav"
        )

        print(f"Creating {output_file}")

        add_noise(
            input_file,
            output_file,
            noise_level=0.015
        )


print("================================")
print("CREATING NOISY TEST DATA")
print("================================")

process_folder(
    INPUT_REAL,
    OUTPUT_REAL,
    "real"
)

process_folder(
    INPUT_AI,
    OUTPUT_AI,
    "ai"
)

print("\nDone!")