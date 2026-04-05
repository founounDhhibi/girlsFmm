from typing import Dict, Any

# ⚖️ Weights aligned with cybersecurity risk frameworks (NIST/ISO 27005)
WEIGHTS = {
    "threat_severity": 0.40,
    "model_confidence": 0.30,
    "feature_indicators": 0.30
}

# 📊 Base risk per threat type (Financial = highest real-world impact)
SEVERITY_BASE = {
    "financial": 0.90,
    "psychological": 0.75,
    "social": 0.60,
    "safe": 0.05
}

def calculate_risk(threat_type: str, confidence: float, features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates a transparent risk score (0-100) using a weighted formula.
    Formula: (Severity × 40%) + (Confidence × 30%) + (Feature Risk × 30%)
    """
    # 1️⃣ Threat Severity Component (0.0 to 1.0)
    base_severity = SEVERITY_BASE.get(threat_type, 0.5)

    # 2️⃣ Feature Risk Component (0.0 to 1.0)
    feature_risk = _calculate_feature_risk(features)

    # 3️⃣ Combine using transparent weights
    raw_score = (
        base_severity * WEIGHTS["threat_severity"] +
        confidence * WEIGHTS["model_confidence"] +
        feature_risk * WEIGHTS["feature_indicators"]
    )

    # Normalize to 0-100 scale
    risk_score = min(max(raw_score * 100, 0), 100)

    # 4️⃣ Determine Level & UI Color
    if risk_score < 30:
        level, color = "LOW", "green"
    elif risk_score < 60:
        level, color = "MEDIUM", "orange"
    elif risk_score < 80:
        level, color = "HIGH", "red"
    else:
        level, color = "CRITICAL", "darkred"

    # 5️⃣ Return structured object for XAI & Dashboard
    return {
        "score": round(risk_score, 2),
        "level": level,
        "color": color,
        "breakdown": {
            "threat_severity": round(base_severity * 100, 2),
            "confidence": round(confidence * 100, 2),
            "feature_risk": round(feature_risk * 100, 2)
        }
    }

def _calculate_feature_risk(features: Dict[str, Any]) -> float:
    """
    Converts linguistic features into a risk contribution score (0.0 to 1.0).
    Each condition adds a risk factor. We average them to avoid single-point spikes.
    """
    risk_factors = []

    # High urgency pressure
    if features.get("urgency_score", 0) >= 3:
        risk_factors.append(0.85)
    
    # Financial/banking language
    if features.get("financial_score", 0) >= 2:
        risk_factors.append(0.90)
    
    # Multiple links (higher redirect risk)
    if features.get("url_count", 0) >= 2:
        risk_factors.append(0.75)
    
    # 🇹 LOCAL CONTEXT: Tunisian bank + suspicious link = classic phishing pattern
    if features.get("tunisian_bank_mentions", 0) >= 1 and features.get("url_count", 0) >= 1:
        risk_factors.append(0.95)
    
    # Aggressive capitalization (shouting/pressure)
    if features.get("uppercase_ratio", 0) > 0.4:
        risk_factors.append(0.60)
    
    # Suspicious domain extension
    if features.get("suspicious_tld"):
        risk_factors.append(0.70)
    
    # Local phone number in unsolicited message
    if features.get("tunisian_phone"):
        risk_factors.append(0.50)

    # Average triggered risk factors, or return safe baseline
    return sum(risk_factors) / len(risk_factors) if risk_factors else 0.20



if __name__ == "__main__":
    from feature_extractor import extract_features
    
    print("--- TESTING RISK SCORER ---")
    
    # Test 1: High-Risk Tunisian Phishing
    text1 = "URGENT! Your BIAT account is suspended. Click immediately: http://fake-biat.xyz"
    feat1 = extract_features(text1)
    risk1 = calculate_risk("financial", 0.7418, feat1)
    print(f"📝 Input: '{text1[:40]}...'")
    print(f" Risk: {risk1['score']}/100 ({risk1['level']})")
    print(f"📊 Breakdown: {risk1['breakdown']}")
    print("-" * 50)
    
    # Test 2: Low-Risk Safe Message
    text2 = "Hello team, meeting tomorrow at 10am in room B."
    feat2 = extract_features(text2)
    risk2 = calculate_risk("safe", 0.4523, feat2)
    print(f"📝 Input: '{text2}'")
    print(f"🎯 Risk: {risk2['score']}/100 ({risk2['level']})")
    print(f"📊 Breakdown: {risk2['breakdown']}")