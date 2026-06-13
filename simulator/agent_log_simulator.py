#!/usr/bin/env python3
import json, time, random, requests, datetime, sys
from faker import Faker
sys.path.insert(0, '/workspaces/agentwatch')
from simulator.config import (
    SPLUNK_HEC_URL, SPLUNK_HEC_TOKEN, SPLUNK_INDEX,
    LOG_INTERVAL_SECONDS, ANOMALY_RATE,
    AGENTS, ALL_TOOLS, ANOMALY_SCENARIOS
)

fake = Faker()

def send_to_splunk(event):
    url = f"{SPLUNK_HEC_URL}/services/collector/event"
    headers = {
        "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "index": SPLUNK_INDEX,
        "sourcetype": "agentwatch:activity",
        "source": "agentwatch_simulator",
        "event": event
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=5, verify=False)
        return r.status_code == 200
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def generate_normal_event(agent):
    tool = random.choice(agent["allowed_tools"])
    return {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "agent_id": agent["id"],
        "agent_name": agent["name"],
        "agent_role": agent["role"],
        "event_type": "tool_call",
        "tool_called": tool,
        "authorized": True,
        "anomaly": False,
        "anomaly_type": None,
        "severity": "INFO",
        "data_volume_mb": round(random.uniform(0.1, 50.0), 2),
        "duration_ms": random.randint(50, 2000),
        "target_resource": fake.uri_path(),
        "source_ip": fake.ipv4_private(),
        "session_id": fake.uuid4(),
        "call_count_last_5min": random.randint(1, 20),
        "description": f"{agent['name']} called {tool} as part of normal workflow"
    }

def generate_anomaly_event(agent):
    scenario = random.choice(ANOMALY_SCENARIOS)
    forbidden = [t for t in ALL_TOOLS if t not in agent["allowed_tools"]]
    if scenario["type"] == "unauthorized_tool_access":
        tool = random.choice(forbidden) if forbidden else "export_all_data"
        authorized = False
    elif scenario["type"] == "data_exfiltration_attempt":
        tool = "export_all_data"
        authorized = False
    elif scenario["type"] == "privilege_escalation":
        tool = "modify_permissions"
        authorized = False
    elif scenario["type"] == "credential_access":
        tool = "access_credentials"
        authorized = False
    elif scenario["type"] == "excessive_api_calls":
        tool = random.choice(agent["allowed_tools"])
        authorized = True
    else:
        tool = random.choice(agent["allowed_tools"])
        authorized = True
    return {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "agent_id": agent["id"],
        "agent_name": agent["name"],
        "agent_role": agent["role"],
        "event_type": "tool_call",
        "tool_called": tool,
        "authorized": authorized,
        "anomaly": True,
        "anomaly_type": scenario["type"],
        "severity": scenario["severity"],
        "data_volume_mb": round(random.uniform(200.0, 5000.0), 2) if "data" in scenario["type"] else round(random.uniform(0.1, 50.0), 2),
        "duration_ms": random.randint(50, 2000),
        "target_resource": fake.uri_path(),
        "source_ip": fake.ipv4_private(),
        "session_id": fake.uuid4(),
        "call_count_last_5min": random.randint(80, 500) if scenario["type"] == "excessive_api_calls" else random.randint(1, 20),
        "description": scenario["description"]
    }

def run_simulator(total_events=200):
    print("\n" + "="*60)
    print("  AgentWatch - AI Agent Log Simulator")
    print("="*60)
    print(f"  Target:       {SPLUNK_HEC_URL}")
    print(f"  Index:        {SPLUNK_INDEX}")
    print(f"  Events:       {total_events}")
    print(f"  Anomaly rate: {ANOMALY_RATE*100:.0f}%")
    print("="*60 + "\n")

    success = 0
    failed = 0
    anomalies = 0

    for i in range(total_events):
        agent = random.choice(AGENTS)
        is_anomaly = random.random() < ANOMALY_RATE
        if is_anomaly:
            event = generate_anomaly_event(agent)
            anomalies += 1
            tag = f"  ANOMALY [{event['severity']}] {agent['name']} -> {event['tool_called']} ({event['anomaly_type']})"
        else:
            event = generate_normal_event(agent)
            tag = f"  NORMAL  {agent['name']} -> {event['tool_called']}"

        sent = send_to_splunk(event)
        if sent:
            success += 1
            print(f"[{i+1:03d}/{total_events}] {tag}")
        else:
            failed += 1
            print(f"[{i+1:03d}/{total_events}]  FAILED to send")

        time.sleep(LOG_INTERVAL_SECONDS)

    print("\n" + "="*60)
    print(f"  Sent:      {success}")
    print(f"  Anomalies: {anomalies}")
    print(f"  Failed:    {failed}")
    print("="*60 + "\n")

if __name__ == "__main__":
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    run_simulator(total)
