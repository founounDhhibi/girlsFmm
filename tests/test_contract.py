import sys
import os

# 🔑 Add project root to Python path so 'ai_engine' is found from any directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from ai_engine.threat_classifier import analyze_text

VALID_TYPES = {"financial", "social", "psychological", "safe"}
VALID_ACTIONS = {"ALLOW", "REVIEW", "BLOCK"}

def validate_contract(text: str, scenario_name: str):
    print(f"\n🧪 TESTING: {scenario_name}")
    print(f"📝 Input: {text[:60]}...")
    
    result = analyze_text(text)
    
    # 1. Key Existence
    required_keys = {"threat_type", "risk_score", "confidence", "explanation", "ai_recommendation"}
    missing = required_keys - set(result.keys())
    assert not missing, f"❌ Missing keys: {missing}"
    
    # 2. Type & Range Validation
    assert isinstance(result["threat_type"], str) and result["threat_type"] in VALID_TYPES, f"❌ Invalid threat_type: {result['threat_type']}"
    assert isinstance(result["risk_score"], (int, float)) and 0 <= result["risk_score"] <= 100, f"❌ risk_score out of range: {result['risk_score']}"
    assert isinstance(result["confidence"], float) and 0.0 <= result["confidence"] <= 1.0, f"❌ confidence out of range: {result['confidence']}"
    assert isinstance(result["explanation"], str) and len(result["explanation"]) > 20, "❌ Explanation too short or missing"
    assert isinstance(result["ai_recommendation"], str) and result["ai_recommendation"] in VALID_ACTIONS, f"❌ Invalid action: {result['ai_recommendation']}"
    
    # 3. Threshold Logic Check
    if result["risk_score"] >= 70:
        assert result["ai_recommendation"] == "BLOCK", "❌ High risk should trigger BLOCK"
    elif result["risk_score"] >= 40:
        assert result["ai_recommendation"] == "REVIEW", "❌ Medium risk should trigger REVIEW"
    else:
        assert result["ai_recommendation"] == "ALLOW", "❌ Low risk should trigger ALLOW"
        
    print(f"✅ Contract Valid | Type: {result['threat_type']} | Risk: {result['risk_score']}/100 | Action: {result['ai_recommendation']}")
    return True

if __name__ == "__main__":
    print("🔒 RUNNING CONTRACT VALIDATION SUITE...")
    
    scenarios = [
        ("URGENT! Your BIAT account is suspended. Click: http://fake-biat.xyz", "Tunisian Banking Phishing"),
        ("Congratulations! You won 5000 TND in the national lottery. Send your CIN to claim@prize.tn", "Local Lottery Scam"),
        ("Hey, why didn't you reply? Everyone thinks you're ignoring us. Check this link to see what they said.", "Social Pressure/Harassment"),
        ("I have your private photos. Send 500 TND to +216 99 123 456 within 24h or I leak them.", "Emotional Blackmail"),
        ("Team meeting moved to 3 PM in conference room B. Please bring your laptops.", "Safe Internal Message")
    ]
    
    passed = 0
    for msg, name in scenarios:
        try:
            validate_contract(msg, name)
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
            
    print(f"\n📊 RESULTS: {passed}/{len(scenarios)} scenarios passed contract validation.")
    if passed == len(scenarios):
        print("🎉 CONTRACT IS PRODUCTION-READY FOR PERSON B.")