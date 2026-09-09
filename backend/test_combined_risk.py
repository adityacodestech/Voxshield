from risk_engine import calculate_risk


tests = [
    {
        "name": "Genuine Speaker",
        "ai_score": 5,
        "speaker_match": True
    },
    {
        "name": "Human Voice - Speaker Mismatch",
        "ai_score": 20,
        "speaker_match": False
    },
    {
        "name": "Suspicious AI Voice",
        "ai_score": 75,
        "speaker_match": True
    },
    {
        "name": "AI Impersonation Attack",
        "ai_score": 90,
        "speaker_match": False
    }
]


print("\n================================")
print("🛡️ COMBINED RISK ENGINE TEST")
print("================================")

for test in tests:

    result = calculate_risk(
        test["ai_score"],
        test["speaker_match"]
    )

    print(f"\nTest: {test['name']}")
    print(f"AI Score       : {test['ai_score']}%")
    print(f"Speaker Match  : {test['speaker_match']}")
    print(f"Risk Level     : {result['risk_level']}")
    print(f"Action         : {result['action']}")
    print(f"Message        : {result['message']}")

print("\n================================")