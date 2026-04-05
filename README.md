🛡️ AI Cyber Human Shield
AI-Augmented Cyber Defense, but Human Controlled
A transparent, explainable, Tunisian-aware threat analysis system that empowers human operators to make informed security decisions.
🏆 Hackathon AI x CYBER 2026 Submission | 🇹🇳 Built for Tunisian Cybersecurity
🎯 Problem Statement
"How can we design an intelligent system to protect Tunisian citizens in cyberspace—capable of detecting, analyzing, and responding to social, financial, and psychological threats—while guaranteeing transparency, data sovereignty, and absolute human control?"
AI Cyber Human Shield answers this by acting as a security co-pilot: it analyzes messages (emails, SMS, social media), detects threats with explainable AI, calculates transparent risk scores, and always requires human validation before any action is taken.
✨ Key Features
Feature
Description
Hackathon Alignment
🔍 Multi-Threat Detection
Detects financial phishing, social engineering, psychological manipulation, and safe content
Covers 3+ threat types per PDF
🇹🇳 Tunisian Context Awareness
Recognizes local banks (BIAT, Attijari), phone formats (+216), and regional scam patterns
25% Local Impact criteria
📊 Transparent Risk Scoring
Weighted formula: (Severity×40%) + (Confidence×30%) + (Features×30%) → 0-100 score
Zero Black-Box requirement
🗣️ Explainable AI (XAI)
Plain-English explanations: "Risk HIGH because: urgency=3, bank_mention=1, suspicious TLD"
30% Transparency criteria
👤 Human-in-the-Loop
AI proposes (ALLOW/REVIEW/BLOCK), human operator approves/rejects → zero auto-action
30% Human Control criteria
📝 Full Audit Trail
Every AI prediction + human decision logged with timestamp, IP, and operator name
"Traçabilité totale" requirement
🐳 Docker-Ready
Containerized architecture for reproducible deployment
25% Engineering criteria
🏗️ Architecture Diagram
mermaid

12345678910111213141516171819
📦 Component Responsibilities
Component
Owner
Purpose
ai_engine/
Person A
NLP pipeline, classification, risk scoring, XAI
app.py
Person B
Flask routes, request handling, API contract
database.py
Shared
SQLAlchemy models for analyses + audit_logs
audit_logger.py
Person B
Structured logging for traceability
templates/
Person B
Dashboard UI with real-time stats + decision queue
docker/
Person B
Containerization for reproducible deployment
🚀 Quick Start
Prerequisites
Python 3.10+
pip (Python package manager)
Git
Installation
bash
1234567891011121314
Test the API
bash
12345678910111213141516
Access the Dashboard
Open your browser to: http://localhost:5000/dashboard
🔑 API Contract (Person A → Person B)
The AI engine exposes a single, contract-compliant function:
python
1234567891011
Threshold Logic
Risk Score
AI Recommendation
Human Action Required
0–39
ALLOW
Optional review
40–69
REVIEW
✅ Mandatory approve/reject
70–100
BLOCK
✅ Mandatory approve/reject
⚠️ Zero Auto-Action: The system never executes blocking/approving actions without explicit human validation.
🧪 Testing
Run Contract Validation
bash
1
Validates all 5 contract keys, type safety, range boundaries, and threshold logic across 5 realistic scenarios (phishing, lottery scam, harassment, blackmail, safe).
Simulate Attacks
bash
1
Runs pre-defined Tunisian-context attack scenarios to demonstrate detection efficacy.
🐳 Docker Deployment
bash
123456
Docker Structure
1234
📜 Transparency Note (Required Deliverable)
Algorithm Choices
Component
Technology
Why Chosen
Classification
HuggingFace facebook/bart-large-mnli (Zero-Shot)
No training data needed; adaptable to new threat types; transparent category definitions
Feature Extraction
Rule-based lexicons + regex
Enables XAI traceability; embeds Tunisian context; deterministic behavior
Risk Scoring
Weighted formula (40/30/30)
Industry-aligned (NIST/ISO 27005); fully auditable; no hidden weights
XAI
Feature→Evidence mapping rules
Converts technical signals to plain English; satisfies "Zéro Black-Box"
Data Provenance & Bias Mitigation
Training Data: Zero-shot model pre-trained on public NLI datasets (MNLI). No fine-tuning on private/user data.
Lexicons: Curated from Tunisian cybersecurity reports, ANSSI advisories, and local scam databases.
Bias Handling:
Low-confidence predictions (<40%) default to safe but flag for human review
Tunisian context rules prevent Western-centric false negatives
All decisions logged for post-hoc bias auditing
AI Self-Defense Measures
Input Sanitization: All user text stripped of executable code before processing
Model Isolation: AI runs locally; no external API calls → data sovereignty
Rate Limiting: Flask middleware prevents abuse of /api/analyze
Audit Immutability: audit_logs table is append-only; no DELETE permissions
👥 Team & Contributions
Member
Role
Key Deliverables
Person A
AI Engine Owner
ai_engine/ module, feature extraction, risk scoring, XAI, contract design
Person B (Maryem)
Workflow & Integration Owner
Flask API, database schema, audit logging, dashboard UI, Docker deployment
Collaboration Protocol:
Sync every 4 hours via standup
Contract-first development: API schema agreed before coding
Git workflow: main (stable), dev (integration), feature branches
📁 Project Structure
12345678910111213141516171819202122232425262728293031323334353637
🏆 Hackathon Rubric Alignment
Criteria (Weight)
How We Deliver
Human Control & Explainability (30%)
XAI explanations + threshold-based routing + mandatory human approval + audit logs
Engineering Depth & Architecture (25%)
Modular pipeline, contract-first design, Docker, ETL-style feature engineering
Local Impact (25%)
Tunisian bank/phone/scam detection + Darija-aware lexicons + ANSSI-aligned recommendations
Innovation & UX (20%)
Risk DNA visualization, human-AI confidence matching, one-click attack simulation
📬 Contact & Support
Repository: github.com/your-username/ai-cyber-human-shield
Issues: Use GitHub Issues for bugs or feature requests
Demo Video: [Link to backup recording]
Pitch Deck: docs/pitch.pdf
"AI proposes, human disposes. Transparency isn't optional—it's the foundation of trust."
📄 License
© 2026 Securinets FST. All rights reserved.
This project was developed for the AI x CYBER Hackathon 2026.
For educational and demonstration purposes only.
Built with ❤️ for a safer Tunisian cyberspace 🇹🇳🔐
