// ==========================================
// ANALYZER PAGE LOGIC (Existing)
// ==========================================
const form = document.getElementById('analysis-form');
if (form) {
    let currentAnalysisId = null;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = document.getElementById('message-input').value.trim();
        if (!text) return alert('Please enter a message.');

        const btn = form.querySelector('button');
        btn.disabled = true; btn.textContent = '⏳ Analyzing...';

        try {
            const res = await fetch('/api/analyze', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const data = await res.json();

            if (data.status === 'success') {
                currentAnalysisId = data.analysis_id;
                document.getElementById('res-threat').textContent = data.threat_type;
                document.getElementById('res-risk').textContent = data.risk_score;
                document.getElementById('res-confidence').textContent = (data.confidence * 100).toFixed(1);
                document.getElementById('res-explanation').textContent = data.explanation;
                document.getElementById('res-recommendation').textContent = data.ai_recommendation;

                const adversarial = data.adversarial_detection || {};
                const alertBox = document.getElementById('adversarial-alert');
                if (alertBox) {
                    if (adversarial.is_adversarial || adversarial.is_probe) {
                        const indicatorList = (adversarial.indicators || [])
                            .map(indicator => `<li>${indicator.type}: ${indicator.description}</li>`)
                            .join('');
                        alertBox.innerHTML = `
                            <h4>🛡️ Adversarial Alert</h4>
                            <p><strong>Status:</strong> Probe detected</p>
                            <p><strong>Detector Confidence:</strong> ${(adversarial.confidence * 100).toFixed(1)}%</p>
                            <p><strong>Recommended Response:</strong> ${adversarial.recommendation || 'Review manually'}</p>
                            <ul class="adversarial-indicators">${indicatorList}</ul>
                        `;
                        alertBox.style.display = 'block';
                    } else {
                        alertBox.innerHTML = '';
                        alertBox.style.display = 'none';
                    }
                }

                document.getElementById('result-section').style.display = 'block';
                document.getElementById('final-message').textContent = '';
                document.querySelector('.human-controls').style.display = 'block';
            } else alert('Error: ' + (data.error || 'Unknown'));
        } catch (err) { alert('Network error.'); }
        finally { btn.disabled = false; btn.textContent = '🔍 Analyze Threat'; }
    });

    window.submitAction = async (action) => {
        if (!currentAnalysisId) return alert('No pending analysis.');
        const operator = document.getElementById('operator-name').value.trim() || 'Guest';
        try {
            const res = await fetch('/api/action', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ analysis_id: currentAnalysisId, action, operator })
            });
            const data = await res.json();
            if (data.status === 'success') {
                document.getElementById('final-message').textContent = data.message;
                document.querySelector('.human-controls').style.display = 'none';
                currentAnalysisId = null;
                form.reset();
                document.getElementById('result-section').style.display = 'none';
            }
        } catch { alert('Failed to submit decision.'); }
    };
}

// ==========================================
// DASHBOARD LOGIC
// ==========================================
async function loadDashboard() {
    if (!document.querySelector('.dashboard-container')) return;

    // 1. Fetch & display stats
    try {
        const stats = await (await fetch('/api/stats')).json();
        document.getElementById('stat-total').textContent = stats.total;
        document.getElementById('stat-pending').textContent = stats.pending;
        document.getElementById('stat-approved').textContent = stats.approved;
        document.getElementById('stat-rejected').textContent = stats.rejected;
        const probesNode = document.getElementById('stat-probes');
        if (probesNode) probesNode.textContent = stats.probes_detected ?? 0;
        const suspiciousNode = document.getElementById('stat-suspicious-ips');
        if (suspiciousNode) suspiciousNode.textContent = stats.suspicious_ips ?? 0;

        const patternList = document.getElementById('pattern-list');
        if (patternList) {
            const patterns = Array.isArray(stats.common_attack_patterns) ? stats.common_attack_patterns : [];
            if (patterns.length === 0) {
                patternList.innerHTML = '<p class="loading">No adversarial patterns detected yet.</p>';
            } else {
                patternList.innerHTML = patterns.map(pattern => `
                    <div class="pattern-item">
                        <span class="pattern-name">${pattern.name}</span>
                        <span class="pattern-count">${pattern.count}</span>
                    </div>
                `).join('');
            }
        }
    } catch (e) { console.error('Stats failed:', e); }

    // 2. Fetch & render pending queue
    try {
        const pending = await (await fetch('/api/pending')).json();
        const container = document.getElementById('pending-list');
        
        if (pending.length === 0) {
            container.innerHTML = '<p class="loading">✅ All caught up! No pending decisions.</p>';
            return;
        }

        container.innerHTML = pending.map(p => `
            <div class="pending-item">
                <div class="pending-info">
                    <div class="pending-type">${p.threat_type?.toUpperCase() || 'UNKNOWN'}</div>
                    <div class="pending-risk">Risk: ${p.risk_score}/100 • Confidence: ${(p.confidence*100).toFixed(1)}%</div>
                    <small>${p.message_text.substring(0, 50)}...</small>
                </div>
                <div class="pending-actions">
                    <button class="btn-approve" onclick="handleDashboardAction(${p.id}, 'approve')">✅ Approve</button>
                    <button class="btn-reject" onclick="handleDashboardAction(${p.id}, 'reject')">❌ Reject</button>
                </div>
            </div>
        `).join('');
    } catch (e) { console.error('Pending failed:', e); }
}

window.handleDashboardAction = async (id, action) => {
    const operator = prompt('Enter Operator Name for Audit Trail:') || 'Dashboard_Operator';
    try {
        await fetch('/api/action', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ analysis_id: id, action, operator })
        });
        loadDashboard(); // Refresh queue & stats
    } catch { alert('Failed to submit decision.'); }
};

// ==========================================
// AUDIT LOG LOGIC
// ==========================================
async function loadAuditLog() {
    const tbody = document.getElementById('audit-tbody');
    if (!tbody) return;

    try {
        const response = await fetch('/api/audit-data');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const logs = await response.json();

        if (!Array.isArray(logs) || logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No logs found. Run a simulation first.</td></tr>';
            return;
        }

        tbody.innerHTML = logs.map(log => `
            <tr>
                <td>${log.id}</td>
                <td>${log.timestamp}</td>
                <td><span class="actor-badge actor-${log.actor}">${log.actor}</span></td>
                <td>${log.event_type}</td>
                <td>${log.action_description}</td>
                <td><pre style="margin:0;font-size:10px;white-space:pre-wrap;word-break:break-all;">${JSON.stringify(log.details, null, 2)}</pre></td>
            </tr>
        `).join('');
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="6" class="loading" style="color:#dc2626;">Failed to load: ${error.message}</td></tr>`;
        console.error('Audit Log Error:', error);
    }
}

// ==========================================
// DEMO SIMULATION LOGIC
// ==========================================
const simBtn = document.getElementById('btn-run-sim');
if (simBtn) {
    simBtn.addEventListener('click', async () => {
        // Realistic Tunisian threat scenarios
        const scenarios = [
            "URGENT: Votre compte BIAT a été suspendu pour activité suspecte. Cliquez immédiatement pour vérifier votre identité: http://biat-secure-verify.bit.ly/xyz123. Contactez-nous au +216 71 123 456.",
            "Félicitations! 🎉 Votre numéro a été sélectionné pour gagner 50,000 TND dans la Loterie Nationale Tunisienne! Pour réclamer votre prix, envoyez vos coordonnées bancaires à lottery-tn@winners-now.com avant minuit!",
            "⚠️ ALERTE: Le gouvernement va couper internet demain à 18h! Partagez ce message à tous vos contacts avant qu'il ne soit trop tard! Source: un ami fiable qui travaille au ministère (ne citez pas).",
            "Tu penses vraiment que quelqu'un t'aime? Personne ne se soucie de toi. Tu ferais mieux de disparaître. Tout le monde serait mieux sans toi.",
            "Salut! Ça va? On se voit demain au café près de l'ENSI à 10h? J'ai hâte de te montrer les photos des vacances! 😊"
        ];

        const btn = document.getElementById('btn-run-sim');
        const progressDiv = document.getElementById('sim-progress');
        const statusP = document.getElementById('sim-status');
        const bar = document.getElementById('sim-bar');

        btn.disabled = true;
        progressDiv.style.display = 'block';

        for (let i = 0; i < scenarios.length; i++) {
            statusP.textContent = `Analyzing scenario ${i + 1}/${scenarios.length}...`;
            bar.style.width = `${((i + 1) / scenarios.length) * 100}%`;

            try {
                // Send to your existing /api/analyze endpoint
                await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: scenarios[i], source: 'simulation_demo' })
                });
            } catch (e) {
                console.error(`Scenario ${i+1} failed:`, e);
            }
            // 600ms delay so jury can visually track progress
            await new Promise(r => setTimeout(r, 600));
        }

        statusP.textContent = '✅ Simulation Complete! Check Dashboard & Audit Log.';
        btn.disabled = false;
        
        // Auto-refresh dashboard stats
        if (typeof loadDashboard === 'function') loadDashboard();
    });
}