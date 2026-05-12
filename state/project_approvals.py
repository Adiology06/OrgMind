import json, os
from datetime import datetime

FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'project_approvals.json')

# pending human approvals per project
PROJECT_APPROVALS = {}

def _load():
    global PROJECT_APPROVALS
    try:
        if os.path.exists(FILE):
            with open(FILE) as f:
                PROJECT_APPROVALS = json.load(f)
    except:
        PROJECT_APPROVALS = {}

def _save():
    try:
        with open(FILE, 'w') as f:
            json.dump(PROJECT_APPROVALS, f, indent=2, default=str)
    except:
        pass

_load()

def set_pending_candidates(project_id: str, candidates: list):
    if project_id not in PROJECT_APPROVALS:
        PROJECT_APPROVALS[project_id] = {}
    PROJECT_APPROVALS[project_id]["candidates"]          = candidates
    PROJECT_APPROVALS[project_id]["selected_candidate"]  = None
    PROJECT_APPROVALS[project_id]["candidate_status"]    = "pending_ceo"
    PROJECT_APPROVALS[project_id]["updated_at"]          = datetime.now().isoformat()
    _save()

def set_pending_investors(project_id: str, investors: list):
    if project_id not in PROJECT_APPROVALS:
        PROJECT_APPROVALS[project_id] = {}
    PROJECT_APPROVALS[project_id]["investors"]           = investors
    PROJECT_APPROVALS[project_id]["selected_investor"]   = None
    PROJECT_APPROVALS[project_id]["investor_status"]     = "pending_ceo"
    PROJECT_APPROVALS[project_id]["updated_at"]          = datetime.now().isoformat()
    _save()

def ceo_select_candidate(project_id: str, candidate_index: int) -> dict:
    if project_id not in PROJECT_APPROVALS:
        return {"error": "Project not found"}
    candidates = PROJECT_APPROVALS[project_id].get("candidates", [])
    if candidate_index >= len(candidates):
        return {"error": "Invalid index"}
    selected = candidates[candidate_index]

    # support multiple selections — store as list
    existing = PROJECT_APPROVALS[project_id].get("selected_candidate")
    if existing:
        if isinstance(existing, list):
            # add if not already in list
            if not any(c.get("name") == selected.get("name") for c in existing):
                existing.append(selected)
            PROJECT_APPROVALS[project_id]["selected_candidate"] = existing
        else:
            # convert to list
            if existing.get("name") != selected.get("name"):
                PROJECT_APPROVALS[project_id]["selected_candidate"] = [existing, selected]
    else:
        PROJECT_APPROVALS[project_id]["selected_candidate"] = selected

    PROJECT_APPROVALS[project_id]["candidate_status"] = "approved"
    PROJECT_APPROVALS[project_id]["updated_at"]        = datetime.now().isoformat()
    _save()
    return selected

def ceo_select_investor(project_id: str, investor_index: int) -> dict:
    if project_id not in PROJECT_APPROVALS:
        return {"error": "Project not found"}
    investors = PROJECT_APPROVALS[project_id].get("investors", [])
    if investor_index >= len(investors):
        return {"error": "Invalid index"}
    selected = investors[investor_index]
    PROJECT_APPROVALS[project_id]["selected_investor"] = selected
    PROJECT_APPROVALS[project_id]["investor_status"]   = "approved"
    PROJECT_APPROVALS[project_id]["updated_at"]        = datetime.now().isoformat()
    _save()
    return selected

def get_project_approval(project_id: str) -> dict:
    return PROJECT_APPROVALS.get(project_id, {})

def final_approve_project(project_id: str) -> dict:
    if project_id not in PROJECT_APPROVALS:
        return {"error": "Not found"}
    PROJECT_APPROVALS[project_id]["final_status"]  = "approved"
    PROJECT_APPROVALS[project_id]["approved_at"]   = datetime.now().isoformat()
    _save()
    return PROJECT_APPROVALS[project_id]

def get_all_project_approvals() -> dict:
    return PROJECT_APPROVALS