from pydub import AudioSegment
import os

INPUT_FOLDER = "downloads"
OUTPUT_FOLDER = "test_samples/ai_other"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

files = os.listdir(INPUT_FOLDER)

count = 1

for filename in files:

    if not filename.lower().endswith((".mp3", ".wav", ".m4a", ".ogg")):
        continue

    input_file = os.path.join(INPUT_FOLDER, filename)

    audio = AudioSegment.from_file(input_file)

    audio = (
        audio
        .set_frame_rate(16000)
        .set_channels(1)
        .set_sample_width(2)
    )

    output_file = os.path.join(
        OUTPUT_FOLDER,
        f"other_ai_{count:02d}.wav"
    )

    audio.export(output_file, format="wav")

    print(f"Created: {output_file}")

    count += 1

print("\nDone!")