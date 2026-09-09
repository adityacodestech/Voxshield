from speaker_verification import verify_speaker


TEST_FILE = "speaker_profiles/reference_voice.wav"


result = verify_speaker(TEST_FILE)

print("\n================================")
print("👤 SPEAKER VERIFICATION TEST")
print("================================")

print(f"Speaker Match Score : {result['speaker_match_score']}%")
print(f"Speaker Match       : {result['speaker_match']}")
print(f"Reason              : {result['reason']}")

print("================================")