from transformers import pipeline
from feature_extractor import extract_features
from risk_scorer import calculate_risk
# Global variable to store the model (so we don't reload it every time)
_classifier = None

def load_model():
    """
    Loads the HuggingFace Zero-Shot Classifier.
    We use 'facebook/bart-large-mnli' because it is the industry standard 
    for categorizing text without prior training.
    """
    global _classifier
    if _classifier is None:
        print("📥 Loading AI Model (First time takes ~15s, then instant)...")
        _classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    return _classifier

# 🎯 Define our Threat Categories (The "Taxonomy")
CANDIDATE_LABELS = [
    "financial threat",        # Phishing, Scams, Banking fraud
    "social engineering",      # Manipulation, Fake news, Harassment
    "psychological manipulation", # Blackmail, Emotional pressure, Radicalization
    "safe content"             # Normal messages
]

# 🗺️ Map Model Output to Our Standard Codes
LABEL_MAP = {
    "financial threat": "financial",
    "social engineering": "social",
    "psychological manipulation": "psychological",
    "safe content": "safe"
}

def classify_threat(text: str):
    """
    Analyzes text and returns: (threat_type, confidence_score)
    """
    model = load_model()
    
    # Run the AI analysis
    result = model(text, candidate_labels=CANDIDATE_LABELS)
    
    # Get the best match
    predicted_label = result['labels'][0]
    confidence = result['scores'][0]
    
    # 🔒 Safety fallback: if AI is very uncertain, default to "safe" but flag for review
    if confidence < 0.50:
        return "safe", confidence
    
    # Map model output to our standardized codes
    return LABEL_MAP.get(predicted_label, "unknown"), confidence



def analyze_text(text: str) -> dict:
    """
    SINGLE ENTRY POINT FOR FLASK INTEGRATION
    Returns a standardized dictionary matching the partner's contract.
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
    
    # 5. Generate explanation (Step 5 will upgrade this to full XAI)
    explanation = (
        f"AI classified as '{threat_type}' threat with {confidence:.0%} confidence. "
        f"Risk score: {risk_score}/100. "
        f"Key indicators: urgency={features['urgency_score']}, "
        f"financial_terms={features['financial_score']}, "
        f"links={features['url_count']}."
    )
    
    # 6. Return exact contract structure
    return {
        "threat_type": threat_type,
        "risk_score": risk_score,
        "confidence": confidence,
        "explanation": explanation,
        "ai_recommendation": recommendation
    }
 
if __name__ == "__main__":
    print("--- TESTING CLASSIFIER ---")
    
    # Test 1: Phishing
    text1 = "URGENT! Your BIAT account is suspended. Click here: http://fake-biat.xyz"
    type1, conf1 = classify_threat(text1)
    print(f"📝 Text: '{text1[:30]}...'")
    print(f"🤖 AI Verdict: {type1} (Confidence: {conf1:.2%})")
    print("-" * 40)
    
    # Test 2: Safe
    text2 = "Hello, can we meet for lunch tomorrow?"
    type2, conf2 = classify_threat(text2)
    print(f"📝 Text: '{text2}'")
    print(f"🤖 AI Verdict: {type2} (Confidence: {conf2:.2%})")
    
    print("--- TESTING INTEGRATION CONTRACT ---")
    
    test_msg = "URGENT! Your BIAT account is suspended. Click immediately: http://fake-biat.xyz"
    result = analyze_text(test_msg)
    
    print("📦 Contract Output:")
    for key, value in result.items():
        print(f"  {key}: {value}")