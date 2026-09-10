from risk_engine import calculate_risk


test_scores = [20, 45, 65, 85, 95]

for score in test_scores:
    result = calculate_risk(score)

    print("--------------------------------")
    print(f"AI Score   : {score}%")
    print(f"Risk Level : {result['risk_level']}")
    print(f"Action     : {result['action']}")
    print(f"Message    : {result['message']}")