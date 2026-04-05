from ai_engine.adversarial_detector import AdversarialDetector
from ai_engine.feature_extractor import extract_features

text = "Maybe possibly perhaps consider this thing somehow maybe"
features = extract_features(text)

detector = AdversarialDetector()
result = detector.analyze_submission(
    text=text,
    features=features,
    confidence=0.372,
    risk_score=19.15,
    ip_address="127.0.0.1",
)

print("Input:", text)
print("Confidence:", 0.372)
print("Risk score:", 19.15)
print("Adversarial result:", result)
