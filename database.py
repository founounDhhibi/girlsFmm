from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json


db = SQLAlchemy()


class Analysis(db.Model):
    """Stores every AI analysis and human decision."""

    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message_text = db.Column(db.Text, nullable=False)
    threat_type = db.Column(db.String(50))
    risk_score = db.Column(db.Float)
    confidence = db.Column(db.Float)
    explanation = db.Column(db.Text)
    ai_recommendation = db.Column(db.String(20))

    human_decision = db.Column(db.String(20), nullable=True)
    human_operator = db.Column(db.String(100))
    decision_timestamp = db.Column(db.DateTime, nullable=True)

    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_adversarial_probe = db.Column(db.Boolean, default=False)
    adversarial_confidence = db.Column(db.Float, default=0.0)
    adversarial_indicators = db.Column(db.Text)
    adversarial_recommendation = db.Column(db.String(50))

    def to_dict(self):
        """Converts DB row to JSON-safe dictionary for frontend/API."""
        indicators = []
        if self.adversarial_indicators:
            try:
                indicators = json.loads(self.adversarial_indicators)
            except json.JSONDecodeError:
                indicators = []

        preview = self.message_text[:100] + "..." if len(self.message_text) > 100 else self.message_text

        return {
            "id": self.id,
            "message_text": preview,
            "threat_type": self.threat_type,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "ai_recommendation": self.ai_recommendation,
            "human_decision": self.human_decision,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "ip_address": self.ip_address,
            "adversarial_detection": {
                "is_adversarial": self.is_adversarial_probe,
                "confidence": self.adversarial_confidence,
                "indicators": indicators,
                "recommendation": self.adversarial_recommendation,
            },
        }


class AuditLog(db.Model):
    """Immutable trail of every AI prediction and human action."""

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    event_type = db.Column(db.String(50), nullable=False)
    actor = db.Column(db.String(20), nullable=False)
    action_description = db.Column(db.Text, nullable=False)
    details_json = db.Column(db.Text)
    analysis_id = db.Column(db.Integer, db.ForeignKey("analyses.id"), nullable=True)
    ip_address = db.Column(db.String(45))

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": self.event_type,
            "actor": self.actor,
            "action_description": self.action_description,
            "details": json.loads(self.details_json) if self.details_json else {},
            "analysis_id": self.analysis_id,
        }