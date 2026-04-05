# 📦 app.py - CLEAN VERSION
import json
import os
import sys
from collections import Counter
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from sqlalchemy import text

from audit_logger import log_event
from database import Analysis, AuditLog, db
from ai_engine.threat_classifier import analyze_text as ai_engine_analyze


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///cyber_shield.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    db.create_all()
    _analysis_columns = {
        row[1]
        for row in db.session.execute(text("PRAGMA table_info(analyses)"))
    }

    _column_statements = [
        ("is_adversarial_probe", "ALTER TABLE analyses ADD COLUMN is_adversarial_probe BOOLEAN DEFAULT 0"),
        ("adversarial_confidence", "ALTER TABLE analyses ADD COLUMN adversarial_confidence FLOAT DEFAULT 0.0"),
        ("adversarial_indicators", "ALTER TABLE analyses ADD COLUMN adversarial_indicators TEXT"),
        ("adversarial_recommendation", "ALTER TABLE analyses ADD COLUMN adversarial_recommendation VARCHAR(50)"),
    ]

    for column_name, statement in _column_statements:
        if column_name not in _analysis_columns:
            db.session.execute(text(statement))

    db.session.commit()
    print("✅ Database initialized. Tables ready.")


def _parse_indicators(raw_indicators):
    if not raw_indicators:
        return []

    try:
        parsed = json.loads(raw_indicators)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def _get_adversarial_dashboard_stats():
    adversarial_rows = Analysis.query.filter_by(is_adversarial_probe=True).all()
    unique_ips = {row.ip_address for row in adversarial_rows if row.ip_address}
    pattern_counter = Counter()

    for row in adversarial_rows:
        for indicator in _parse_indicators(row.adversarial_indicators):
            if isinstance(indicator, dict) and indicator.get("type"):
                pattern_counter[indicator["type"]] += 1

    return {
        "probes_detected": len(adversarial_rows),
        "suspicious_ips": len(unique_ips),
        "common_attack_patterns": [
            {"name": pattern.replace("_", " ").title(), "count": count}
            for pattern, count in pattern_counter.most_common(5)
        ],
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


@app.route("/audit-log")
def audit_log_page():
    return render_template("audit_log.html")


@app.route("/api/analyze", methods=["POST"])
def analyze_text_route():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing \"text\" field"}), 400

    text = data["text"].strip()
    if len(text) < 3:
        return jsonify({"error": "Text too short"}), 400

    ai_output = ai_engine_analyze(text, ip_address=request.remote_addr)
    adversarial = ai_output.get("adversarial_detection", {})

    analysis = Analysis(
        message_text=text,
        threat_type=ai_output["threat_type"],
        risk_score=ai_output["risk_score"],
        confidence=ai_output["confidence"],
        explanation=ai_output["explanation"],
        ai_recommendation=ai_output["ai_recommendation"],
        human_decision=None,
        ip_address=request.remote_addr,
        is_adversarial_probe=adversarial.get("is_adversarial", False),
        adversarial_confidence=adversarial.get("confidence", 0.0),
        adversarial_indicators=json.dumps(adversarial.get("indicators", [])),
        adversarial_recommendation=adversarial.get("recommendation"),
    )
    db.session.add(analysis)
    db.session.commit()

    log_event(
        event_type="ai_prediction",
        actor="AI",
        action_description=f"Classified as {ai_output['threat_type']} (Risk: {ai_output['risk_score']})",
        details=ai_output,
        analysis_id=analysis.id,
        ip_address=request.remote_addr,
    )

    return jsonify(
        {
            "status": "success",
            "analysis_id": analysis.id,
            **analysis.to_dict(),
            "requires_human_action": True,
        }
    ), 200


@app.route("/api/action", methods=["POST"])
def human_action():
    data = request.get_json()
    if not data or "analysis_id" not in data or "action" not in data:
        return jsonify({"error": "Missing analysis_id or action"}), 400

    analysis_id = data["analysis_id"]
    action = data["action"]
    operator = data.get("operator", "Anonymous_Operator")

    analysis = Analysis.query.get(analysis_id)
    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    analysis.human_decision = action
    analysis.human_operator = operator
    analysis.decision_timestamp = datetime.utcnow()
    db.session.commit()

    log_event(
        event_type="human_decision",
        actor="HUMAN",
        action_description=f"Human {action}ed AI recommendation",
        details={"operator": operator, "action_taken": action, "ai_rec": analysis.ai_recommendation},
        analysis_id=analysis.id,
        ip_address=request.remote_addr,
    )

    final_status = "✅ Approved & Executed" if action == "approve" else "❌ Rejected & Ignored"
    return jsonify({"status": "success", "message": final_status, "analysis_id": analysis_id}), 200


@app.route("/api/stats")
def get_stats():
    total = Analysis.query.count()
    pending = Analysis.query.filter_by(human_decision=None).count()
    approved = Analysis.query.filter_by(human_decision="approve").count()
    rejected = Analysis.query.filter_by(human_decision="reject").count()

    return jsonify(
        {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            **_get_adversarial_dashboard_stats(),
        }
    )


@app.route("/api/pending")
def get_pending():
    pending_analyses = Analysis.query.filter_by(human_decision=None).order_by(Analysis.created_at.desc()).all()
    return jsonify([analysis.to_dict() for analysis in pending_analyses])


@app.route("/api/audit-data")
def get_audit_data():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return jsonify([log.to_dict() for log in logs])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)