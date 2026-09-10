from speaker_verification import compare_speakers

REFERENCE_FILE = "speaker_profiles/reference_voice.wav"
TEST_FILE = "speaker_profiles/my_voice_test_converted.wav"

score = compare_speakers(REFERENCE_FILE, TEST_FILE)

print("\n================================")
print("👤 SAME SPEAKER TEST")
print("================================")
print(f"Speaker Match Score : {score}%")

if score >= 70:
    print("Speaker Match       : True")
    print("Result              : Same speaker likely")
else:
    print("Speaker Match       : False")
    print("Result              : Different speaker likely")

print("================================")