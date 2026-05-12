from datetime import datetime
import uuid, json, os

LOG_FILE      = os.path.join(os.path.dirname(__file__), '..', 'data', 'approvals_log.json')
REJECTED_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'rejected_approvals.json')

PENDING_APPROVALS   = {}
COMPLETED_APPROVALS = {}
REJECTED_APPROVALS  = {}  # rejected — can be resubmitted with modifications


def _load_from_disk():
    global COMPLETED_APPROVALS, REJECTED_APPROVALS
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE) as f:
                data = json.load(f)
            for entry in data:
                if entry.get("status") == "decided":
                    COMPLETED_APPROVALS[entry["approval_id"]] = entry
    except:
        pass
    try:
        if os.path.exists(REJECTED_FILE):
            with open(REJECTED_FILE) as f:
                REJECTED_APPROVALS = json.load(f)
    except:
        pass


def _save_to_disk():
    try:
        with open(LOG_FILE, 'w') as f:
            json.dump(list(COMPLETED_APPROVALS.values()), f, indent=2, default=str)
    except:
        pass
    try:
        with open(REJECTED_FILE, 'w') as f:
            json.dump(REJECTED_APPROVALS, f, indent=2, default=str)
    except:
        pass


_load_from_disk()


def request_approval(agent: str, task: str, details: dict,
                     priority: str = "medium",
                     project_name: str = "",
                     max_per_project: int = 6) -> str:

    # check pending duplicates
    for aid, ap in PENDING_APPROVALS.items():
        if ap["agent"] == agent and ap["task"][:50] == task[:50]:
            print(f"\n  ⏭️  DUPLICATE SKIPPED: [{aid}] pending")
            return aid

    # check recently completed (10 min window)
    now = datetime.now()
    for aid, ap in COMPLETED_APPROVALS.items():
        if ap["agent"] == agent and ap["task"][:50] == task[:50]:
            try:
                diff = (now - datetime.fromisoformat(ap.get("decided_at",""))).total_seconds()
                if diff < 600:
                    print(f"\n  ⏭️  RECENTLY DECIDED: [{aid}]")
                    return aid
            except:
                pass

    # enforce max approvals per project
    if project_name:
        proj_pending = [a for a in PENDING_APPROVALS.values()
                        if a.get("project_name") == project_name]
        if len(proj_pending) >= max_per_project:
            print(f"\n  ⚠️  MAX APPROVALS REACHED for {project_name} — skipping")
            return ""

    approval_id = str(uuid.uuid4())[:8].upper()
    entry = {
        "approval_id":    approval_id,
        "agent":          agent,
        "task":           task,
        "details":        details,
        "priority":       priority,
        "project_name":   project_name,
        "status":         "pending",
        "requested_at":   datetime.now().isoformat(),
        "decided_at":     None,
        "decision":       None,
        "notes":          "",
        "resubmission":   False,
    }
    PENDING_APPROVALS[approval_id] = entry
    print(f"\n  📥 QUEUED [{approval_id}] {agent.upper()}: {task[:55]}")
    return approval_id


def ceo_decide(approval_id: str, decision: str, notes: str = "") -> dict:
    if approval_id not in PENDING_APPROVALS:
        if approval_id in COMPLETED_APPROVALS:
            return {"error": "Already decided",
                    "decision": COMPLETED_APPROVALS[approval_id]["decision"]}
        return {"error": "Not found"}

    item = PENDING_APPROVALS.pop(approval_id)
    item.update({
        "status":     "decided",
        "decision":   decision,
        "notes":      notes,
        "decided_at": datetime.now().isoformat(),
    })

    if decision == "reject":
        # store in rejected so CEO can resubmit with modification
        REJECTED_APPROVALS[approval_id] = item
        print(f"\n  ❌ REJECTED [{approval_id}] — can be resubmitted")
    else:
        COMPLETED_APPROVALS[approval_id] = item

    _save_to_disk()
    print(f"\n  ✅ CEO DECISION [{approval_id}] → {decision.upper()}")
    if notes:
        print(f"     Notes: {notes}")
    return item


def resubmit_rejected(approval_id: str, modified_task: str = "",
                       modified_cost: str = "") -> str:
    """CEO resubmits a rejected approval with modifications."""
    if approval_id not in REJECTED_APPROVALS:
        return ""
    original = REJECTED_APPROVALS.pop(approval_id)
    task     = modified_task or original["task"]

    new_id = request_approval(
        agent        = original["agent"],
        task         = task,
        details      = {**original.get("details",{}),
                        "modified_cost": modified_cost,
                        "original_id":   approval_id,
                        "resubmitted":   True},
        priority     = original["priority"],
        project_name = original.get("project_name",""),
    )
    if new_id:
        PENDING_APPROVALS[new_id]["resubmission"] = True
    _save_to_disk()
    return new_id

def get_decision(approval_id: str) -> dict:
    if approval_id in COMPLETED_APPROVALS:
        return COMPLETED_APPROVALS[approval_id]
    if approval_id in PENDING_APPROVALS:
        return PENDING_APPROVALS[approval_id]
    if approval_id in REJECTED_APPROVALS:
        return REJECTED_APPROVALS[approval_id]
    return {"status": "not_found"}

def get_rejected() -> list:
    return list(REJECTED_APPROVALS.values())


def get_all_pending() -> list:
    return list(PENDING_APPROVALS.values())


def get_all_completed() -> list:
    return list(COMPLETED_APPROVALS.values())


def get_all_approvals() -> list:
    pending   = sorted(PENDING_APPROVALS.values(),
                       key=lambda x: x["requested_at"], reverse=True)
    completed = sorted(COMPLETED_APPROVALS.values(),
                       key=lambda x: x.get("decided_at") or "", reverse=True)
    rejected  = sorted(REJECTED_APPROVALS.values(),
                       key=lambda x: x.get("decided_at") or "", reverse=True)
    return list(pending) + list(rejected) + list(completed)