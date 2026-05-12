from langchain_groq import ChatGroq
from state.schema import AgentState, new_state
from agents.ceo import should_escalate, ceo_review
from dotenv import load_dotenv
from datetime import datetime
import os, json, re

import json as json_lib

def load_laws():
    law_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'indian_laws.json')
    with open(law_path, 'r', encoding='utf-8') as f:
        return json_lib.load(f)

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,
)

CONTRACTS = [
    {"id": "CT001", "party": "DevTech Solutions",  "type": "Service Agreement",   "value": 320000, "expiry": "2026-12-31", "status": "active"},
    {"id": "CT002", "party": "Mehta & Co",          "type": "NDA",                 "value": 0,      "expiry": "2026-06-01", "status": "expiring_soon"},
    {"id": "CT003", "party": "Sharma Vendors",      "type": "Vendor Contract",     "value": 85000,  "expiry": "2026-05-15", "status": "expiring_soon"},
    {"id": "CT004", "party": "Ravi Nambiar",        "type": "Consulting Agreement","value": 95000,  "expiry": "2027-03-01", "status": "active"},
]

COMPLIANCE_DEADLINES = [
    {"task": "GST Filing Q4",          "due": "2026-05-10", "dept": "Finance",   "status": "pending"},
    {"task": "TDS Return",             "due": "2026-05-07", "dept": "Finance",   "status": "overdue"},
    {"task": "Employee PF Deposit",    "due": "2026-05-15", "dept": "HR",        "status": "pending"},
    {"task": "Annual ROC Filing",      "due": "2026-06-30", "dept": "Legal",     "status": "pending"},
    {"task": "MSME Udyam Renewal",     "due": "2026-05-20", "dept": "Admin",     "status": "pending"},
]

def check_law_compliance(situation: str, dept: str = "hr") -> dict:
    print(f"\n⚖️  Legal Agent — Indian Law Compliance Check")
    print(f"  Situation: {situation[:60]}")
    print("─" * 55)

    laws     = load_laws()
    relevant = []

    # keyword matching against all laws
    situation_lower = situation.lower()
    for law in laws["labour_laws"]:
        if any(kw in situation_lower for kw in law["keywords"]):
            relevant.append(law)
            print(f"  📜 APPLICABLE: {law['act']} — {law['section']}")
            print(f"     Rule   : {law['rule'][:80]}...")
            print(f"     Penalty: {law['penalty']}")

    # also check NOC requirements
    noc_relevant = []
    for noc in laws["noc_requirements"]:
        if any(kw in situation_lower for kw in
               ["hire", "recruit", "project", "government", "noc"]):
            noc_relevant.append(noc)

    if not relevant:
        print(f"  ✅ No specific law violations detected for this situation")

    # Ask LLM for legal advice
    prompt = f"""
You are an Indian corporate lawyer.
Situation: {situation}
Applicable laws found: {json_lib.dumps([l['act']+' '+l['section'] for l in relevant])}

Give specific legal advice in JSON only:
{{
  "risk_level": "high/medium/low",
  "immediate_action": "what to do right now",
  "documents_needed": ["doc1", "doc2"],
  "timeline": "how long to comply",
  "legal_warning": "one line warning if risk is high"
}}
"""
    response = llm.invoke(prompt)
    raw      = response.content.strip().replace("```json","").replace("```","").strip()
    import re
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    try:
        advice = json_lib.loads(match.group()) if match else {}
    except:
        advice = {}

    risk = advice.get("risk_level", "low")
    flag = "🔴" if risk == "high" else "🟡" if risk == "medium" else "✅"
    print(f"\n  {flag} Risk Level     : {risk.upper()}")
    print(f"  ⚡ Immediate Action: {advice.get('immediate_action','')[:70]}")
    print(f"  📅 Timeline        : {advice.get('timeline','')}")
    if advice.get("legal_warning"):
        print(f"  ⚠️  WARNING        : {advice.get('legal_warning','')}")

    return {
        "situation":        situation,
        "applicable_laws":  relevant,
        "noc_requirements": noc_relevant,
        "legal_advice":     advice,
        "risk_level":       risk,
        "laws_triggered":   len(relevant),
    }

def review_contracts() -> dict:
    print(f"\n⚖️  Legal Agent — Contract Review")
    print("─" * 45)

    expiring = [c for c in CONTRACTS if c["status"] == "expiring_soon"]
    active   = [c for c in CONTRACTS if c["status"] == "active"]

    for c in CONTRACTS:
        flag = "⚠️ " if c["status"] == "expiring_soon" else "✅"
        print(f"  {flag} {c['id']} | {c['party']:22s} | {c['type']:22s} | Exp: {c['expiry']}")

    if expiring:
        print(f"\n  ⚠️  {len(expiring)} contracts expiring soon — needs CEO attention")

    return {"total": len(CONTRACTS), "active": len(active),
            "expiring_soon": expiring, "needs_renewal": len(expiring)}


def check_compliance() -> dict:
    print(f"\n📋 Legal Agent — Compliance Check")
    print("─" * 45)

    overdue  = [t for t in COMPLIANCE_DEADLINES if t["status"] == "overdue"]
    pending  = [t for t in COMPLIANCE_DEADLINES if t["status"] == "pending"]

    for t in COMPLIANCE_DEADLINES:
        flag = "🔴" if t["status"] == "overdue" else "🟡"
        print(f"  {flag} {t['task']:30s} | Due: {t['due']} | {t['dept']}")

    if overdue:
        print(f"\n  🔴 {len(overdue)} OVERDUE — immediate action required")

    return {"total": len(COMPLIANCE_DEADLINES), "overdue": overdue,
            "pending": pending, "overdue_count": len(overdue)}


def generate_policy(policy_type: str) -> dict:
    print(f"\n📜 Legal Agent — Generating Policy: {policy_type}")
    print("─" * 45)

    prompt = f"""
Generate a concise {policy_type} policy for an Indian SME/startup in JSON format only.
{{
  "policy_name": "...",
  "effective_date": "...",
  "sections": [
    {{"title": "...", "content": "2 sentences"}},
    {{"title": "...", "content": "2 sentences"}},
    {{"title": "...", "content": "2 sentences"}}
  ],
  "approved_by": "CEO",
  "version": "1.0"
}}
"""
    response = llm.invoke(prompt)
    raw   = response.content.strip().replace("```json","").replace("```","").strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    try:
        policy = json.loads(match.group()) if match else {}
    except:
        policy = {}

    print(f"  📄 Policy : {policy.get('policy_name','')}")
    print(f"  📅 Date   : {policy.get('effective_date','')}")
    for s in policy.get("sections", []):
        print(f"  • {s.get('title','')}")

    return {"policy_type": policy_type, "policy": policy}


def run_legal_agent(action: str, **kwargs) -> AgentState:
    state = new_state(task=f"Legal:{action}", agent="legal", priority="medium")

    if action == "contracts":
        result = review_contracts()
        if result["needs_renewal"] > 0:
            state["needs_ceo_approval"] = True
            state["task"] = f"Legal: {result['needs_renewal']} contracts expiring soon need CEO review"
            if should_escalate(state):
                state = ceo_review(state)
    
    elif action == "lawcheck":
        result = check_law_compliance(
            situation=kwargs.get("situation", "employee termination"),
            dept=kwargs.get("dept", "hr")
        )
        if result["risk_level"] == "high":
            state["needs_ceo_approval"] = True
            state["priority"]           = "critical"
            state["task"] = f"LEGAL RISK: {result['laws_triggered']} laws triggered for — {kwargs.get('situation','')[:50]}"
            if should_escalate(state):
                state = ceo_review(state)

    elif action == "compliance":
        result = check_compliance()
        if result["overdue_count"] > 0:
            state["needs_ceo_approval"] = True
            state["priority"]           = "critical"
            state["task"] = f"CRITICAL: {result['overdue_count']} compliance deadlines OVERDUE — legal risk"
            if should_escalate(state):
                state = ceo_review(state)


    elif action == "policy":
        result = generate_policy(policy_type=kwargs.get("policy_type", "Remote Work"))
        

    else:
        result = {"error": f"Unknown action: {action}"}

    state["result"]     = result
    state["updated_at"] = datetime.now().isoformat()
    return state