from typing import Dict, Any, List

# 🗣️ FEATURE → EVIDENCE MAPPING RULES
# Converts raw feature counts/booleans into human-readable security insights
EVIDENCE_RULES = {
    "urgency_score": lambda v: f"Contains {v} urgency-inducing words (pressure tactic)" if v >= 2 else None,
    "financial_score": lambda v: f"Mentions financial/banking terms ({v} matches)" if v >= 1 else None,
    "url_count": lambda v: f"Contains {v} link(s) - verify domain legitimacy" if v >= 1 else None,
    "tunisian_bank_mentions": lambda v: f"References Tunisian banking institutions (high phishing indicator)" if v >= 1 else None,
    "tunisian_phone": lambda v: "Contains Tunisian phone format (+216) - verify caller identity" if v else None,
    "suspicious_tld": lambda v: "Uses suspicious domain extension (.xyz/.top/.tk) - common in phishing" if v else None,
    "uppercase_ratio": lambda v: f"Aggressive capitalization ({v:.0%}) - psychological pressure" if v > 0.3 else None,
    "email_count": lambda v: f"Contains {v} email address(es) - potential credential harvesting" if v >= 1 else None,
}

# 🛡️ ACTIONABLE RECOMMENDATIONS PER THREAT TYPE
RECOMMENDATIONS = {
    "financial": "🚨 DO NOT click links or share credentials. Verify directly with your bank via official app/phone. Report to ANSSI if suspicious.",
    "social": "⚠️ High manipulation risk. Do not engage. Verify source through independent channels. Block/report if harassing.",
    "psychological": "🧠 Emotional pressure detected. Pause before responding. This message uses fear/urgency tactics. Consult a trusted person.",
    "safe": "✅ No significant threats detected. Exercise normal digital hygiene."
}

def generate_explanation(threat_type: str, confidence: float, features: Dict[str, Any], risk_result: Dict[str, Any]) -> str:
    """
    Generates a plain-English, auditable explanation for the human operator.
    Complies with 'Zéro Black-Box' and 'Traçabilité totale' requirements.
    """
    # 1️⃣ Collect triggered evidence from features
    evidence = []
    for key, rule in EVIDENCE_RULES.items():
        val = features.get(key, 0)
        result = rule(val)
        if result:
            evidence.append(result)
    
    if not evidence:
        evidence.append("No high-risk linguistic patterns detected in this message.")

    # 2️⃣ Interpret confidence level for operators
    if confidence >= 0.8:
        conf_level = "Very High"
    elif confidence >= 0.6:
        conf_level = "High"
    elif confidence >= 0.4:
        conf_level = "Medium"
    else:
        conf_level = "Low"

    # 3️⃣ Fetch threat-specific recommendation
    rec = RECOMMENDATIONS.get(threat_type, RECOMMENDATIONS["safe"])

    # 4️⃣ Assemble contract-compliant explanation string
    explanation = (
        f"[{threat_type.upper()}] AI classified this as a {threat_type} threat "
        f"with {conf_level} confidence ({confidence:.0%}). "
        f"Risk score: {risk_result['score']}/100 ({risk_result['level']}). "
        f"Evidence: {'; '.join(evidence)}. "
        f"Recommendation: {rec}"
    )
    
    return explanation
if __name__ == "__main__":
    from .feature_extractor import extract_features
    from .risk_scorer import calculate_risk
    from .classifier import classify_threat

    print("--- TESTING XAI EXPLAINER ---")
    text = "URGENT! Your BIAT account is suspended. Click immediately: http://fake-biat.xyz"
    
    features = extract_features(text)
    threat_type, confidence = classify_threat(text)
    risk_result = calculate_risk(threat_type, confidence, features)
    explanation = generate_explanation(threat_type, confidence, features, risk_result)
    
    print("📝 Input:", text[:50] + "...")
    print("🔍 XAI Output:")
    print(explanation)