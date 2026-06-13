#!/usr/bin/env python3
from flask import Flask, jsonify, render_template_string
import requests, json, urllib3
urllib3.disable_warnings()

app = Flask(__name__)
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

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AgentWatch - AI Agent Governance</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#080c18;color:#e0e6ff;min-height:100vh}
header{background:#0d1226;border-bottom:2px solid #1e3a8a;padding:18px 32px;display:flex;align-items:center;justify-content:space-between}
.logo{display:flex;align-items:center;gap:12px}
.logo h1{font-size:24px;font-weight:800;background:linear-gradient(135deg,#4f8ef7,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.logo p{font-size:12px;color:#6b7db3;margin-top:2px}
.live{display:flex;align-items:center;gap:6px;background:#0a2a1a;border:1px solid #06d6a044;padding:6px 14px;border-radius:20px;font-size:12px;color:#06d6a0}
.dot{width:8px;height:8px;background:#06d6a0;border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:24px 32px 0}
.kpi{background:#0d1226;border:1px solid #1e2d5a;border-radius:14px;padding:22px;position:relative;overflow:hidden}
.kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:3px}
.kpi.blue::before{background:linear-gradient(90deg,#4f8ef7,#06d6a0)}
.kpi.red::before{background:linear-gradient(90deg,#ff4d6d,#ffa040)}
.kpi.yellow::before{background:linear-gradient(90deg,#ffd166,#ffa040)}
.kpi.green::before{background:linear-gradient(90deg,#06d6a0,#4f8ef7)}
.kpi label{font-size:11px;color:#6b7db3;text-transform:uppercase;letter-spacing:1.5px}
.kpi .val{font-size:42px;font-weight:800;margin:6px 0 4px;line-height:1}
.kpi.blue .val{color:#4f8ef7}
.kpi.red .val{color:#ff4d6d}
.kpi.yellow .val{color:#ffd166}
.kpi.green .val{color:#06d6a0}
.kpi .sub{font-size:11px;color:#3d4f7a}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:16px 32px}
.panel{background:#0d1226;border:1px solid #1e2d5a;border-radius:14px;padding:22px}
.panel h3{font-size:11px;color:#6b7db3;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:18px}
.feed{padding:0 32px 32px}
.panel-full{background:#0d1226;border:1px solid #1e2d5a;border-radius:14px;padding:22px}
.panel-full h3{font-size:11px;color:#6b7db3;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:18px;display:flex;justify-content:space-between;align-items:center}
.btn{background:#1a2744;border:1px solid #2d4080;color:#4f8ef7;padding:5px 14px;border-radius:6px;cursor:pointer;font-size:11px;text-transform:uppercase;letter-spacing:1px}
.btn:hover{background:#2d4080}
.event{display:flex;align-items:center;gap:14px;padding:12px 0;border-bottom:1px solid #111827}
.event:last-child{border:none}
.badge{padding:4px 10px;border-radius:20px;font-size:10px;font-weight:700;min-width:72px;text-align:center;letter-spacing:0.5px}
.CRITICAL{background:#1a0a10;color:#ff4d6d;border:1px solid #ff4d6d55}
.HIGH{background:#1a1000;color:#ffa040;border:1px solid #ffa04055}
.MEDIUM{background:#1a1a00;color:#ffd166;border:1px solid #ffd16655}
.INFO{background:#001a12;color:#06d6a0;border:1px solid #06d6a055}
.ev-info{flex:1}
.ev-agent{font-size:13px;font-weight:600;color:#c7d4f7}
.ev-desc{font-size:11px;color:#4a5f8a;margin-top:3px}
.ev-time{font-size:10px;color:#2d3f6a;white-space:nowrap}
.empty{color:#2d3f6a;font-size:13px;padding:20px 0;text-align:center}
</style>
</head>
<body>
<header>
  <div class="logo">
    <div>
      <h1>🔍 AgentWatch</h1>
      <p>AI Agent Governance & Trust Auditor — Splunk Agentic Ops Hackathon 2026</p>
    </div>
  </div>
  <div class="live"><span class="dot"></span> LIVE MONITORING</div>
</header>

<div class="kpis">
  <div class="kpi blue"><label>Total Events</label><div class="val" id="v-total">—</div><div class="sub">Ingested via Splunk HEC</div></div>
  <div class="kpi red"><label>Anomalies Detected</label><div class="val" id="v-anomalies">—</div><div class="sub">Flagged for review</div></div>
  <div class="kpi yellow"><label>Critical Alerts</label><div class="val" id="v-critical">—</div><div class="sub">Immediate action needed</div></div>
  <div class="kpi green"><label>Agents Monitored</label><div class="val" id="v-agents">—</div><div class="sub">Active AI agents tracked</div></div>
</div>

<div class="charts">
  <div class="panel"><h3>Anomalies by Type</h3><canvas id="c1" height="220"></canvas></div>
  <div class="panel"><h3>Activity per Agent</h3><canvas id="c2" height="220"></canvas></div>
</div>

<div class="feed">
  <div class="panel-full">
    <h3>Live Anomaly Feed <button class="btn" onclick="load()">↻ Refresh</button></h3>
    <div id="feed-body"><div class="empty">Loading...</div></div>
  </div>
</div>

<script>
let c1,c2;
const COLORS=['#ff4d6d','#ffa040','#ffd166','#4f8ef7','#06d6a0','#a855f7'];

async function load(){
  try{
    const [s,at,aa,f]=await Promise.all([
      fetch('/api/stats').then(r=>r.json()),
      fetch('/api/anomaly-types').then(r=>r.json()),
      fetch('/api/agent-activity').then(r=>r.json()),
      fetch('/api/feed').then(r=>r.json())
    ]);
    document.getElementById('v-total').textContent=s.total;
    document.getElementById('v-anomalies').textContent=s.anomalies;
    document.getElementById('v-critical').textContent=s.critical;
    document.getElementById('v-agents').textContent=s.agents;
    drawDoughnut(at);
    drawBar(aa);
    drawFeed(f);
  }catch(e){console.error(e)}
}

function drawDoughnut(data){
  const ctx=document.getElementById('c1').getContext('2d');
  if(c1)c1.destroy();
  c1=new Chart(ctx,{type:'doughnut',data:{
    labels:data.map(d=>d.type?d.type.replace(/_/g,' '):'unknown'),
    datasets:[{data:data.map(d=>d.count),backgroundColor:COLORS,borderWidth:0}]
  },options:{cutout:'68%',plugins:{legend:{position:'bottom',labels:{color:'#6b7db3',font:{size:10},padding:12}}}}});
}

function drawBar(data){
  const ctx=document.getElementById('c2').getContext('2d');
  if(c2)c2.destroy();
  c2=new Chart(ctx,{type:'bar',data:{
    labels:data.map(d=>d.agent),
    datasets:[
      {label:'Normal',data:data.map(d=>Math.max(0,d.total-d.anomalies)),backgroundColor:'#4f8ef733',borderColor:'#4f8ef7',borderWidth:1},
      {label:'Anomalies',data:data.map(d=>d.anomalies),backgroundColor:'#ff4d6d33',borderColor:'#ff4d6d',borderWidth:1}
    ]
  },options:{plugins:{legend:{labels:{color:'#6b7db3',font:{size:10}}}},
    scales:{x:{ticks:{color:'#6b7db3',font:{size:10}},grid:{color:'#111827'}},
            y:{ticks:{color:'#6b7db3',font:{size:10}},grid:{color:'#111827'}}},
    responsive:true}});
}

function drawFeed(events){
  const el=document.getElementById('feed-body');
  if(!events||!events.length){el.innerHTML='<div class="empty">No anomalies in last 24h</div>';return;}
  el.innerHTML=events.map(e=>`
    <div class="event">
      <span class="badge ${e.severity||'INFO'}">${e.severity||'INFO'}</span>
      <div class="ev-info">
        <div class="ev-agent">${e.agent_name||'Unknown'} → <strong>${e.tool_called||'?'}</strong> &nbsp;<span style="color:#3d4f7a;font-size:10px">[${(e.anomaly_type||'').replace(/_/g,' ')}]</span></div>
        <div class="ev-desc">${e.description||''}</div>
      </div>
      <div class="ev-time">${(e.timestamp||'').substring(11,19)} UTC</div>
    </div>`).join('');
}

load();
setInterval(load,10000);
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/stats")
def stats():
    t = splunk_search("search index=agentwatch | stats count")
    a = splunk_search("search index=agentwatch anomaly=true | stats count")
    c = splunk_search("search index=agentwatch severity=CRITICAL | stats count")
    ag = splunk_search("search index=agentwatch | stats dc(agent_name) as count")
    return jsonify({
        "total": t[0].get("count",0) if t else 0,
        "anomalies": a[0].get("count",0) if a else 0,
        "critical": c[0].get("count",0) if c else 0,
        "agents": ag[0].get("count",0) if ag else 0,
    })

@app.route("/api/anomaly-types")
def anomaly_types():
    r = splunk_search("search index=agentwatch anomaly=true anomaly_type!=None | stats count by anomaly_type | rename anomaly_type as type")
    return jsonify(r)

@app.route("/api/agent-activity")
def agent_activity():
    r = splunk_search("search index=agentwatch | eval is_anomaly=if(anomaly==\"true\",1,0) | stats count as total, sum(is_anomaly) as anomalies by agent_name | rename agent_name as agent")
    return jsonify(r)

@app.route("/api/feed")
def feed():
    r = splunk_search("search index=agentwatch anomaly=true | sort -_time | head 25 | table timestamp, agent_name, tool_called, severity, anomaly_type, description")
    return jsonify(r)


@app.route("/report")
def report():
    from report.generate_report import generate_report
    return generate_report()

if __name__=="__main__":
    print("\n🔍 AgentWatch Dashboard running!")
    print("   Visit port 5000 in your Ports tab\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
