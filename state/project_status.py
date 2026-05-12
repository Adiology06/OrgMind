import json, os
from datetime import datetime

STATUS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'project_status.json')
PROJECT_STATUS = {}

def _load():
    global PROJECT_STATUS
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE) as f:
                PROJECT_STATUS = json.load(f)
    except:
        PROJECT_STATUS = {}

def _save():
    try:
        with open(STATUS_FILE, 'w') as f:
            json.dump(PROJECT_STATUS, f, indent=2, default=str)
    except:
        pass

_load()

def set_status(project_name: str, status: str, notes: str = ""):
    PROJECT_STATUS[project_name] = {
        "status":     status,
        "updated_at": datetime.now().isoformat(),
        "notes":      notes,
    }
    _save()
    print(f"\n  📊 Project status: {project_name} → {status.upper()}")

def get_status(project_name: str) -> str:
    return PROJECT_STATUS.get(project_name, {}).get("status", "pending")

def get_all_statuses() -> dict:
    return PROJECT_STATUS

def mark_completed(project_name: str):
    set_status(project_name, "completed",
               f"All approvals done. Completed: {datetime.now().strftime('%d %b %Y %I:%M %p')}")

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

    # send completion WhatsApp ONLY now — not on final approve
    try:
        from agents.project_flow import PROJECT_LOG
        proj = next((p for p in PROJECT_LOG
                     if p["project_name"]==project_name), {})
        value       = proj.get("value", 0)
        net_revenue = proj.get("net_revenue", 0)
        candidates  = proj.get("selected_candidates",[])
        investor    = proj.get("selected_investor")

        from tools.notifier import notify_ceo
        notify_ceo(
            message=(
                f"🎉 PROJECT COMPLETED!\n\n"
                f"Project  : {project_name}\n"
                f"Client   : {proj.get('client','')}\n"
                f"Value    : ₹{value:,}\n"
                f"Net Rev  : ₹{net_revenue:,}\n"
                f"Team     : {', '.join([c.get('name','') for c in candidates]) or 'TBD'}\n"
                f"Investor : {investor.get('company','Self-funded') if investor else 'Self-funded'}\n\n"
                f"All {proj.get('approvals_generated',0)} approvals received.\n"
                f"Time     : {datetime.now().strftime('%d %b %Y %I:%M %p')}"
            ),
            priority="normal"
        )
    except:
        pass