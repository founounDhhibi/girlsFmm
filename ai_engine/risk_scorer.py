"""Risk scoring logic for suspicious messages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class RiskBreakdown:
    keyword_score: float
    urgency_score: float
    structure_score: float
    final_score: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "keyword_score": self.keyword_score,
            "urgency_score": self.urgency_score,
            "structure_score": self.structure_score,
            "final_score": self.final_score,
        }


class RiskScorer:
    """Combine message signals into a normalized 0-1 risk score."""

    phishing_keywords = (
        "verify",
        "password",
        "urgent",
        "click",
        "account",
        "confirm",
        "suspended",
        "limited",
        "login",
        "security",
    )

    def score(self, message: str, tokens: list[str], feature_map: Dict[str, float | int | bool]) -> RiskBreakdown:
        lower_message = (message or "").lower()
        token_hits = sum(1 for token in tokens if token in self.phishing_keywords)
        keyword_score = min(1.0, token_hits / max(1, len(tokens) or 1) * 3)

        urgency_score = float(feature_map.get("urgency_score", 0.0))
        if "!" in lower_message:
            urgency_score = min(1.0, urgency_score + 0.15)

        structure_score = 0.0
        if feature_map.get("has_url"):
            structure_score += 0.35
        if feature_map.get("has_email"):
            structure_score += 0.1
        if float(feature_map.get("uppercase_ratio", 0.0)) > 0.35:
            structure_score += 0.2
        if float(feature_map.get("digit_ratio", 0.0)) > 0.2:
            structure_score += 0.15
        if int(feature_map.get("word_count", 0)) <= 4:
            structure_score += 0.1

        final_score = min(1.0, (keyword_score * 0.45) + (urgency_score * 0.25) + (structure_score * 0.30))
        return RiskBreakdown(keyword_score, urgency_score, min(1.0, structure_score), final_score)
