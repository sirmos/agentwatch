# AgentWatch Configuration
# All settings flow from .env file — nothing hardcoded

import os
from dotenv import load_dotenv

load_dotenv()

# Splunk HEC Settings
SPLUNK_HEC_URL = os.getenv("SPLUNK_HEC_URL", "http://localhost:8088")
SPLUNK_HEC_TOKEN = os.getenv("SPLUNK_HEC_TOKEN", "")
SPLUNK_INDEX = os.getenv("SPLUNK_INDEX", "agentwatch")

# AgentWatch Settings
LOG_INTERVAL_SECONDS = int(os.getenv("LOG_INTERVAL_SECONDS", "2"))
ANOMALY_RATE = float(os.getenv("ANOMALY_RATE", "0.15"))  # 15% of events are anomalous

# Agent definitions — simulated AI agents in a fake org
AGENTS = [
    {"id": "agent-sec-001",  "name": "SecurityScanner",   "role": "security",     "allowed_tools": ["search_logs", "scan_network", "check_vulnerabilities"]},
    {"id": "agent-ops-002",  "name": "OpsAutomator",      "role": "operations",   "allowed_tools": ["restart_service", "scale_instances", "read_metrics"]},
    {"id": "agent-data-003", "name": "DataPipeline",      "role": "data",         "allowed_tools": ["read_database", "write_database", "transform_data"]},
    {"id": "agent-dev-004",  "name": "CodeReviewer",      "role": "developer",    "allowed_tools": ["read_code", "post_comment", "check_dependencies"]},
    {"id": "agent-hr-005",   "name": "HRAssistant",       "role": "hr",           "allowed_tools": ["read_employee_data", "send_email", "schedule_meeting"]},
]

# All tools available across the system
ALL_TOOLS = [
    "search_logs", "scan_network", "check_vulnerabilities",
    "restart_service", "scale_instances", "read_metrics",
    "read_database", "write_database", "transform_data",
    "read_code", "post_comment", "check_dependencies",
    "read_employee_data", "send_email", "schedule_meeting",
    "delete_records",       # dangerous — no agent should call this normally
    "export_all_data",      # dangerous — classic data exfil tool
    "modify_permissions",   # dangerous — privilege escalation
    "access_credentials",   # dangerous — credential theft
]

# Anomaly scenarios — what rogue agent behavior looks like
ANOMALY_SCENARIOS = [
    {
        "type": "unauthorized_tool_access",
        "description": "Agent called a tool outside its permitted scope",
        "severity": "HIGH"
    },
    {
        "type": "data_exfiltration_attempt",
        "description": "Agent attempted to export abnormally large volume of data",
        "severity": "CRITICAL"
    },
    {
        "type": "privilege_escalation",
        "description": "Agent attempted to modify its own permissions",
        "severity": "CRITICAL"
    },
    {
        "type": "credential_access",
        "description": "Agent accessed credential store outside normal workflow",
        "severity": "CRITICAL"
    },
    {
        "type": "excessive_api_calls",
        "description": "Agent made abnormally high number of calls in short window",
        "severity": "MEDIUM"
    },
    {
        "type": "off_hours_activity",
        "description": "Agent was active outside its normal operating schedule",
        "severity": "MEDIUM"
    },
]
