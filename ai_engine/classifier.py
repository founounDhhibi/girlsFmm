"""Message classifier built on top of the extractor, scorer, and explainer."""

from __future__ import annotations

from typing import Dict

from .feature_extractor import FeatureExtractor
from .risk_scorer import RiskScorer
from .xai_explainer import XAIExplainer


class ThreatClassifier:
    """High-level classification facade for the Flask app."""

    def __init__(self) -> None:
        self.extractor = FeatureExtractor()
        self.scorer = RiskScorer()
        self.explainer = XAIExplainer()

    def classify(self, message: str) -> Dict[str, object]:
        features = self.extractor.extract(message)
        tokens = self.extractor.tokenize(message)
        breakdown = self.scorer.score(message, tokens, features.to_dict())
        matched_keywords = [token for token in tokens if token in self.scorer.phishing_keywords]

        is_phishing = breakdown.final_score >= 0.6
        result = "Phishing Alert" if is_phishing else "Safe Message"
        recommendation = "Do not click links or share credentials." if is_phishing else "No immediate action required."
        explanation = self.explainer.explain(message, tokens, breakdown.final_score, matched_keywords)

        return {
            "result": result,
            "confidence": round(breakdown.final_score * 100, 1),
            "recommendation": recommendation,
            "explanation": explanation,
            "breakdown": breakdown.to_dict(),
            "features": features.to_dict(),
        }
