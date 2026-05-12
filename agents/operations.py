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

INVENTORY = [
    {"item": "Laptop",          "qty": 3,  "min_qty": 5,  "unit_cost": 55000, "status": "low"},
    {"item": "Office Chairs",   "qty": 12, "min_qty": 10, "unit_cost": 4500,  "status": "ok"},
    {"item": "Server RAM 32GB", "qty": 2,  "min_qty": 4,  "unit_cost": 8000,  "status": "low"},
    {"item": "Printer Paper",   "qty": 45, "min_qty": 20, "unit_cost": 350,   "status": "ok"},
    {"item": "UPS Units",       "qty": 1,  "min_qty": 3,  "unit_cost": 12000, "status": "critical"},
]

VENDORS = [
    {"id": "V001", "name": "TechZone Pvt Ltd",  "category": "IT Hardware",  "rating": 4.5, "payment_terms": "Net 30"},
    {"id": "V002", "name": "Officemart",         "category": "Office Supply","rating": 4.2, "payment_terms": "Net 15"},
    {"id": "V003", "name": "CloudServe India",   "category": "IT Services",  "rating": 4.8, "payment_terms": "Monthly"},
]

TASKS = [
    {"id": "T001", "task": "Setup new employee workstation",  "dept": "IT",        "priority": "high",   "status": "pending"},
    {"id": "T002", "task": "Quarterly office deep cleaning",  "dept": "Admin",     "priority": "medium", "status": "pending"},
    {"id": "T003", "task": "Renew internet service contract", "dept": "IT",        "priority": "high",   "status": "pending"},
    {"id": "T004", "task": "Restock printer consumables",     "dept": "Admin",     "priority": "low",    "status": "pending"},
]


def check_inventory() -> dict:
    print(f"\n📦 Operations Agent — Inventory Check")
    print("─" * 45)

    low      = [i for i in INVENTORY if i["status"] in ("low", "critical")]
    reorder  = []

    for item in INVENTORY:
        flag = "🔴" if item["status"] == "critical" else "⚠️ " if item["status"] == "low" else "✅"
        print(f"  {flag} {item['item']:20s} | Qty: {item['qty']:3} | Min: {item['min_qty']} | ₹{item['unit_cost']:,}")
        if item["status"] in ("low", "critical"):
            needed = item["min_qty"] - item["qty"] + 2
            reorder.append({**item, "reorder_qty": needed, "reorder_cost": needed * item["unit_cost"]})

    total_reorder_cost = sum(r["reorder_cost"] for r in reorder)
    print(f"\n  Items needing reorder : {len(reorder)}")
    print(f"  Total reorder cost    : ₹{total_reorder_cost:,}")

    return {"low_items": low, "reorder_list": reorder,
            "total_reorder_cost": total_reorder_cost, "needs_procurement": len(reorder) > 0}


def manage_tasks() -> dict:
    print(f"\n✅ Operations Agent — Task Management")
    print("─" * 45)

    for t in TASKS:
        flag = "🔴" if t["priority"] == "high" else "🟡" if t["priority"] == "medium" else "🟢"
        print(f"  {flag} {t['id']} | {t['task']:40s} | {t['dept']}")

    prompt = f"""
Tasks list: {json.dumps(TASKS)}
Prioritize these tasks and suggest who should handle each.
Reply as JSON array only:
[{{"id": "T001", "suggested_owner": "...", "reason": "..."}}]
"""
    response = llm.invoke(prompt)
    raw   = response.content.strip().replace("```json","").replace("```","").strip()
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    try:
        suggestions = json.loads(match.group()) if match else []
    except:
        suggestions = []

    print(f"\n  💡 AI Task Assignments:")
    for s in suggestions:
        print(f"     {s.get('id')} → {s.get('suggested_owner','')}: {s.get('reason','')[:50]}")

    return {"total_tasks": len(TASKS), "tasks": TASKS, "ai_assignments": suggestions}


def vendor_coordination() -> dict:
    print(f"\n🤝 Operations Agent — Vendor Coordination")
    print("─" * 45)

    for v in VENDORS:
        print(f"  {v['id']} | {v['name']:22s} | {v['category']:15s} | ⭐ {v['rating']} | {v['payment_terms']}")

    prompt = f"""
Vendors: {json.dumps(VENDORS)}
Suggest which vendor to prioritize for a ₹80,000 IT hardware purchase.
Reply as JSON only: {{"vendor_id": "V001", "reason": "...", "negotiation_tip": "..."}}
"""
    response = llm.invoke(prompt)
    raw   = response.content.strip().replace("```json","").replace("```","").strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    try:
        rec = json.loads(match.group()) if match else {}
    except:
        rec = {}

    print(f"\n  💡 Recommended: {rec.get('vendor_id','')}")
    print(f"  Reason         : {rec.get('reason','')[:70]}")
    print(f"  Negotiation tip: {rec.get('negotiation_tip','')[:70]}")

    return {"vendors": VENDORS, "recommendation": rec}


def run_operations_agent(action: str, **kwargs) -> AgentState:
    state = new_state(task=f"Operations:{action}", agent="operations", priority="medium")

    if action == "inventory":
        result = check_inventory()
        if result["needs_procurement"]:
            state["needs_ceo_approval"] = True
            state["task"] = f"Operations: Reorder needed — ₹{result['total_reorder_cost']:,} required for {len(result['reorder_list'])} items"
            if should_escalate(state):
                state = ceo_review(state)

    elif action == "tasks":
        result = manage_tasks()

    elif action == "vendors":
        result = vendor_coordination()

    else:
        result = {"error": f"Unknown action: {action}"}

    state["result"]     = result
    state["updated_at"] = datetime.now().isoformat()
    return state