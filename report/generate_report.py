#!/usr/bin/env python3
"""
AgentWatch - Audit Report Generator
Generates a one-click governance report from Splunk data
"""
import requests, json, urllib3, datetime
urllib3.disable_warnings()

SPLUNK_URL = "https://localhost:8089"
AUTH = ("admin", "AgentWatch2026!")

def splunk_search(spl, earliest="-24h"):
    r = requests.post(
        f"{SPLUNK_URL}/services/search/jobs/export",
        auth=AUTH,
        data={"search": spl, "output_mode": "json", "earliest_time": earliest},
        verify=False, timeout=15
    )
    results = []
    for line in r.text.strip().split("\n"):
        try:
            d = json.loads(line)
            if "result" in d:
                results.append(d["result"])
        except:
            pass
    return results

def generate_report():
    now = datetime.datetime.utcnow()
    
    # Gather all data
    total = splunk_search("search index=agentwatch | stats count")
    anomalies = splunk_search("search index=agentwatch anomaly=true | stats count")
    critical = splunk_search("search index=agentwatch severity=CRITICAL | stats count")
    high = splunk_search("search index=agentwatch severity=HIGH | stats count")
    by_type = splunk_search("search index=agentwatch anomaly=true | stats count by anomaly_type")
    by_agent = splunk_search("search index=agentwatch | eval is_anomaly=if(anomaly==\"true\",1,0) | stats count as total, sum(is_anomaly) as anomalies by agent_name")
    top_incidents = splunk_search("search index=agentwatch severity=CRITICAL OR severity=HIGH | sort -_time | head 5 | table timestamp, agent_name, tool_called, severity, anomaly_type, description")

    total_count = int(total[0].get("count", 0)) if total else 0
    anomaly_count = int(anomalies[0].get("count", 0)) if anomalies else 0
    critical_count = int(critical[0].get("count", 0)) if critical else 0
    high_count = int(high[0].get("count", 0)) if high else 0
    anomaly_rate = round((anomaly_count / total_count * 100), 1) if total_count > 0 else 0
    
    # Risk score (0-100)
    risk_score = min(100, (critical_count * 10) + (high_count * 5) + (anomaly_count * 2))
    risk_label = "CRITICAL" if risk_score >= 70 else "HIGH" if risk_score >= 40 else "MEDIUM" if risk_score >= 20 else "LOW"
    risk_color = "#ff4d6d" if risk_score >= 70 else "#ffa040" if risk_score >= 40 else "#ffd166" if risk_score >= 20 else "#06d6a0"

    # Build agent rows
    agent_rows = ""
    for a in by_agent:
        name = a.get("agent_name", "Unknown")
        tot = int(a.get("total", 0))
        anom = int(a.get("anomalies", 0))
        rate = round(anom/tot*100, 1) if tot > 0 else 0
        status = "🔴 HIGH RISK" if rate > 20 else "🟡 MONITOR" if rate > 10 else "🟢 NORMAL"
        agent_rows += f"""
        <tr>
          <td>{name}</td>
          <td>{tot}</td>
          <td>{anom}</td>
          <td>{rate}%</td>
          <td>{status}</td>
        </tr>"""

    # Build anomaly type rows
    type_rows = ""
    for t in by_type:
        atype = t.get("anomaly_type", "unknown").replace("_", " ").title()
        count = t.get("count", 0)
        type_rows += f"<tr><td>{atype}</td><td>{count}</td></tr>"

    # Build incident rows
    incident_rows = ""
    for i in top_incidents:
        sev = i.get("severity", "INFO")
        sev_color = "#ff4d6d" if sev == "CRITICAL" else "#ffa040" if sev == "HIGH" else "#ffd166"
        incident_rows += f"""
        <tr>
          <td><span style="color:{sev_color};font-weight:700">{sev}</span></td>
          <td>{i.get("agent_name","?")}</td>
          <td>{i.get("tool_called","?")}</td>
          <td>{(i.get("anomaly_type","")).replace("_"," ").title()}</td>
          <td style="font-size:11px;color:#6b7db3">{i.get("description","")}</td>
          <td style="font-size:11px">{str(i.get("timestamp",""))[:19]}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>AgentWatch Governance Report</title>
<style>
  body{{font-family:'Segoe UI',sans-serif;background:#f8faff;color:#1a2340;margin:0;padding:40px}}
  .report{{max-width:900px;margin:0 auto;background:white;border-radius:16px;box-shadow:0 4px 40px #0002;overflow:hidden}}
  .header{{background:linear-gradient(135deg,#0d1226,#1a2744);color:white;padding:40px;}}
  .header h1{{font-size:28px;font-weight:800;margin:0 0 4px}}
  .header p{{font-size:13px;color:#6b8fd4;margin:0}}
  .header .meta{{margin-top:20px;font-size:12px;color:#4a6fa8}}
  .risk-banner{{padding:24px 40px;display:flex;align-items:center;gap:20px;border-bottom:1px solid #e8edf5}}
  .risk-score{{width:80px;height:80px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:800;color:white;background:{risk_color}}}
  .risk-info h2{{font-size:20px;font-weight:700;color:{risk_color};margin:0 0 4px}}
  .risk-info p{{font-size:13px;color:#6b7db3;margin:0}}
  .kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border-bottom:1px solid #e8edf5}}
  .kpi{{padding:24px;border-right:1px solid #e8edf5;text-align:center}}
  .kpi:last-child{{border-right:none}}
  .kpi .val{{font-size:36px;font-weight:800;color:#1a2340}}
  .kpi .val.red{{color:#ff4d6d}}
  .kpi .val.orange{{color:#ffa040}}
  .kpi label{{font-size:11px;color:#9aabcc;text-transform:uppercase;letter-spacing:1px;display:block;margin-bottom:6px}}
  .section{{padding:32px 40px;border-bottom:1px solid #e8edf5}}
  .section h3{{font-size:14px;font-weight:700;color:#1a2340;text-transform:uppercase;letter-spacing:1px;margin:0 0 16px}}
  table{{width:100%;border-collapse:collapse;font-size:13px}}
  th{{text-align:left;padding:10px 12px;background:#f0f4ff;color:#6b7db3;font-size:11px;text-transform:uppercase;letter-spacing:0.5px}}
  td{{padding:10px 12px;border-bottom:1px solid #f0f4ff;color:#2d3f6a}}
  tr:last-child td{{border-bottom:none}}
  .footer{{padding:24px 40px;background:#f8faff;font-size:12px;color:#9aabcc;text-align:center}}
  @media print{{body{{padding:0}}.report{{box-shadow:none;border-radius:0}}}}
</style>
</head>
<body>
<div class="report">
  <div class="header">
    <h1>🔍 AgentWatch Governance Report</h1>
    <p>AI Agent Trust & Audit Summary — Generated by AgentWatch</p>
    <div class="meta">
      Report Period: Last 24 Hours &nbsp;|&nbsp;
      Generated: {now.strftime("%Y-%m-%d %H:%M:%S")} UTC &nbsp;|&nbsp;
      Powered by Splunk + Foundation-sec
    </div>
  </div>

  <div class="risk-banner">
    <div class="risk-score">{risk_score}</div>
    <div class="risk-info">
      <h2>Overall Risk: {risk_label}</h2>
      <p>Risk score based on {anomaly_count} anomalies across {total_count} total agent events.<br>
      {critical_count} critical incidents require immediate investigation.</p>
    </div>
  </div>

  <div class="kpis">
    <div class="kpi"><label>Total Events</label><div class="val">{total_count}</div></div>
    <div class="kpi"><label>Anomalies</label><div class="val red">{anomaly_count}</div></div>
    <div class="kpi"><label>Critical</label><div class="val orange">{critical_count}</div></div>
    <div class="kpi"><label>Anomaly Rate</label><div class="val">{anomaly_rate}%</div></div>
  </div>

  <div class="section">
    <h3>Agent Risk Summary</h3>
    <table>
      <tr><th>Agent</th><th>Total Calls</th><th>Anomalies</th><th>Anomaly Rate</th><th>Status</th></tr>
      {agent_rows}
    </table>
  </div>

  <div class="section">
    <h3>Anomaly Breakdown by Type</h3>
    <table>
      <tr><th>Anomaly Type</th><th>Count</th></tr>
      {type_rows}
    </table>
  </div>

  <div class="section">
    <h3>Top Critical & High Incidents</h3>
    <table>
      <tr><th>Severity</th><th>Agent</th><th>Tool</th><th>Type</th><th>Description</th><th>Time</th></tr>
      {incident_rows}
    </table>
  </div>

  <div class="footer">
    AgentWatch — AI Agent Governance & Trust Auditor &nbsp;|&nbsp;
    Built for Splunk Agentic Ops Hackathon 2026 &nbsp;|&nbsp;
    Data source: Splunk index=agentwatch
  </div>
</div>
</body></html>"""

    return html

if __name__ == "__main__":
    print("Generating report...")
    html = generate_report()
    with open("/tmp/agentwatch_report.html", "w") as f:
        f.write(html)
    print("✅ Report saved to /tmp/agentwatch_report.html")
