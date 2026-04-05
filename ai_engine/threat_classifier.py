"""Contract-compliant AI analysis entry point with adversarial awareness."""

from .adversarial_detector import AdversarialDetector
from .classifier import classify_threat
from .feature_extractor import extract_features
from .risk_scorer import calculate_risk
from .xai_explainer import generate_explanation

_detector = AdversarialDetector()


def analyze_text(text: str, ip_address: str = None) -> dict:
    """Analyze a message and return threat, risk, XAI, and adversarial metadata."""
    features = extract_features(text)
    threat_type, confidence = classify_threat(text)
    risk_result = calculate_risk(threat_type, confidence, features)
    risk_score = risk_result["score"]

    adversarial_result = _detector.analyze_submission(
        text=text,
        features=features,
        confidence=confidence,
        risk_score=risk_score,
        ip_address=ip_address,
    )

    if adversarial_result["is_adversarial"]:
        recommendation = "REVIEW"
        explanation_prefix = (
            "⚠️ Adversarial behavior detected. "
            f"Indicators: {', '.join(ind['type'] for ind in adversarial_result['indicators']) or 'none'}.\n\n"
        )
    elif risk_score >= 70:
        recommendation = "BLOCK"
        explanation_prefix = ""
    elif risk_score >= 40:
        recommendation = "REVIEW"
        explanation_prefix = ""
    else:
        recommendation = "ALLOW"
        explanation_prefix = ""

    explanation = explanation_prefix + generate_explanation(threat_type, confidence, features, risk_result)

    return {
        "threat_type": threat_type,
        "risk_score": risk_score,
        "confidence": confidence,
        "explanation": explanation,
        "ai_recommendation": recommendation,
        "adversarial_detection": {
            "is_adversarial": adversarial_result["is_adversarial"],
            "is_probe": adversarial_result.get("is_probe", adversarial_result["is_adversarial"]),
            "confidence": adversarial_result["adversarial_confidence"],
            "indicators": adversarial_result["indicators"],
            "recommendation": adversarial_result["recommendation"],
        },
    }


# ==========================================================
# 🧪 TEST BLOCK (Optional - for validation)
# ==========================================================
if __name__ == "__main__":
    print("--- TESTING CONTRACT COMPLIANCE ---")
    test_msg = "URGENT! Your BIAT account is suspended. Click: http://fake-biat.xyz"
    result = analyze_text(test_msg, ip_address="127.0.0.1")
    
    print("📦 Contract Output:")
    for key, value in result.items():
        print(f"  {key}: {value}")