# 📦 app.py - CLEAN VERSION
import sys
import os

# 🔑 Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, render_template, request, jsonify
from database import db, Analysis, AuditLog
from audit_logger import log_event
from datetime import datetime

# ✅ Import AI engine ONCE at module level
from ai_engine.threat_classifier import analyze_text as ai_engine_analyze

# 1. Create Flask app
app = Flask(__name__)

# 2. Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cyber_shield.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Bind DB & create tables
db.init_app(app)
with app.app_context():
    db.create_all()
    print("✅ Database initialized. Tables ready.")

# ==========================================
# HTML ROUTES
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/audit-log')
def audit_log_page():
    return render_template('audit_log.html')

# ==========================================
# API ROUTES
# ==========================================

@app.route('/api/analyze', methods=['POST'])
def analyze_text_route():  # ← Renamed to avoid conflict with imported function
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing "text" field'}), 400

    text = data['text'].strip()
    if len(text) < 3:
        return jsonify({'error': 'Text too short'}), 400

    # ✅ Call AI engine (imported at top, no re-import needed)
    ai_output = ai_engine_analyze(text)
    
    # Save to DB
    analysis = Analysis(
        message_text=text,
        threat_type=ai_output['threat_type'],
        risk_score=ai_output['risk_score'],
        confidence=ai_output['confidence'],
        explanation=ai_output['explanation'],
        ai_recommendation=ai_output['ai_recommendation'],
        human_decision=None,
        ip_address=request.remote_addr
    )
    db.session.add(analysis)
    db.session.commit()

    # Log AI Prediction
    log_event(
        event_type='ai_prediction',
        actor='AI',
        action_description=f"Classified as {ai_output['threat_type']} (Risk: {ai_output['risk_score']})",
        details=ai_output,
        analysis_id=analysis.id,
        ip_address=request.remote_addr
    )

    return jsonify({
        'status': 'success',
        'analysis_id': analysis.id,
        **analysis.to_dict(),
        'requires_human_action': True
    }), 200


@app.route('/api/action', methods=['POST'])
def human_action():
    data = request.get_json()
    if not data or 'analysis_id' not in data or 'action' not in data:
        return jsonify({'error': 'Missing analysis_id or action'}), 400

    analysis_id = data['analysis_id']
    action = data['action']
    operator = data.get('operator', 'Anonymous_Operator')

    analysis = Analysis.query.get(analysis_id)
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404

    analysis.human_decision = action
    analysis.human_operator = operator
    analysis.decision_timestamp = datetime.utcnow()
    db.session.commit()

    log_event(
        event_type='human_decision',
        actor='HUMAN',
        action_description=f"Human {action}ed AI recommendation",
        details={'operator': operator, 'action_taken': action, 'ai_rec': analysis.ai_recommendation},
        analysis_id=analysis.id,
        ip_address=request.remote_addr
    )

    final_status = "✅ Approved & Executed" if action == 'approve' else "❌ Rejected & Ignored"
    return jsonify({
        'status': 'success',
        'message': final_status,
        'analysis_id': analysis_id
    }), 200


@app.route('/api/stats')
def get_stats():
    total = Analysis.query.count()
    pending = Analysis.query.filter_by(human_decision=None).count()
    approved = Analysis.query.filter_by(human_decision='approve').count()
    rejected = Analysis.query.filter_by(human_decision='reject').count()
    
    return jsonify({
        'total': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected
    })


@app.route('/api/pending')
def get_pending():
    pending_analyses = Analysis.query.filter_by(human_decision=None).order_by(Analysis.created_at.desc()).all()
    return jsonify([a.to_dict() for a in pending_analyses])


@app.route('/api/audit-data')
def get_audit_data():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return jsonify([log.to_dict() for log in logs])


if __name__ == '__main__':
    # Disable reloader to prevent import caching issues during dev
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)