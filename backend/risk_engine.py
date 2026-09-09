def calculate_risk(ai_score, speaker_match):
    """
    Combined risk assessment using:
    1. AI-generated voice score
    2. Speaker verification result
    """

    # -----------------------------------------
    # CASE 1: AI voice + speaker mismatch
    # -----------------------------------------
    if ai_score >= 60 and not speaker_match:
        return {
            "risk_level": "CRITICAL",
            "action": "BLOCK_AND_ALERT",
            "message": "High likelihood of AI-generated voice and speaker mismatch detected. Possible voice impersonation attack."
        }

    # -----------------------------------------
    # CASE 2: AI voice detected
    # -----------------------------------------
    elif ai_score >= 60:
        return {
            "risk_level": "HIGH",
            "action": "VERIFY",
            "message": "Potential AI-generated voice detected. Strong verification recommended."
        }

    # -----------------------------------------
    # CASE 3: Human-like voice but speaker mismatch
    # -----------------------------------------
    elif not speaker_match:
        return {
            "risk_level": "MEDIUM",
            "action": "VERIFY",
            "message": "Voice appears human but does not sufficiently match the enrolled speaker. Possible impersonation."
        }

    # -----------------------------------------
    # CASE 4: Human voice + speaker match
    # -----------------------------------------
    else:
        return {
            "risk_level": "LOW",
            "action": "ALLOW",
            "message": "Voice appears human and matches the enrolled speaker."
        }