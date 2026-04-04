from flask import redirect, url_for

@app.route("/action", methods=["POST"])
def action():
    message = request.form.get("message")
    result = request.form.get("result")
    explanation = request.form.get("explanation")
    confidence = request.form.get("confidence")
    user_action = request.form.get("action")

    # Simulation
    if user_action == "approve" and result == "Phishing Alert":
        final_status = "🚫 Threat Blocked"
        details = "The malicious link has been disabled and message marked as spam."
    elif user_action == "approve":
        final_status = "✅ Safe Approved"
        details = "No threat detected. Message is safe."
    else:
        final_status = "❌ Action Rejected"
        details = "No action was taken. User rejected the AI recommendation."

    # Save to DB
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO actions (message, result, explanation, confidence, action) VALUES (?,?,?,?,?)",
              (message, result, explanation, confidence, user_action))
    conn.commit()
    conn.close()

    return render_template("result.html",
                           message=message,
                           result=result,
                           final_status=final_status,
                           details=details)