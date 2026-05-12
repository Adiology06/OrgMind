"""
Shared company state — updated by agents as they work.
KPI dashboard reads from here.
"""
from datetime import datetime

STATE = {
    "revenue":             {"current": 0,       "target": 500000, "unit": "INR"},
    "leads":               {"current": 5,        "target": 20,     "unit": "count"},
    "open_tickets":        {"current": 5,        "target": 2,      "unit": "count"},
    "budget_used_pct":     {"current": 37.4,     "target": 60,     "unit": "percent"},
    "employee_attendance": {"current": 84.6,     "target": 95,     "unit": "percent"},
    "active_contracts":    {"current": 2,        "target": 5,      "unit": "count"},
    "bugs_open":           {"current": 5,        "target": 0,      "unit": "count"},
    "campaigns_active":    {"current": 1,        "target": 3,      "unit": "count"},
    "candidates_hired":    {"current": 0,        "target": 10,      "unit": "count"},
    "invoices_generated":  {"current": 0,        "target": 10,     "unit": "count"},
    "expenses_approved":   {"current": 0,        "target": 20,     "unit": "count"},
}

ACTIVITY_LOG = []  # human-readable activity feed
ACTIVE_PROJECT = None


def update_kpi(key: str, value, reason: str = ""):
    if key in STATE:
        old = STATE[key]["current"]
        STATE[key]["current"] = value
        log_activity(f"KPI updated: {key} changed from {old} to {value}. {reason}")


def increment_kpi(key: str, by: int = 1):
    if key in STATE:
        STATE[key]["current"] = round(STATE[key]["current"] + by, 2)


def log_activity(message: str, agent: str = "system", category: str = "info"):
    ACTIVITY_LOG.append({
        "message":   message,
        "agent":     agent,
        "category":  category,
        "timestamp": datetime.now().isoformat(),
        "time":      datetime.now().strftime("%I:%M %p"),
    })
    # keep last 100 entries
    if len(ACTIVITY_LOG) > 100:
        ACTIVITY_LOG.pop(0)


def set_active_project(project: dict):
    global ACTIVE_PROJECT
    ACTIVE_PROJECT = {**project, "started_at": datetime.now().isoformat()}
    log_activity(
        f"New project started: {project.get('name','?')} "
        f"for {project.get('client','?')} "
        f"worth ₹{project.get('value',0):,}",
        agent="CEO",
        category="project"
    )

def on_project_complete(project_value: int, project_name: str):
    update_kpi("revenue", STATE["revenue"]["current"] + project_value,
               f"Project completed: {project_name}")
    increment_kpi("active_contracts", 1)
    log_activity(
        f"Revenue updated: +₹{project_value:,} from {project_name}",
        agent="analytics", category="finance"
    )

def mark_completed(project_name: str):
    try:
        from agents.project_flow import get_projects
        from state.project_status import set_status
        projects = get_projects()
        proj     = next((p for p in projects
                         if p["project_name"] == project_name), {})
        net_rev  = proj.get("net_revenue", 0)
        if net_rev:
            update_kpi(
                "revenue",
                STATE["revenue"]["current"] + net_rev,
                f"Project completed: {project_name} net ₹{net_rev:,}"
            )
            increment_kpi("active_contracts", 1)
        set_status(project_name, "completed",
                   f"All approvals done. {datetime.now().strftime('%d %b %Y %I:%M %p')}")
        # update project log status
        try:
            from agents.project_flow import PROJECT_LOG, _save_projects
            for p in PROJECT_LOG:
                if p["project_name"] == project_name:
                    p["status"] = "completed"
                    break
            _save_projects()
        except:
            pass
        # send completion WhatsApp
        try:
            from tools.notifier import notify_ceo
            notify_ceo(
                message=(
                    f"🎉 PROJECT COMPLETED!\n\n"
                    f"Project  : {project_name}\n"
                    f"Client   : {proj.get('client','')}\n"
                    f"Value    : ₹{proj.get('value',0):,}\n"
                    f"Net Rev  : ₹{net_rev:,}\n\n"
                    f"All approvals received.\n"
                    f"{datetime.now().strftime('%d %b %Y %I:%M %p')}"
                ),
                priority="normal"
            )
        except:
            pass
    except Exception as e:
        print(f"  ⚠️  mark_completed error: {e}")

def get_state():
    return STATE


def get_activity_log():
    return list(reversed(ACTIVITY_LOG))


def get_active_project():
    return ACTIVE_PROJECT
# Recalculate revenue based on all completed project net revenues.
def recalculate_revenue_from_projects():
    """Recalculate revenue based on all completed project net revenues."""
    try:
        from agents.project_flow import get_projects
        projects       = get_projects()
        base_revenue   = 500000  # base company revenue
        project_revenue = sum(
            p.get("net_revenue", 0)
            for p in projects
            if p.get("status") in ("completed","active","pending")
        )
        STATE["revenue"]["current"] = base_revenue + project_revenue
    except:
        pass