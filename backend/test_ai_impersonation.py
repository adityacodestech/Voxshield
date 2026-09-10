from speaker_verification import compare_speakers

REFERENCE_FILE = "speaker_profiles/reference_voice.wav"
AI_FILE = "test_samples/ai/ai_test_01.wav"

score = compare_speakers(REFERENCE_FILE, AI_FILE)

print("\n================================")
print("🚨 AI IMPERSONATION TEST")
print("================================")
print(f"Speaker Match Score : {score}%")

if score >= 70:
    print("Speaker Match       : True")
    print("Result              : Voice resembles the enrolled speaker")
else:
    print("Speaker Match       : False")
    print("Result              : Speaker mismatch detected")

print("================================")