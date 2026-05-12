from langchain_groq import ChatGroq
from state.schema import AgentState, new_state
from agents.ceo import should_escalate, ceo_review
from dotenv import load_dotenv
from datetime import datetime
import os, json, re

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)

BUGS = [
    {"id": "BUG001", "title": "Login timeout after 2 mins",         "severity": "high",     "status": "open",   "reporter": "Rahul Das"},
    {"id": "BUG002", "title": "PDF export fails on Safari",          "severity": "medium",   "status": "open",   "reporter": "Anjali Singh"},
    {"id": "BUG003", "title": "WhatsApp webhook delay > 30s",        "severity": "high",     "status": "open",   "reporter": "Dev Malhotra"},
    {"id": "BUG004", "title": "Dashboard charts not loading on mobile","severity": "medium",  "status": "open",   "reporter": "Pooja Sharma"},
    {"id": "BUG005", "title": "CSV import throws 500 on large files", "severity": "low",     "status": "open",   "reporter": "Ravi Nambiar"},
]

ROADMAP = [
    {"feature": "Mobile App (Android + iOS)",     "priority": "high",   "sprint": "Sprint 3", "status": "planned"},
    {"feature": "Multi-language support",          "priority": "medium", "sprint": "Sprint 4", "status": "planned"},
    {"feature": "Advanced Analytics Dashboard",    "priority": "high",   "sprint": "Sprint 3", "status": "in_progress"},
    {"feature": "Zapier Integration",              "priority": "medium", "sprint": "Sprint 5", "status": "planned"},
    {"feature": "WhatsApp Bot v2",                 "priority": "high",   "sprint": "Sprint 3", "status": "in_progress"},
]

SECURITY_CHECKS = [
    {"check": "SSL Certificate",         "status": "valid",    "expiry": "2027-01-01"},
    {"check": "API Rate Limiting",        "status": "enabled",  "expiry": None},
    {"check": "SQL Injection Protection", "status": "enabled",  "expiry": None},
    {"check": "2FA for Admin Accounts",   "status": "disabled", "expiry": None},
    {"check": "Data Backup",              "status": "enabled",  "expiry": None},
    {"check": "Dependency Audit",         "status": "overdue",  "expiry": "2026-04-01"},
]


def triage_bugs() -> dict:
    print(f"\n🐛 IT/Dev Agent — Bug Triage")
    print("─" * 45)

    for bug in BUGS:
        flag = "🔴" if bug["severity"] == "high" else "🟡" if bug["severity"] == "medium" else "🟢"
        print(f"  {flag} {bug['id']} | {bug['title']:45s} | {bug['reporter']}")

    high = [b for b in BUGS if b["severity"] == "high"]

    prompt = f"""
Bug list: {json.dumps(BUGS)}
Prioritize and assign these bugs to fix order 1-5.
Reply as JSON array only:
[{{"id": "BUG001", "fix_order": 1, "reason": "...", "estimated_hours": 2}}]
"""
    response = llm.invoke(prompt)
    raw   = response.content.strip().replace("```json","").replace("```","").strip()
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    try:
        priorities = json.loads(match.group()) if match else []
    except:
        priorities = []

    print(f"\n  💡 AI Fix Order:")
    for p in sorted(priorities, key=lambda x: x.get("fix_order", 99)):
        print(f"     #{p.get('fix_order')} {p.get('id')} | ~{p.get('estimated_hours','?')}h | {p.get('reason','')[:50]}")

    return {"total_bugs": len(BUGS), "high_severity": len(high),
            "bugs": BUGS, "fix_priorities": priorities}


def security_audit() -> dict:
    print(f"\n🔒 IT/Dev Agent — Security Audit")
    print("─" * 45)

    issues = []
    for check in SECURITY_CHECKS:
        flag = "✅" if check["status"] in ("valid","enabled") else "🔴"
        print(f"  {flag} {check['check']:30s} | {check['status'].upper()}")
        if check["status"] in ("disabled", "overdue"):
            issues.append(check)

    if issues:
        print(f"\n  ⚠️  {len(issues)} security issues found — critical")

    return {"total_checks": len(SECURITY_CHECKS), "issues": issues,
            "issues_count": len(issues), "score": round((len(SECURITY_CHECKS)-len(issues))/len(SECURITY_CHECKS)*100)}


def product_roadmap() -> dict:
    print(f"\n🗺️  IT/Dev Agent — Product Roadmap")
    print("─" * 45)

    for item in ROADMAP:
        flag = "🔴" if item["priority"] == "high" else "🟡"
        status_icon = "🔄" if item["status"] == "in_progress" else "📅"
        print(f"  {flag} {status_icon} {item['feature']:35s} | {item['sprint']} | {item['status']}")

    in_progress = [r for r in ROADMAP if r["status"] == "in_progress"]
    planned     = [r for r in ROADMAP if r["status"] == "planned"]

    return {"total_features": len(ROADMAP), "in_progress": in_progress,
            "planned": planned, "roadmap": ROADMAP}


def run_it_agent(action: str, **kwargs) -> AgentState:
    state = new_state(task=f"IT:{action}", agent="it_dev", priority="medium")

    if action == "bugs":
        result = triage_bugs()
        if result["high_severity"] > 0:
            state["needs_ceo_approval"] = True
            state["task"] = f"IT: {result['high_severity']} HIGH severity bugs active — including login timeout & WhatsApp delay"
            if should_escalate(state):
                state = ceo_review(state)

    elif action == "security":
        result = security_audit()
        if result["issues_count"] > 0:
            state["needs_ceo_approval"] = True
            state["priority"]           = "critical"
            state["task"] = f"CRITICAL: {result['issues_count']} security issues — 2FA disabled, dependency audit overdue. Security score: {result['score']}%"
            if should_escalate(state):
                state = ceo_review(state)

    elif action == "roadmap":
        result = product_roadmap()

    else:
        result = {"error": f"Unknown action: {action}"}

    state["result"]     = result
    state["updated_at"] = datetime.now().isoformat()
    return state