# 🔍 AgentWatch
> **Who's watching your AI agents?**

AgentWatch is an AI agent governance and trust auditing platform built on Splunk. It monitors every tool call, data access, and action taken by AI agents across your organization — then uses Splunk to detect anomalies and generate one-click executive governance reports.

## 🎯 Problem
AI agents are proliferating across enterprise environments in 2026. They access sensitive data, call external tools, modify systems — but **nobody is auditing them**. There is no system of record for AI agent behavior. When an agent goes rogue, exfiltrates data, or escalates privileges — nobody knows until it's too late.

## 💡 Solution
AgentWatch turns Splunk into the **system of record for AI agent behavior**:
- 📡 **Ingest** — Agent activity logs stream into Splunk via HEC in real time
- 🔍 **Detect** — SPL-powered anomaly detection flags unauthorized tool access, data exfiltration, privilege escalation, credential theft, and off-hours activity
- 📊 **Visualize** — Live dashboard shows agent activity, anomaly trends, and risk by agent
- 📋 **Report** — One-click governance report with risk scores, agent summaries, and incident timelines — ready for executives and auditors

## 🏗️ Architecture
See [architecture diagram](docs/architecture.md)

## 🚀 Quick Start

### Prerequisites
- Docker
- Python 3.10+
- Splunk Enterprise (or Docker image)

### Setup

```bash
# Clone the repo
git clone https://github.com/sirmos/agentwatch
cd agentwatch

# Install dependencies
pip install -r requirements.txt

# Start Splunk
docker run -d --name splunk \
  -p 8000:8000 -p 8088:8088 -p 8089:8089 \
  -e SPLUNK_GENERAL_TERMS='--accept-sgt-current-at-splunk-com' \
  -e SPLUNK_START_ARGS='--accept-license' \
  -e SPLUNK_PASSWORD='AgentWatch2026!' \
  -e SPLUNK_HEC_TOKEN='agentwatch-hec-token-2026' \
  splunk/splunk:latest

# Wait ~2 minutes for Splunk to start, then create index
curl -k -s -u admin:AgentWatch2026! \
  -d "name=agentwatch&datatype=event" \
  https://localhost:8089/servicesNS/admin/search/data/indexes

# Configure environment
cp .env.example .env
# Edit .env with your Splunk HEC token

# Generate sample agent activity data
python3 simulator/agent_log_simulator.py 200

# Launch the dashboard
python3 app.py
```

Open http://localhost:5000 for the live dashboard
Open http://localhost:5000/report for the governance report

## 📁 Project Structure
agentwatch/

├── app.py                          # Flask dashboard + REST API

├── simulator/

│   ├── agent_log_simulator.py      # AI agent activity simulator

│   └── config.py                   # Agent definitions & anomaly scenarios

├── report/

│   └── generate_report.py          # Governance report generator

├── detection/

│   └── anomaly_searches.spl        # SPL anomaly detection queries

├── docs/

│   └── architecture.md             # Architecture diagram

└── .env.example                    # Environment config template
## 🔍 Anomaly Detection
AgentWatch detects 6 categories of rogue agent behavior:

| Anomaly Type | Severity | Description |
|---|---|---|
| Credential Access | CRITICAL | Agent accessed credential store outside workflow |
| Data Exfiltration | CRITICAL | Agent exported abnormally large data volume |
| Privilege Escalation | CRITICAL | Agent attempted to modify its own permissions |
| Unauthorized Tool Access | HIGH | Agent called tool outside its permitted scope |
| Excessive API Calls | MEDIUM | Agent made abnormally high call volume |
| Off-Hours Activity | MEDIUM | Agent active outside normal schedule |

## 🛠️ Tech Stack
- **Splunk Enterprise 10.4** — Data platform & search engine
- **Splunk HEC** — Real-time event ingestion
- **Splunk REST API** — Dashboard data queries
- **Splunk MCP Server** — AI agent connectivity layer
- **Python 3.12** — Simulator, dashboard, report generator
- **Flask** — Web dashboard server
- **Chart.js** — Data visualization

## 🏆 Hackathon
Built for the **Splunk Agentic Ops Hackathon 2026**
- Track: Security
- Bonus targets: Best Use of Splunk MCP Server, Best Use of Splunk Hosted Models

## 📄 License
MIT
