"""Sample attack scenarios for Person B testing and demo flows."""

ATTACK_SCENARIOS = [
    {
        "name": "Credential Harvesting",
        "message": "Urgent: verify your account now at http://example-login.com",
        "expected_result": "Phishing Alert",
    },
    {
        "name": "Password Reset Lure",
        "message": "Your password will expire today. Confirm immediately.",
        "expected_result": "Phishing Alert",
    },
    {
        "name": "Normal Business Email",
        "message": "Can we reschedule the meeting to tomorrow morning?",
        "expected_result": "Safe Message",
    },
]


def get_scenarios() -> list[dict]:
    return ATTACK_SCENARIOS
