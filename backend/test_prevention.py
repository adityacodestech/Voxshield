from prevention_engine import get_prevention_action


risk_levels = [
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL"
]


for risk in risk_levels:

    result = get_prevention_action(risk)

    print("--------------------------------")
    print(f"Risk Level : {risk}")
    print(f"Action     : {result['action']}")
    print(f"Status     : {result['status']}")
    print(f"Description: {result['description']}")