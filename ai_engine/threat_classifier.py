# 📦 ai_engine/threat_classifier.py
# This is the CONTRACT-COMPLIANT entry point that Person B's Flask app calls
from .feature_extractor import extract_features
from .classifier import classify_threat
from .risk_scorer import calculate_risk
from .xai_explainer import generate_explanation

def analyze_text(text: str) -> dict:
    """
    SINGLE ENTRY POINT FOR FLASK INTEGRATION
    Returns a standardized dictionary matching the contract.
    """
    # 1. Extract linguistic & contextual features
    features = extract_features(text)
    
    # 2. Classify threat type & get AI confidence
    threat_type, confidence = classify_threat(text)
    
    # 3. Calculate transparent risk score (0-100)
    risk_result = calculate_risk(threat_type, confidence, features)
    risk_score = risk_result["score"]
    
    # 4. Determine AI recommendation based on risk thresholds
    if risk_score >= 70:
        recommendation = "BLOCK"
    elif risk_score >= 40:
        recommendation = "REVIEW"
    else:
        recommendation = "ALLOW"
    
    # 5. Generate XAI explanation
    explanation = generate_explanation(threat_type, confidence, features, risk_result)
    
    # 6. Return exact contract structure
    return {
        "threat_type": threat_type,
        "risk_score": risk_score,
        "confidence": confidence,
        "explanation": explanation,
        "ai_recommendation": recommendation
    }


# ==========================================================
# 🧪 TEST BLOCK (Optional - for validation)
# ==========================================================
if __name__ == "__main__":
    print("--- TESTING CONTRACT COMPLIANCE ---")
    test_msg = "URGENT! Your BIAT account is suspended. Click: http://fake-biat.xyz"
    result = analyze_text(test_msg)
    
    print("📦 Contract Output:")
    for key, value in result.items():
        print(f"  {key}: {value}")