def get_prevention_action(risk_level):
    """
    Decide what security action should be taken
    based on the calculated risk level.
    """

    if risk_level == "LOW":
        return {
            "action": "ALLOW",
            "status": "SAFE",
            "description": "Call can continue normally."
        }

    elif risk_level == "MEDIUM":
        return {
            "action": "REQUEST_VERIFICATION",
            "status": "VERIFY",
            "description": "Ask the user for additional verification."
        }

    elif risk_level == "HIGH":
        return {
            "action": "STRONG_VERIFICATION",
            "status": "WARNING",
            "description": "Require strong identity verification before continuing."
        }

    elif risk_level == "CRITICAL":
        return {
            "action": "BLOCK_AND_ALERT",
            "status": "BLOCKED",
            "description": "Block the suspicious interaction and alert security."
        }

    else:
        return {
            "action": "MANUAL_REVIEW",
            "status": "UNKNOWN",
            "description": "Send the interaction for manual security review."
        }