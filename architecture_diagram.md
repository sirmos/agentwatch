# AgentWatch — Architecture

## System Overview
┌─────────────────────────────────────────────────────────────┐

│                    AI AGENT LAYER                           │

│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │

│  │SecurityAgent│ │ OpsAgent    │ │  HRAgent    │  ...      │

│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘          │

└─────────┼───────────────┼───────────────┼──────────────────┘

│               │               │

▼               ▼               ▼

┌─────────────────────────────────────────────────────────────┐

│              AGENTWATCH INGESTION LAYER                     │

│                                                             │

│   agent_log_simulator.py  (or real agent SDK hooks)        │

│   → Structured JSON events per tool call                   │

│   → Fields: agent_id, tool_called, authorized,             │

│             anomaly, severity, data_volume_mb, session_id  │

└──────────────────────────┬──────────────────────────────────┘

│ HTTPS / HEC

▼

┌─────────────────────────────────────────────────────────────┐

│                  SPLUNK PLATFORM                            │

│                                                             │

│  ┌─────────────────┐    ┌──────────────────────────────┐   │

│  │  HTTP Event     │    │   index=agentwatch            │   │

│  │  Collector      │───▶│   sourcetype=agentwatch:      │   │

│  │  (port 8088)    │    │   activity                    │   │

│  └─────────────────┘    └──────────────┬───────────────┘   │

│                                        │                    │

│  ┌─────────────────────────────────────▼───────────────┐   │

│  │              SPL DETECTION ENGINE                   │   │

│  │  • Unauthorized tool access detection               │   │

│  │  • Data exfiltration volume analysis                │   │

│  │  • Privilege escalation monitoring                  │   │

│  │  • Credential access alerting                       │   │

│  │  • Excessive API call rate detection                │   │

│  │  • Off-hours activity flagging                      │   │

│  └─────────────────────────────────────────────────────┘   │

│                                                             │

│  ┌──────────────────────┐  ┌──────────────────────────┐    │

│  │   Splunk MCP Server  │  │  Splunk REST API          │    │

│  │   (AI agent access)  │  │  (port 8089)              │    │

│  └──────────────────────┘  └──────────────┬───────────┘    │

└──────────────────────────────────────────┼─────────────────┘

│

▼

┌─────────────────────────────────────────────────────────────┐

│              AGENTWATCH APPLICATION LAYER                   │

│                                                             │

│  ┌─────────────────────────────────────────────────────┐   │

│  │  app.py (Flask)                                     │   │

│  │                                                     │   │

│  │  GET /           → Live monitoring dashboard        │   │

│  │  GET /api/stats  → KPI metrics from Splunk          │   │

│  │  GET /api/feed   → Live anomaly event stream        │   │

│  │  GET /api/anomaly-types → Breakdown by type         │   │

│  │  GET /api/agent-activity → Per-agent risk scores    │   │

│  │  GET /report     → Executive governance report      │   │

│  └─────────────────────────────────────────────────────┘   │

│                                                             │

│  ┌─────────────────┐    ┌───────────────────────────────┐  │

│  │  Live Dashboard │    │  Governance Report            │  │

│  │  • KPI cards    │    │  • Overall risk score         │  │

│  │  • Anomaly chart│    │  • Agent risk table           │  │

│  │  • Agent chart  │    │  • Incident timeline          │  │

│  │  • Live feed    │    │  • Anomaly breakdown          │  │

│  └─────────────────┘    └───────────────────────────────┘  │

└─────────────────────────────────────────────────────────────┘
## Data Flow
1. AI agents perform tool calls → events structured as JSON
2. Events shipped to Splunk via HEC (port 8088, HTTPS)
3. Splunk indexes events into `agentwatch` index
4. SPL queries run against index to detect anomalies
5. Flask app queries Splunk REST API (port 8089)
6. Dashboard renders live — auto-refreshes every 10 seconds
7. /report generates full HTML governance report on demand

## Key Splunk Capabilities Used
- **Splunk HEC** — Real-time event ingestion
- **Splunk REST API** — Programmatic search execution
- **Splunk MCP Server** — Standardized AI agent connectivity
- **SPL** — Search Processing Language for anomaly detection
- **Splunk Index** — Persistent event storage and retrieval
