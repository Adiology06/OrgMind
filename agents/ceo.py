from langchain_groq import ChatGroq
from agents.approval_queue import request_approval, get_decision
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)

APPROVAL_RULES = {
    "finance":    {"auto_approve_below": 5000},
    "hr":         {"always_ask": True},
    "legal":      {"always_ask": True},
    "operations": {"auto_approve_below": 10000},
    "marketing":  {"auto_approve_below": 2000},
    "sales":      {"auto_approve_below": 50000},
    "it_dev":     {"always_ask": False},
    "support":    {"always_ask": False},
    "procurement":{"auto_approve_below": 15000},
    "admin":      {"auto_approve_below": 3000},
    "analytics":  {"always_ask": False},
}


def should_escalate(state: dict) -> bool:
    if state.get("ceo_decision"):
        return False
    if state.get("is_emergency") or state.get("priority") == "critical":
        return True
    rules = APPROVAL_RULES.get(state.get("current_agent",""), {})
    if rules.get("always_ask"):
        return True
    return state.get("needs_ceo_approval", False)


def ceo_review(state: dict) -> dict:
    """Queue approval request — no blocking, no input()."""
    try:
        summary = llm.invoke(
            f"Summarize in 1 sentence for CEO approval: {state.get('task','')}"
        ).content.strip()
    except:
        summary = state.get("task", "")

    approval_id = request_approval(
        agent    = state.get("current_agent", "unknown"),
        task     = state.get("task", ""),
        details  = {"summary": summary, "priority": state.get("priority","medium")},
        priority = state.get("priority", "medium"),
    )

    # notify CEO via WhatsApp if configured
    try:
        from tools.notifier import notify_ceo
        notify_ceo(
            message  = f"[{approval_id}] {state.get('task','')[:80]}",
            priority = state.get("priority", "medium"),
        )
    except:
        pass

    return {
        **state,
        "ceo_decision":  "pending",
        "approval_id":   approval_id,
        "updated_at":    datetime.now().isoformat(),
    }


def get_approval_history() -> list:
    from agents.approval_queue import get_all_approvals
    return get_all_approvals()


def emergency_broadcast(state: dict) -> dict:
    return ceo_review({**state, "priority": "critical"})