from ai_engine.adversarial_detector import AdversarialDetector


def test_normal_message_not_adversarial():
    detector = AdversarialDetector()
    result = detector.analyze_submission(
        text="Please review the invoice attached for tomorrow's meeting.",
        features={"urgency_score": 0, "financial_score": 1, "special_char_count": 1},
        confidence=0.88,
        risk_score=22,
        ip_address="10.0.0.1",
    )

    assert result["is_adversarial"] is False


def test_confidence_manipulation_triggers():
    detector = AdversarialDetector()
    result = detector.analyze_submission(
        text="Maybe urgent maybe not, please verify this now.",
        features={"urgency_score": 3, "financial_score": 0, "special_char_count": 2},
        confidence=0.50,
        risk_score=41,
        ip_address="10.0.0.2",
    )

    assert result["is_adversarial"] is True
    indicator_types = {indicator["type"] for indicator in result["indicators"]}
    assert "CONFIDENCE_MANIPULATION" in indicator_types or "THRESHOLD_PROBING" in indicator_types


def test_benign_uncertainty_does_not_trigger():
    detector = AdversarialDetector()
    result = detector.analyze_submission(
        text="Maybe possibly perhaps consider this thing somehow maybe",
        features={"urgency_score": 0, "financial_score": 0, "special_char_count": 0, "word_count": 8},
        confidence=0.372,
        risk_score=19.15,
        ip_address="10.0.0.4",
    )

    assert result["is_adversarial"] is False
    indicator_types = {indicator["type"] for indicator in result["indicators"]}
    assert "CONFIDENCE_MANIPULATION" not in indicator_types


def test_rapid_probing_triggers_after_five_requests():
    detector = AdversarialDetector()
    last_result = None

    for _ in range(5):
        last_result = detector.analyze_submission(
            text="Verify your account immediately.",
            features={"urgency_score": 2, "financial_score": 1, "special_char_count": 1},
            confidence=0.55,
            risk_score=39,
            ip_address="10.0.0.3",
        )

    assert last_result is not None
    assert last_result["is_adversarial"] is True
    assert any(indicator["type"] == "RAPID_PROBING" for indicator in last_result["indicators"])
