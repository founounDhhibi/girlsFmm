from database import db, AuditLog
import json
from datetime import datetime

def log_event(event_type, actor, action_description, details=None, analysis_id=None, ip_address="unknown"):
    """
    Creates an immutable audit log entry in the database.
    Meets hackathon requirement: 'Toutes les décisions de l'IA doivent générer des logs'
    """
    # Convert complex objects to JSON string for safe DB storage
    details_str = json.dumps(details, default=str) if details else None

    new_log = AuditLog(
        timestamp=datetime.utcnow(),
        event_type=event_type,
        actor=actor,
        action_description=action_description,
        details_json=details_str,
        analysis_id=analysis_id,
        ip_address=ip_address
    )

    db.session.add(new_log)
    db.session.commit()
    return new_log