from gtts import gTTS
from pydub import AudioSegment
import os

OUTPUT_FOLDER = "test_samples/ai"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

sentences = [
    "Your account security verification is required before continuing.",
    "The caller requested an urgent change to the registered account.",
    "Please confirm the identity of the person making this request.",
    "Our security system detected unusual communication activity.",
    "The transaction cannot proceed until additional verification is completed."
]

for i, text in enumerate(sentences, start=1):

    mp3_file = f"temp_ai_{i}.mp3"
    wav_file = os.path.join(
        OUTPUT_FOLDER,
        f"ai_test_{i:02d}.wav"
    )

    print(f"Generating {wav_file}...")

    tts = gTTS(text=text, lang="en")
    tts.save(mp3_file)

    audio = AudioSegment.from_mp3(mp3_file)

    audio = (
        audio
        .set_frame_rate(16000)
        .set_channels(1)
        .set_sample_width(2)
    )

    audio.export(wav_file, format="wav")

    os.remove(mp3_file)

print("\nDone! New unseen AI samples created.")