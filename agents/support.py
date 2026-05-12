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

TICKETS = [
    {"id": "TK001", "customer": "Rahul Das",    "issue": "Cannot login to dashboard after password reset",         "priority": "high",   "status": "open",   "created": "2026-04-30"},
    {"id": "TK002", "customer": "Anjali Singh",  "issue": "Invoice PDF not generating for INV003",                  "priority": "medium", "status": "open",   "created": "2026-04-29"},
    {"id": "TK003", "customer": "Karan Patel",   "issue": "Refund request for duplicate payment of ₹48,000",       "priority": "high",   "status": "open",   "created": "2026-04-28"},
    {"id": "TK004", "customer": "Pooja Sharma",  "issue": "WhatsApp notifications not being received",              "priority": "low",    "status": "open",   "created": "2026-04-30"},
    {"id": "TK005", "customer": "Dev Malhotra",  "issue": "Feature request: bulk CSV import for leads",             "priority": "low",    "status": "open",   "created": "2026-04-27"},
]


def triage_tickets() -> dict:
    print(f"\n🎫 Support Agent — Ticket Triage")
    print("─" * 45)

    triaged = []
    for t in TICKETS:
        prompt = f"""
Support ticket:
Customer: {t['customer']}
Issue   : {t['issue']}
Priority: {t['priority']}

Give:
1. Category (billing/technical/feature/account)
2. Suggested resolution in 1 sentence
3. Estimated time to resolve (e.g. "2 hours")

Reply as JSON only:
{{"category": "...", "resolution": "...", "eta": "..."}}
"""
        response = llm.invoke(prompt)
        raw   = response.content.strip().replace("```json","").replace("```","").strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        try:
            ai = json.loads(match.group()) if match else {}
        except:
            ai = {}

        triaged.append({**t, "category": ai.get("category",""),
                        "resolution": ai.get("resolution",""), "eta": ai.get("eta","")})
        flag = "🔴" if t["priority"] == "high" else "🟡" if t["priority"] == "medium" else "🟢"
        print(f"  {flag} {t['id']} | {t['customer']:14s} | {ai.get('category',''):10s} | ETA: {ai.get('eta','')}")
        print(f"       → {ai.get('resolution','')[:70]}")

    high_priority = [t for t in triaged if t["priority"] == "high"]
    return {"total": len(TICKETS), "triaged": triaged, "high_priority": high_priority}


def process_refund(ticket_id: str) -> dict:
    ticket = next((t for t in TICKETS if t["id"] == ticket_id), None)
    if not ticket:
        return {"error": "Ticket not found"}

    print(f"\n💰 Support Agent — Processing Refund: {ticket_id}")
    print("─" * 45)
    print(f"  Customer : {ticket['customer']}")
    print(f"  Issue    : {ticket['issue']}")

    prompt = f"""
Refund request:
Customer: {ticket['customer']}
Issue   : {ticket['issue']}
Write a professional refund approval message (2 sentences).
Reply with just the message.
"""
    response = llm.invoke(prompt)
    message  = response.content.strip()
    print(f"  📧 Message: {message[:100]}...")

    return {"ticket_id": ticket_id, "customer": ticket["customer"],
            "refund_message": message, "status": "approved_pending_ceo"}


def chatbot_response(customer_query: str) -> dict:
    print(f"\n🤖 Support Chatbot — Query: {customer_query[:50]}")
    print("─" * 45)

    prompt = f"""
You are OrgMind's customer support AI.
Customer query: {customer_query}
Product: OrgMind — AI business operating system for SMEs

Reply helpfully in 2-3 sentences. Be friendly and professional.
"""
    response = llm.invoke(prompt)
    reply    = response.content.strip()
    print(f"  🤖 Bot: {reply[:100]}...")

    return {"query": customer_query, "response": reply,
            "timestamp": datetime.now().isoformat()}


def run_support_agent(action: str, **kwargs) -> AgentState:
    state = new_state(task=f"Support:{action}", agent="support", priority="medium")

    if action == "triage":
        result = triage_tickets()
        high   = result.get("high_priority", [])
        if high:
            state["needs_ceo_approval"] = True
            state["task"] = f"Support: {len(high)} HIGH priority tickets need attention — including refund of ₹48,000"
            if should_escalate(state):
                state = ceo_review(state)

    elif action == "refund":
        result = process_refund(ticket_id=kwargs.get("ticket_id", "TK003"))
        state["needs_ceo_approval"] = True
        state["task"] = f"Support: Refund request from {result.get('customer','')} needs CEO approval"
        if should_escalate(state):
            state = ceo_review(state)

    elif action == "chatbot":
        result = chatbot_response(customer_query=kwargs.get("query", "How do I reset my password?"))

    else:
        result = {"error": f"Unknown action: {action}"}

    state["result"]     = result
    state["updated_at"] = datetime.now().isoformat()
    return state