import math


def validate_input(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")

    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")

    if value < 0 or value > 1:
        raise ValueError(f"{name} must be between 0 and 1")


def calculate_risk(
    ai_probability,  
    speaker_mismatch, 
    caller_risk, 
    transaction_risk, 
    behavioral_risk
    ):

    validate_input(ai_probability, "ai_probability")
    validate_input(speaker_mismatch, "speaker_mismatch")
    validate_input(caller_risk, "caller_risk")
    validate_input(transaction_risk, "transaction_risk")
    validate_input(behavioral_risk, "behavioral_risk")

    risk = (
        0.50 *  ai_probability + 
        0.20 * speaker_mismatch +
        0.10 * caller_risk +
        0.15 * transaction_risk +
        0.05 * behavioral_risk
    )

    risk_score = round(risk*100)

    return risk_score

#severity risk score
def get_severity(risk_score):
    if risk_score <= 30:
        return "LOW"
    elif risk_score <= 60:
        return "MEDIUM"
    elif risk_score <= 80:
        return "HIGH"
    else:
        return "CRITICAL"    


def get_action(severity):
    if severity == "LOW":
        return "ALLOW"

    elif severity == "MEDIUM":
        return "MONITOR"

    elif severity == "HIGH":
        return "SECONDARY_VERIFICATION"

    else:
        return "BLOCK_AND_ESCALATE"


def get_risk_result(
    ai_probability,
    speaker_mismatch,
    caller_risk,
    transaction_risk,
    behavioral_risk
):
    try:
        risk_score = calculate_risk(
            ai_probability,
            speaker_mismatch,
            caller_risk,
            transaction_risk,
            behavioral_risk
        )

        severity = get_severity(risk_score)
        action = get_action(severity)

        reasons = get_risk_reasons(
            ai_probability,
            speaker_mismatch,
            caller_risk,
            transaction_risk,
            behavioral_risk
        )

        return {
            "risk_score": risk_score,
            "severity": severity,
            "action": action,
            "reasons": reasons
        }

    except Exception:
        return get_fail_safe_result()


def get_risk_reasons(
    ai_probability,
    speaker_mismatch,
    caller_risk,
    transaction_risk,
    behavioral_risk
):
    reasons = []

    if ai_probability >= 0.7:
        reasons.append("High synthetic voice probability")

    if speaker_mismatch >= 0.7:
        reasons.append("High speaker mismatch")

    if caller_risk >= 0.7:
        reasons.append("High-risk caller")

    if transaction_risk >= 0.7:
        reasons.append("High-risk transaction")

    if behavioral_risk >= 0.7:
        reasons.append("Suspicious behavioral pattern")

    return reasons


def get_fail_safe_result():
    return {
        "risk_score": None,
        "severity": "UNKNOWN",
        "action": "SECONDARY_VERIFICATION",
        "reasons": [
            "Risk assessment could not be completed safely"
        ]
    }

