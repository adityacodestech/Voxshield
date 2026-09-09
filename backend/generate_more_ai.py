from gtts import gTTS
from pydub import AudioSegment
import os

OUTPUT_FOLDER = "ai_samples"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

sentences = [
    "Hello, how are you doing today?",
    "Please confirm your identity before continuing.",
    "Your account has been successfully verified.",
    "Please transfer the payment to the given account.",
    "I will call you again in a few minutes.",
    "The meeting has been scheduled for tomorrow morning.",
    "Your transaction was completed successfully.",
    "Please share the verification code with me.",
    "We need to discuss an important matter today.",
    "The system has detected unusual activity.",
    "Please contact customer support for assistance.",
    "Your request has been received and is being processed.",
    "I am calling regarding your recent account activity.",
    "Please confirm the amount before completing the transaction.",
    "The security team needs additional information from you.",
    "Your appointment has been confirmed for this afternoon.",
    "Thank you for your cooperation and have a great day."
]

start_number = 6

for i, text in enumerate(sentences):

    number = start_number + i

    mp3_file = f"temp_ai_{number:03d}.mp3"
    wav_file = os.path.join(
        OUTPUT_FOLDER,
        f"ai_{number:03d}.wav"
    )

    print(f"Generating AI sample {number}:")
    print(text)

    # Generate synthetic speech
    tts = gTTS(
        text=text,
        lang="en",
        slow=False
    )

    tts.save(mp3_file)

    # Convert to required WAV format
    audio = AudioSegment.from_mp3(mp3_file)

    audio = audio.set_frame_rate(16000)
    audio = audio.set_channels(1)
    audio = audio.set_sample_width(2)

    audio.export(
        wav_file,
        format="wav"
    )

    # Remove temporary MP3
    os.remove(mp3_file)

    print(f"Saved: {wav_file}")
    print()


print("================================")
print("DONE!")
print("17 AI samples generated.")
print("================================")