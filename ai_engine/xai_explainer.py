"""Explainable AI helper for human-readable detection reasons."""

from __future__ import annotations

from typing import Iterable


class XAIExplainer:
    """Explain why a message received a specific risk score."""

    def explain(self, message: str, tokens: list[str], risk_score: float, matched_keywords: Iterable[str]) -> str:
        reasons: list[str] = []
        matched_keywords = list(dict.fromkeys(matched_keywords))

        if matched_keywords:
            reasons.append(f"Matched suspicious terms: {', '.join(matched_keywords[:4])}")
        if "http" in (message or "").lower() or "www" in (message or "").lower():
            reasons.append("Message contains a link")
        if "@" in (message or ""):
            reasons.append("Message contains an email address")
        if len(tokens) <= 4:
            reasons.append("Very short message, which is common in fraud attempts")
        if any(word in (message or "").lower() for word in ("urgent", "immediately", "now", "asap")):
            reasons.append("Urgency language detected")
        if not reasons:
            reasons.append("No high-risk indicators were found")

        risk_label = "high" if risk_score >= 0.6 else "low"
        return f"Risk level: {risk_label}. " + " ".join(reasons)
