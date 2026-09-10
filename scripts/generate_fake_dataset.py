from pathlib import Path
import subprocess

PIPER = r"C:\Users\harsh\OneDrive\Desktop\ml\SIH\venv\Scripts\piper.exe"
MODEL = "en_US-lessac-medium"
OUTPUT_DIR = Path("data/processed/fake")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sentences = [
    "The quick brown fox jumps over the lazy dog.",
    "Welcome to the VoxShield voice security system.",
    "Artificial intelligence is changing modern cybersecurity.",
    "Please verify the identity of the person speaking on this call.",
    "Your security verification has been completed successfully.",
    "This message was generated for testing our voice detection model.",
    "Voice cloning technology can create realistic synthetic speech.",
    "Protecting people from impersonation attacks is very important.",
    "The system continuously analyzes incoming speech for suspicious signals.",
    "Please wait while your request is being processed.",
    "Your account security is our highest priority.",
    "The meeting will begin shortly after everyone joins the call.",
    "Machine learning can help detect synthetic audio.",
    "This is an example of an artificially generated voice.",
    "Real time voice analysis can improve communication security.",
    "The weather today is pleasant and clear.",
    "Thank you for using the VoxShield security platform.",
    "Please confirm the transaction before proceeding.",
    "Your verification code has been sent successfully.",
    "The security team is monitoring this conversation.",
    "Never share your confidential information with unknown callers.",
    "This audio sample is part of our research dataset.",
    "Modern neural networks can generate highly realistic speech.",
    "Voice authentication requires reliable detection technology.",
    "The system detected unusual characteristics in the audio.",
    "Please contact customer support if you notice suspicious activity.",
    "Your request has been received and is being reviewed.",
    "Cybersecurity is becoming increasingly important in the digital age.",
    "Synthetic speech can be difficult to distinguish from human speech.",
    "Our model analyzes acoustic patterns to identify generated voices.",
    "The application is ready to process the next audio segment.",
    "Please remain on the line while we verify your information.",
    "This test evaluates the performance of our AI voice detector.",
    "Secure communication requires strong identity verification.",
    "The voice detection system is running successfully.",
    "Artificial speech generation has improved significantly in recent years.",
    "Our goal is to prevent voice based impersonation attacks.",
    "The audio pipeline successfully received this speech segment.",
    "Please listen carefully to the following security announcement.",
    "The system will automatically analyze the incoming voice.",
    "Your account has been protected by an additional security check.",
    "This synthetic speech sample will be used for model training.",
    "The detector evaluates whether speech is genuine or AI generated.",
    "Real time protection can help reduce the impact of fraud.",
    "The analysis is complete and the result is ready.",
    "Voice security is an important part of modern digital systems.",
    "This sample demonstrates neural text to speech generation.",
    "The VoxShield project detects and prevents voice cloning attacks.",
    "Thank you for participating in this voice security experiment.",
]

for i, text in enumerate(sentences, start=1):

    output_file = OUTPUT_DIR / f"fake_{i:03d}.wav"

    subprocess.run(
        [
            PIPER,
            "-m",
            MODEL,
            "-f",
            str(output_file),
        ],
        input=text,
        text=True,
        check=True,
    )

    print(f"Generated: {output_file}")

print("\nSUCCESS: 50 AI-generated WAV files created.")