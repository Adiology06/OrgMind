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

ASSETS = [
    {"id": "A001", "item": "MacBook Pro 14\"",  "assigned_to": "Rahul Das",    "status": "active",      "value": 145000},
    {"id": "A002", "item": "Dell Monitor 27\"",  "assigned_to": "Anjali Singh", "status": "active",      "value": 28000},
    {"id": "A003", "item": "iPhone 15",          "assigned_to": "Unassigned",   "status": "available",   "value": 72000},
    {"id": "A004", "item": "Projector Epson",    "assigned_to": "Conference Room","status": "active",    "value": 45000},
    {"id": "A005", "item": "UPS APC 1500VA",     "assigned_to": "Server Room",  "status": "maintenance", "value": 12000},
]

MEETINGS = [
    {"title": "Weekly Team Standup",       "date": "2026-05-04", "time": "10:00 AM", "attendees": ["All Teams"],         "duration": 30},
    {"title": "Q2 Review with Investors",  "date": "2026-05-07", "time": "03:00 PM", "attendees": ["CEO","Finance","Sales"], "duration": 60},
    {"title": "Product Roadmap Discussion","date": "2026-05-06", "time": "02:00 PM", "attendees": ["IT","Sales","CEO"],   "duration": 45},
]


def manage_assets() -> dict:
    print(f"\n🏢 Admin Agent — Asset Management")
    print("─" * 45)

    total_value  = sum(a["value"] for a in ASSETS)
    available    = [a for a in ASSETS if a["status"] == "available"]
    maintenance  = [a for a in ASSETS if a["status"] == "maintenance"]

    for a in ASSETS:
        flag = "✅" if a["status"] == "active" else "🟡" if a["status"] == "available" else "🔴"
        print(f"  {flag} {a['id']} | {a['item']:22s} | {a['assigned_to']:20s} | ₹{a['value']:,}")

    print(f"\n  Total Asset Value  : ₹{total_value:,}")
    print(f"  Available Assets   : {len(available)}")
    print(f"  Under Maintenance  : {len(maintenance)}")

    return {"total_assets": len(ASSETS), "total_value": total_value,
            "available": available, "maintenance": maintenance}


def schedule_meetings() -> dict:
    print(f"\n📅 Admin Agent — Meeting Schedule")
    print("─" * 45)

    for m in MEETINGS:
        print(f"  📅 {m['date']} {m['time']} | {m['title']:35s} | {m['duration']} min")
        print(f"     Attendees: {', '.join(m['attendees'])}")

    # Generate MoM template for next meeting
    next_meeting = MEETINGS[0]
    prompt = f"""
Generate a Meeting Minutes (MoM) template for:
Title    : {next_meeting['title']}
Date     : {next_meeting['date']}
Attendees: {', '.join(next_meeting['attendees'])}

Reply as JSON only:
{{
  "agenda": ["item1", "item2", "item3"],
  "action_items": [{{"task": "...", "owner": "...", "deadline": "..."}}],
  "next_meeting": "..."
}}
"""
    response = llm.invoke(prompt)
    raw   = response.content.strip().replace("```json","").replace("```","").strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    try:
        mom = json.loads(match.group()) if match else {}
    except:
        mom = {}

    print(f"\n  📝 MoM Template for '{next_meeting['title']}':")
    for i, item in enumerate(mom.get("agenda", []), 1):
        print(f"     {i}. {item}")

    return {"meetings": MEETINGS, "next_meeting": next_meeting, "mom_template": mom}


def run_admin_agent(action: str, **kwargs) -> AgentState:
    state = new_state(task=f"Admin:{action}", agent="admin", priority="low")

    if action == "assets":
        result = manage_assets()
    elif action == "meetings":
        result = schedule_meetings()
    else:
        result = {"error": f"Unknown action: {action}"}

    state["result"]     = result
    state["updated_at"] = datetime.now().isoformat()
    return state
