from risk_engine import (
    calculate_risk,
    get_severity,
    get_action,
    get_risk_result,
    get_fail_safe_result
)

from unittest.mock import patch
import risk_engine


# Test 1: Genuine Call
score = calculate_risk(
    ai_probability=0.05,
    speaker_mismatch=0.05,
    caller_risk=0.0,
    transaction_risk=0.2,
    behavioral_risk=0.0
)

print(f"Test 1 - Genuine Call Risk Score: {score}")


# Test 2: Suspicious Call
score = calculate_risk(
    ai_probability=0.70,
    speaker_mismatch=0.60,
    caller_risk=0.5,
    transaction_risk=0.7,
    behavioral_risk=0.6
)

print(f"Test 2 - Suspicious Call Risk Score: {score}")


# Test 3: Critical Call
score = calculate_risk(
    ai_probability=0.95,
    speaker_mismatch=0.90,
    caller_risk=1.0,
    transaction_risk=1.0,
    behavioral_risk=0.9
)

print(f"Test 3 - Critical Call Risk Score: {score}")


# Test 4: Safe Case - All Zeros
score = calculate_risk(
    ai_probability=0,
    speaker_mismatch=0,
    caller_risk=0,
    transaction_risk=0,
    behavioral_risk=0
)

print(f"Test 4 - Safe Case Risk Score: {score}")


# Test 5: Maximum Case - All Ones
score = calculate_risk(
    ai_probability=1,
    speaker_mismatch=1,
    caller_risk=1,
    transaction_risk=1,
    behavioral_risk=1
)

print(f"Test 5 - Maximum Case Risk Score: {score}")


# Test 6: Severity Classification
score = calculate_risk(
    ai_probability=0.95,
    speaker_mismatch=0.90,
    caller_risk=1.0,
    transaction_risk=1.0,
    behavioral_risk=0.9
)

severity = get_severity(score)

print(f"Test 6 - Risk Score: {score}")
print(f"Test 6 - Severity: {severity}")


# Test 7: Security Action

severity = get_severity(score)
action = get_action(severity)

print(f"Test 7 - Risk Score: {score}")
print(f"Test 7 - Severity: {severity}")
print(f"Test 7 - Action: {action}")


# Test 8: Test all security actions

test_severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

for severity in test_severities:
    action = get_action(severity)
    print(f"{severity} -> {action}")


# Test 9: Invalid Input

try:
    score = calculate_risk(
        ai_probability=2,
        speaker_mismatch=0.5,
        caller_risk=0.2,
        transaction_risk=0.3,
        behavioral_risk=0.1
    )

    print("Test 9 FAILED - Invalid input was accepted")

except ValueError as error:
    print(f"Test 9 PASSED - Invalid input rejected: {error}")


# Test 10: Non-numeric Input

try:
    score = calculate_risk(
        ai_probability="hello",
        speaker_mismatch=0.5,
        caller_risk=0.2,
        transaction_risk=0.3,
        behavioral_risk=0.1
    )

    print("Test 10 FAILED - Text input was accepted")

except ValueError as error:
    print(f"Test 10 PASSED - Text input rejected: {error}")    


# Test 11: Complete Risk Result

result = get_risk_result(
    ai_probability=0.95,
    speaker_mismatch=0.90,
    caller_risk=1.0,
    transaction_risk=1.0,
    behavioral_risk=0.9
)

print("Test 11 - Complete Risk Result:")
print(result)



# Test 12: Boundary Values

try:
    score = calculate_risk(
        ai_probability=0,
        speaker_mismatch=0,
        caller_risk=0,
        transaction_risk=0,
        behavioral_risk=0
    )

    print(f"Test 12 PASSED - Minimum values accepted: {score}")

except ValueError as error:
    print(f"Test 12 FAILED - Minimum values rejected: {error}")


try:
    score = calculate_risk(
        ai_probability=1,
        speaker_mismatch=1,
        caller_risk=1,
        transaction_risk=1,
        behavioral_risk=1
    )

    print(f"Test 12 PASSED - Maximum values accepted: {score}")

except ValueError as error:
    print(f"Test 12 FAILED - Maximum values rejected: {error}")



# Test 13: Invalid Boundary Values

try:
    calculate_risk(
        ai_probability=-0.1,
        speaker_mismatch=0.5,
        caller_risk=0.2,
        transaction_risk=0.3,
        behavioral_risk=0.1
    )

    print("Test 13 FAILED - Negative value was accepted")

except ValueError as error:
    print(f"Test 13 PASSED - Negative value rejected: {error}")


try:
    calculate_risk(
        ai_probability=1.1,
        speaker_mismatch=0.5,
        caller_risk=0.2,
        transaction_risk=0.3,
        behavioral_risk=0.1
    )

    print("Test 13 FAILED - Value above 1 was accepted")

except ValueError as error:
    print(f"Test 13 PASSED - Value above 1 rejected: {error}")



# Test 14: Validation of All Risk Inputs

test_inputs = [
    ("speaker_mismatch", -0.1),
    ("caller_risk", 1.5),
    ("transaction_risk", -1),
    ("behavioral_risk", 2)
]

for field, value in test_inputs:
    try:
        values = {
            "ai_probability": 0.5,
            "speaker_mismatch": 0.5,
            "caller_risk": 0.5,
            "transaction_risk": 0.5,
            "behavioral_risk": 0.5
        }

        values[field] = value

        calculate_risk(**values)

        print(f"Test 14 FAILED - {field} accepted invalid value")

    except ValueError as error:
        print(f"Test 14 PASSED - {field} rejected: {error}")


# Test 15: Security Decision Mapping

expected_actions = {
    "LOW": "ALLOW",
    "MEDIUM": "MONITOR",
    "HIGH": "SECONDARY_VERIFICATION",
    "CRITICAL": "BLOCK_AND_ESCALATE"
}

for severity, expected_action in expected_actions.items():
    actual_action = get_action(severity)

    if actual_action == expected_action:
        print(f"Test 15 PASSED - {severity} -> {actual_action}")
    else:
        print(
            f"Test 15 FAILED - {severity} -> "
            f"Expected: {expected_action}, Got: {actual_action}"
        )



# Test 16: Safe Call Complete Result

safe_result = get_risk_result(
    ai_probability=0.05,
    speaker_mismatch=0.05,
    caller_risk=0.0,
    transaction_risk=0.2,
    behavioral_risk=0.0
)

print("Test 16 - Safe Call Result:")
print(safe_result)


# Test 17: Medium Risk Complete Result

medium_result = get_risk_result(
    ai_probability=0.4,
    speaker_mismatch=0.3,
    caller_risk=0.3,
    transaction_risk=0.4,
    behavioral_risk=0.2
)

print("Test 17 - Medium Risk Result:")
print(medium_result)



# Test 18: Fail-Safe Result

fail_safe_result = get_fail_safe_result()

print("Test 18 - Fail-Safe Result:")
print(fail_safe_result)


# Test 19 - Unexpected Error Fail-Safe

with patch("risk_engine.calculate_risk", side_effect=RuntimeError("Test failure")):

    fail_safe_result = risk_engine.get_risk_result(
        0.5,
        0.5,
        0.5,
        0.5,
        0.5
    )

print("Test 19 - Unexpected Error Fail-Safe:")
print(fail_safe_result)



# Test 20 - NaN Input Rejection

result = get_risk_result(
    float("nan"),
    0.0,
    0.0,
    0.0,
    0.0
)

if result["severity"] == "UNKNOWN" and result["action"] == "SECONDARY_VERIFICATION":
    print("Test 20 PASSED - NaN triggered fail-safe")
else:
    print("Test 20 FAILED - NaN was not handled safely")



# Test 21 - Infinity Input Rejection

result = get_risk_result(
    float("inf"),
    0.0,
    0.0,
    0.0,
    0.0
)

if result["severity"] == "UNKNOWN" and result["action"] == "SECONDARY_VERIFICATION":
    print("Test 21 PASSED - Infinity triggered fail-safe")
else:
    print("Test 21 FAILED - Infinity was not handled safely")