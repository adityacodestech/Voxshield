from gtts import gTTS
from pydub import AudioSegment
import os

os.makedirs("ai_samples", exist_ok=True)

sentences = [
    "Please verify the transaction before continuing.",
    "Your account security code is ready.",
    "This is a test of the voice detection system.",
    "Please confirm your identity.",
    "The payment has been successfully processed."
]

for i, text in enumerate(sentences, start=1):

    mp3_file = f"temp_{i}.mp3"
    wav_file = f"ai_samples/ai_{i:03d}.wav"

    print(f"Generating AI sample {i}...")

    # Generate synthetic speech
    tts = gTTS(text=text, lang="en")
    tts.save(mp3_file)

    # Convert to required format
    audio = AudioSegment.from_mp3(mp3_file)

    audio = audio.set_frame_rate(16000)
    audio = audio.set_channels(1)
    audio = audio.set_sample_width(2)

    audio.export(wav_file, format="wav")

    os.remove(mp3_file)

    print(f"Saved: {wav_file}")

print("\n✅ AI sample generation complete!")