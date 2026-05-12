from langchain_groq import ChatGroq
from state.schema import AgentState, new_state
from dotenv import load_dotenv
from datetime import datetime
import os, json, re

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)

# Live KPI data pulled from all departments
COMPANY_KPIS = {
    "revenue":          {"current": 268000, "target": 400000, "unit": "INR"},
    "leads":            {"current": 5,      "target": 20,     "unit": "count"},
    "open_tickets":     {"current": 5,      "target": 2,      "unit": "count"},
    "budget_used_pct":  {"current": 37.4,   "target": 60,     "unit": "percent"},
    "employee_attendance":{"current": 84.6, "target": 95,     "unit": "percent"},
    "active_contracts": {"current": 2,      "target": 5,      "unit": "count"},
    "bugs_open":        {"current": 5,      "target": 0,      "unit": "count"},
    "campaigns_active": {"current": 1,      "target": 3,      "unit": "count"},
}


from state.company_state import get_state, get_activity_log, log_activity
from state.company_state import recalculate_revenue_from_projects
recalculate_revenue_from_projects()

def generate_kpi_report() -> dict:
    print(f"\n📊 Analytics Agent — KPI Dashboard")
    print("─" * 45)

    kpis = get_state()
    on_track, needs_attention = [], []

    for kpi, data in kpis.items():
        pct    = (data["current"] / data["target"] * 100) if data["target"] > 0 else 0
        lower  = kpi in ("open_tickets", "bugs_open")
        good   = (data["current"] <= data["target"]) if lower else (pct >= 70)
        status = "✅" if good else "⚠️ "
        if good:
            on_track.append(kpi)
        else:
            needs_attention.append(kpi)
        print(f"  {status} {kpi:25s} | "
              f"{data['current']:>8} / {data['target']:>8} {data['unit']}")

    print(f"\n  ✅ On Track      : {len(on_track)}")
    print(f"  ⚠️  Needs Attention: {len(needs_attention)}")

    return {
        "kpis":             kpis,
        "on_track":         on_track,
        "needs_attention":  needs_attention,
        "health_score":     round(len(on_track) / len(kpis) * 100),
    }


def daily_summary() -> dict:
    print(f"\n📋 Analytics Agent — Daily Business Summary")
    print("─" * 45)

    prompt = f"""
Generate a concise daily business summary for the CEO based on this data:
KPIs: {json.dumps(COMPANY_KPIS)}
Date: {datetime.now().strftime('%d %B %Y')}

Include: top 3 wins, top 3 concerns, 1 recommended action.
Reply as JSON only:
{{
  "date": "...",
  "health_score": 0,
  "wins": ["win1", "win2", "win3"],
  "concerns": ["concern1", "concern2", "concern3"],
  "recommended_action": "..."
}}
"""
    response = llm.invoke(prompt)
    raw   = response.content.strip().replace("```json","").replace("```","").strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    try:
        summary = json.loads(match.group()) if match else {}
    except:
        summary = {}

    print(f"  📅 Date     : {summary.get('date', datetime.now().strftime('%d %B %Y'))}")
    print(f"  💚 Health   : {summary.get('health_score', 0)}%")
    print(f"\n  🏆 Wins:")
    for w in summary.get("wins", []):
        print(f"     + {w}")
    print(f"\n  ⚠️  Concerns:")
    for c in summary.get("concerns", []):
        print(f"     - {c}")
    print(f"\n  💡 Action   : {summary.get('recommended_action','')}")

    return summary


def anomaly_detection() -> dict:
    print(f"\n🔍 Analytics Agent — Anomaly Detection")
    print("─" * 45)

    anomalies = []

    # Simple rule-based anomaly detection across KPIs
    checks = [
        ("Revenue below 70% of target",     COMPANY_KPIS["revenue"]["current"] < COMPANY_KPIS["revenue"]["target"] * 0.7),
        ("Lead generation critically low",   COMPANY_KPIS["leads"]["current"] < COMPANY_KPIS["leads"]["target"] * 0.5),
        ("Too many open support tickets",    COMPANY_KPIS["open_tickets"]["current"] > COMPANY_KPIS["open_tickets"]["target"] * 2),
        ("Attendance below 85%",             COMPANY_KPIS["employee_attendance"]["current"] < 85),
        ("More than 3 bugs open",            COMPANY_KPIS["bugs_open"]["current"] > 3),
    ]

    for desc, condition in checks:
        if condition:
            anomalies.append(desc)
            print(f"  🚨 ANOMALY: {desc}")
        else:
            print(f"  ✅ OK     : {desc}")

    if not anomalies:
        print(f"\n  ✅ No anomalies detected")
    else:
        print(f"\n  🚨 {len(anomalies)} anomalies detected")

    return {"anomalies": anomalies, "count": len(anomalies),
            "status": "critical" if len(anomalies) >= 3 else "warning" if anomalies else "healthy"}


def run_analytics_agent(action: str, **kwargs) -> AgentState:
    state = new_state(task=f"Analytics:{action}", agent="analytics", priority="low")

    if action == "kpi":
        result = generate_kpi_report()
    elif action == "summary":
        result = daily_summary()
    elif action == "anomaly":
        result = anomaly_detection()
    else:
        result = {"error": f"Unknown action: {action}"}

    state["result"]     = result
    state["updated_at"] = datetime.now().isoformat()
    return state