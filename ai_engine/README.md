# AI Engine

This folder contains the core AI pipeline for threat detection and adversarial awareness.

## Files

- `classifier.py`: Loads the zero-shot model and classifies threat type.
- `feature_extractor.py`: Extracts linguistic and security features from text.
- `risk_scorer.py`: Computes transparent risk score (0-100).
- `xai_explainer.py`: Generates human-readable explanations.
- `adversarial_detector.py`: Detects probing, confusion attacks, and rapid scans.
- `threat_classifier.py`: Contract entry point used by Flask app.

## Public Contract

`threat_classifier.analyze_text(text, ip_address=None)` returns:

- `threat_type`
- `risk_score`
- `confidence`
- `explanation`
- `ai_recommendation`
- `adversarial_detection`

## Quick Test

```bash
python -m ai_engine.tests.test_adversarial
```
