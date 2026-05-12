from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime
import csv, os
from agents.it_coder   import run_it_coder
from agents.legal      import check_law_compliance
from fastapi import FastAPI, Request
from state.company_state import get_activity_log, get_active_project, set_active_project
from tools.sheets import read_sheet_raw, sync_resumes, sync_leads, sync_projects

load_dotenv()

app = FastAPI(title="OrgMind", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    #allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Agent imports ───────────────────────────────────────────────────
from agents.hr         import run_hr_agent
from agents.finance    import run_finance_agent
from agents.sales      import run_sales_agent
from agents.marketing  import run_marketing_agent
from agents.legal      import run_legal_agent
from agents.operations import run_operations_agent
from agents.support    import run_support_agent
from agents.it_dev     import run_it_agent
from agents.analytics  import run_analytics_agent
from agents.admin      import run_admin_agent
from agents.ceo        import get_approval_history

# ════════════════════════════════════════════════════════════════════
#  HEALTH
# ════════════════════════════════════════════════════════════════════
@app.get("/")
def root():
    return {"status": "OrgMind is running", "mode": "CEO controlled", "agents": 10}

@app.get("/health")
def health():
    return {
        "groq":   bool(os.getenv("GROQ_API_KEY")),
        "twilio": bool(os.getenv("TWILIO_SID")),
        "status": "ok",
        "time":   datetime.now().isoformat(),
    }

# ════════════════════════════════════════════════════════════════════
#  CEO DASHBOARD APIs
# ════════════════════════════════════════════════════════════════════
@app.get("/ceo/approvals")
def ceo_approvals():
    return {"approvals": get_approval_history()}

@app.get("/ceo/overview")
def ceo_overview():
    """Full company snapshot for CEO dashboard."""
    kpi     = run_analytics_agent(action="kpi")["result"]
    anomaly = run_analytics_agent(action="anomaly")["result"]
    return {
        "company":    "OrgMind",
        "timestamp":  datetime.now().isoformat(),
        "kpis":       kpi,
        "anomalies":  anomaly,
        "approvals_pending": len([a for a in get_approval_history() if a.get("decision") == "approve"]),
    }

# ════════════════════════════════════════════════════════════════════
#  HR
# ════════════════════════════════════════════════════════════════════
@app.get("/hr/screen")
def hr_screen_by_role(role: str = "ML Engineer"):
    try:
        from agents.hr import screen_resumes
        role_skill_map = {
            "ml/ai engineer":        ["python","ml","ai","langchain"],
            "frontend developer":    ["react","javascript","typescript"],
            "backend developer":     ["python","nodejs","java","api"],
            "app developer":         ["flutter","android","ios","mobile"],
            "data analyst":          ["python","sql","tableau","analytics"],
            "devops engineer":       ["aws","docker","kubernetes","linux"],
            "marketing executive":   ["marketing","seo","social media","ads"],
            "video editor":          ["premiere","after effects","editing"],
            "legal counsel":         ["law","compliance","contracts"],
            "finance analyst":       ["finance","accounting","excel","gst"],
            "hr executive":          ["recruitment","hr","payroll"],
            "content creator":       ["writing","content","social media"],
        }
        skills = role_skill_map.get(role.lower(), role.lower().split()[:3])
        result = screen_resumes(job_role=role, required_skills=skills)
        return result
    except Exception as e:
        return {"candidates": [], "error": str(e), "job_role": role}

@app.get("/hr/schedule")
def hr_schedule():
    return run_hr_agent(action="schedule", candidate_name="Arjun Sharma", job_role="ML Engineer")["result"]

@app.get("/hr/payroll/{employee_id}")
def hr_payroll(employee_id: str = "E001"):
    return run_hr_agent(action="payroll", employee_id=employee_id)["result"]

@app.get("/hr/performance")
def hr_performance():
    return run_hr_agent(action="performance",
        employee_name="Rahul Das",
        metrics={"tasks_completed": 45, "on_time_delivery": "89%", "peer_rating": 4.2})["result"]

# ════════════════════════════════════════════════════════════════════
#  FINANCE
# ════════════════════════════════════════════════════════════════════
@app.get("/finance/expenses")
def finance_expenses():
    return run_finance_agent(action="expenses", threshold=5000)["result"]

@app.get("/finance/invoice/{invoice_id}")
def finance_invoice(invoice_id: str = "INV001"):
    return run_finance_agent(action="invoice", invoice_id=invoice_id)["result"]

@app.get("/finance/budget")
def finance_budget():
    return run_finance_agent(action="budget")["result"]

@app.get("/finance/cashflow")
def finance_cashflow():
    return run_finance_agent(action="cashflow")["result"]

# ════════════════════════════════════════════════════════════════════
#  SALES
# ════════════════════════════════════════════════════════════════════
@app.get("/sales/score")
def sales_score():
    return run_sales_agent(action="score")["result"]

@app.get("/sales/proposal/{lead_id}")
def sales_proposal(lead_id: str = "L001"):
    return run_sales_agent(action="proposal", lead_id=lead_id)["result"]

@app.get("/sales/forecast")
def sales_forecast():
    return run_sales_agent(action="forecast")["result"]

@app.get("/sales/followup")
def sales_followup():
    return run_sales_agent(action="followup")["result"]

# ════════════════════════════════════════════════════════════════════
#  MARKETING
# ════════════════════════════════════════════════════════════════════
@app.get("/marketing/campaign/{campaign_id}")
def marketing_campaign(campaign_id: str = "C001"):
    return run_marketing_agent(action="campaign", campaign_id=campaign_id)["result"]

@app.get("/marketing/whatsapp/{campaign_id}")
def marketing_whatsapp(campaign_id: str = "C001"):
    return run_marketing_agent(action="whatsapp", campaign_id=campaign_id)["result"]

@app.get("/marketing/adperformance")
def marketing_ads():
    return run_marketing_agent(action="adperformance")["result"]

@app.get("/marketing/social")
def marketing_social():
    return run_marketing_agent(action="social", platform="LinkedIn", topic="AI automation for SMEs 2026")["result"]

# ════════════════════════════════════════════════════════════════════
#  LEGAL
# ════════════════════════════════════════════════════════════════════
@app.get("/legal/contracts")
def legal_contracts():
    return run_legal_agent(action="contracts")["result"]

@app.get("/legal/compliance")
def legal_compliance():
    return run_legal_agent(action="compliance")["result"]

@app.get("/legal/policy")
def legal_policy():
    return run_legal_agent(action="policy", policy_type="Data Privacy")["result"]


# ── IT Code Fixer ────────────────────────────────────────────────────
@app.post("/it/fix-code")
async def fix_code_endpoint(request: Request):
    body = await request.json()
    result = run_it_coder(
        action="fix",
        code=body.get("code",""),
        filename=body.get("filename","code.py"),
        language=body.get("language","python"),
    )
    return result["result"]

@app.post("/it/review-code")
async def review_code_endpoint(request: Request):
    body = await request.json()
    result = run_it_coder(
        action="review",
        code=body.get("code",""),
        filename=body.get("filename","code.py"),
        language=body.get("language","python"),
    )
    return result["result"]

# ── Law Engine ───────────────────────────────────────────────────────
@app.get("/legal/lawcheck")
def law_check(situation: str = "employee termination after 2 years"):
    return check_law_compliance(situation=situation)

# ════════════════════════════════════════════════════════════════════
#  OPERATIONS
# ════════════════════════════════════════════════════════════════════
@app.get("/ops/inventory")
def ops_inventory():
    return run_operations_agent(action="inventory")["result"]

@app.get("/ops/tasks")
def ops_tasks():
    return run_operations_agent(action="tasks")["result"]

@app.get("/ops/vendors")
def ops_vendors():
    return run_operations_agent(action="vendors")["result"]

# ════════════════════════════════════════════════════════════════════
#  SUPPORT
# ════════════════════════════════════════════════════════════════════
@app.get("/support/triage")
def support_triage():
    return run_support_agent(action="triage")["result"]

@app.get("/support/refund/{ticket_id}")
def support_refund(ticket_id: str = "TK003"):
    return run_support_agent(action="refund", ticket_id=ticket_id)["result"]

@app.get("/support/chatbot")
def support_chatbot(query: str = "How do I export my report?"):
    return run_support_agent(action="chatbot", query=query)["result"]

# ════════════════════════════════════════════════════════════════════
#  IT / DEV
# ════════════════════════════════════════════════════════════════════
@app.get("/it/bugs")
def it_bugs():
    return run_it_agent(action="bugs")["result"]

@app.get("/it/security")
def it_security():
    return run_it_agent(action="security")["result"]

@app.get("/it/roadmap")
def it_roadmap():
    return run_it_agent(action="roadmap")["result"]

# ════════════════════════════════════════════════════════════════════
#  ANALYTICS
# ════════════════════════════════════════════════════════════════════
@app.get("/analytics/kpi")
def analytics_kpi():
    return run_analytics_agent(action="kpi")["result"]

@app.get("/analytics/summary")
def analytics_summary():
    return run_analytics_agent(action="summary")["result"]

@app.get("/analytics/anomaly")
def analytics_anomaly():
    return run_analytics_agent(action="anomaly")["result"]

# ════════════════════════════════════════════════════════════════════
#  ADMIN
# ════════════════════════════════════════════════════════════════════
@app.get("/admin/assets")
def admin_assets():
    return run_admin_agent(action="assets")["result"]

@app.get("/admin/meetings")
def admin_meetings():
    return run_admin_agent(action="meetings")["result"]

# Project flow and CEO dashboard are in separate files, see agents/project_flow.py and agents/ceo.py
from agents.project_flow import start_new_project, get_projects

@app.post("/ceo/new-project")
async def new_project(request: Request):
    body = await request.json()
    result = start_new_project(
        project_name        = body.get("project_name",""),
        client              = body.get("client",""),
        value               = int(body.get("value",0)),
        lead_id             = body.get("lead_id",""),
        roles_needed        = body.get("roles_needed",""),
        selected_candidates = body.get("selected_candidates",[]),
        project_type        = body.get("project_type",""),
    )
    return result


@app.get("/ceo/projects")
def list_ceo_projects():
    from agents.project_flow  import get_projects
    from state.project_status import get_all_statuses
    projects = get_projects()
    statuses = get_all_statuses()
    for p in projects:
        pname    = p["project_name"]
        status   = statuses.get(pname, {})
        p["status"]     = status.get("status", "pending")
        p["status_note"] = status.get("notes","")
    return {"projects": projects}

from agents.chatbot  import chat, get_chat_history, clear_history
from tools.notifier  import send_whatsapp, send_email, notify_ceo
from fastapi         import FastAPI, Request

@app.post("/chat")
async def chatbot_endpoint(request: Request):
    body       = await request.json()
    query      = body.get("query", "")
    session_id = body.get("session_id", "default")
    return chat(query=query, session_id=session_id)

@app.get("/chat/history")
def chat_history(session_id: str = "default"):
    return {"history": get_chat_history(session_id)}

@app.post("/chat/clear")
async def chat_clear(request: Request):
    body = await request.json()
    clear_history(body.get("session_id", "default"))
    return {"status": "cleared"}

@app.post("/notify/whatsapp")
async def notify_whatsapp(request: Request):
    body = await request.json()
    return send_whatsapp(
        to_number=body.get("to", os.getenv("YOUR_WHATSAPP_NUMBER","")),
        message=body.get("message","Test from OrgMind")
    )

@app.post("/notify/ceo")
async def notify_ceo_endpoint(request: Request):
    body = await request.json()
    return notify_ceo(
        message=body.get("message",""),
        priority=body.get("priority","normal")
    )
# CEO Dashboard - Approval Queue APIs
from agents.approval_queue import (
    get_all_pending, get_all_completed,
    ceo_decide, get_all_approvals
)

@app.get("/ceo/approvals/all")
def all_approvals():
    return {"approvals": get_all_approvals()}

@app.post("/ceo/approvals/decide")
async def decide_approval(request: Request):
    body = await request.json()
    result = ceo_decide(
        approval_id = body.get("approval_id",""),
        decision    = body.get("decision",""),
        notes       = body.get("notes",""),
    )

    # check if all pending approvals are now decided
    remaining = get_all_pending()
    if len(remaining) == 0:
        # check if any project is in pending/active status
        from state.project_status import get_all_statuses, mark_completed
        from agents.project_flow  import get_projects
        projects = get_projects()
        statuses = get_all_statuses()
        for proj in projects:
            pname  = proj["project_name"]
            status = statuses.get(pname, {}).get("status","pending")
            if status in ("pending", "active"):
                mark_completed(pname)

    return result
# Company state and activity feed APIs
@app.get("/state/activity")
def activity_feed():
    return {"activities": get_activity_log()}

@app.get("/state/project")
def active_project():
    return {"project": get_active_project()}
    
#Project listing API (with CSV loading and fallback)
@app.get("/projects/list")
def list_projects_csv():
    from agents.project_flow import get_projects
    launched_names = {
        (p["project_name"], p["client"])
        for p in get_projects()
    }

    projects  = []
    live_path = os.path.join("data", "projects_live.csv")
    csv_path  = os.path.join("data", "projects.csv") if not os.path.exists(live_path) else live_path

    fallback = [
        {"id":"P001","name":"Infosys AI Automation Platform",
         "client":"Infosys Ltd","value":"5000000","type":"AI/ML Development",
         "status":"available","roles":"ML/AI Engineer,Backend Developer,DevOps Engineer",
         "duration":"6-12 months","description":"Build agentic AI system for internal ops"},
        {"id":"P002","name":"Zomato Operations Management",
         "client":"Zomato","value":"1500000","type":"Full Business Automation",
         "status":"available","roles":"Frontend Developer,Backend Developer,Data Analyst",
         "duration":"3-6 months","description":"Automate delivery ops and analytics"},
        {"id":"P003","name":"HDFC Legal Compliance System",
         "client":"HDFC Bank","value":"6000000","type":"IT Consulting",
         "status":"available","roles":"Legal Counsel,Backend Developer,Data Analyst",
         "duration":"6-12 months","description":"AI-powered compliance and contract mgmt"},
        {"id":"P004","name":"PhonePe Analytics Dashboard",
         "client":"PhonePe","value":"2200000","type":"Data Analytics",
         "status":"available","roles":"Data Analyst,ML/AI Engineer,Frontend Developer",
         "duration":"3-6 months","description":"Business intelligence and KPI tracking"},
        {"id":"P005","name":"Urban Company Franchise OS",
         "client":"Urban Company","value":"800000","type":"Full Business Automation",
         "status":"available","roles":"Backend Developer,Frontend Developer,Marketing Executive",
         "duration":"1-3 months","description":"Full OrgMind deployment for franchise ops"},
    ]

    # load from CSV (live sheet takes priority)
    if os.path.exists(csv_path):
        try:
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("status","available") != "available":
                        continue
                    # normalize name field
                    row["name"] = row.get("name", row.get("project_name",""))
                    if row.get("name") and row.get("client"):
                        projects.append(row)
        except:
            pass

    if not projects:
        projects = fallback

    # mark launched ones
    result = []
    for p in projects:
        p["already_launched"] = (p["name"], p["client"]) in launched_names
        result.append(p)

    return {"projects": result}

# Data sync endpoints for Google Sheets integration (resumes, leads, projects)
@app.get("/sync/resumes")
def sync_resumes_endpoint():
    return sync_resumes()

@app.get("/sync/leads")
def sync_leads_endpoint():
    return sync_leads()

@app.get("/sync/projects")
def sync_projects_endpoint():
    return sync_projects()

@app.get("/sync/all")
def sync_all():
    return {
        "resumes":  sync_resumes(),
        "leads":    sync_leads(),
        "projects": sync_projects(),
    }
# Marketing broadcast endpoints  
@app.post("/notify/broadcast/whatsapp")
async def broadcast_whatsapp(request: Request):
    body = await request.json()
    from tools.notifier import marketing_broadcast_whatsapp
    return marketing_broadcast_whatsapp(
        numbers      = body.get("numbers", []),
        message      = body.get("message",""),
        campaign_name= body.get("campaign_name","")
    )

@app.post("/notify/broadcast/email")
async def broadcast_email(request: Request):
    body = await request.json()
    from tools.notifier import marketing_broadcast_email
    return marketing_broadcast_email(
        emails       = body.get("emails",[]),
        subject      = body.get("subject",""),
        body         = body.get("body",""),
        campaign_name= body.get("campaign_name","")
    )

@app.post("/notify/candidate")
async def notify_candidate(request: Request):
    body = await request.json()
    from tools.notifier import notify_candidate_shortlisted
    return notify_candidate_shortlisted(
        candidate         = body.get("candidate",{}),
        project_name      = body.get("project_name",""),
        interview_schedule= body.get("schedule",{})
    )

@app.post("/notify/investor")
async def notify_investor(request: Request):
    body = await request.json()
    from tools.notifier import notify_investor_selected
    return notify_investor_selected(
        investor = body.get("investor",{}),
        project  = body.get("project",{})
    )

@app.post("/notify/client")
async def notify_client(request: Request):
    body = await request.json()
    from tools.notifier import notify_client_project_started
    return notify_client_project_started(
        client_name  = body.get("client_name",""),
        client_email = body.get("client_email",""),
        client_phone = body.get("client_phone",""),
        project      = body.get("project",{})
    )

@app.get("/investors/top5")
def top_investors():
    from agents.sales import score_investors
    return score_investors()
# CEO Approval Queue APIs

from state.project_approvals import (
    get_project_approval, ceo_select_candidate,
    ceo_select_investor, final_approve_project,
    get_all_project_approvals
)

@app.get("/project/approval/{project_name}")
def get_proj_approval(project_name: str):
    return get_project_approval(project_name)

@app.get("/project/approvals/all")
def all_proj_approvals():
    return get_all_project_approvals()

@app.post("/project/select-candidate")
async def select_candidate(request: Request):
    body      = await request.json()
    proj      = body.get("project_name","")
    idx       = body.get("candidate_index", 0)
    candidate = ceo_select_candidate(proj, idx)
    
    # after selecting candidate, update KPI
    from state.company_state import increment_kpi
    increment_kpi("candidates_hired", 1)

    if candidate and not candidate.get("error"):
        from agents.hr import schedule_interview
        from tools.notifier import send_whatsapp, notify_ceo
        import os

        schedule = schedule_interview(
            candidate_name = candidate.get("name",""),
            job_role       = candidate.get("role","")
        )

        # For demo: send to CEO's number (since sandbox only has your number)
        # In production: send to candidate's actual number
        ceo_number = os.getenv("YOUR_WHATSAPP_NUMBER","")
        cand_phone = candidate.get("phone","")

        # try candidate's number first, fall back to CEO for demo
        send_to = f"whatsapp:+91{cand_phone}" if cand_phone and len(cand_phone)==10 \
                  else ceo_number

        sched = schedule.get("schedule", {})
        msg = (
            f"🎉 Congratulations {candidate.get('name','')}!\n\n"
            f"You are shortlisted for *{candidate.get('role','')}* at "
            f"*NexaCore Technologies Pvt Ltd*.\n\n"
            f"Project  : {proj}\n"
            f"Score    : {candidate.get('score',0)}/100\n\n"
            f"📅 Interview:\n"
            f"Date     : {sched.get('date','TBD')}\n"
            f"Time     : {sched.get('time','TBD')}\n"
            f"Mode     : {sched.get('mode','Google Meet')}\n\n"
            f"Our HR team will share meeting link shortly.\n"
            f"— NexaCore HR Team"
        )

        if send_to:
            send_whatsapp(send_to, msg)

        # always notify CEO
        notify_ceo(
            f"HR: {candidate.get('name','')} selected for {proj}. "
            f"Interview scheduled. WhatsApp sent.",
            priority="normal"
        )

    return {"selected": candidate, "status": "interview_scheduled"}


@app.post("/project/select-investor")
async def select_investor(request: Request):
    body     = await request.json()
    proj     = body.get("project_name","")
    idx      = body.get("investor_index", 0)
    investor = ceo_select_investor(proj, idx)

    if investor and not investor.get("error"):
        from tools.notifier import send_whatsapp, notify_ceo
        import os

        ceo_number  = os.getenv("YOUR_WHATSAPP_NUMBER","")
        inv_phone   = investor.get("phone","")
        send_to     = f"whatsapp:+91{inv_phone}" \
                      if inv_phone and len(str(inv_phone))==10 \
                      else ceo_number

        msg = (
            f"🤝 Investment Opportunity — NexaCore Technologies\n\n"
            f"Dear {investor.get('contact_name','')},\n\n"
            f"Your investment interest has been reviewed and selected "
            f"by our CEO for:\n\n"
            f"Project : {proj}\n"
            f"Amount  : ₹{investor.get('budget_inr',0):,}\n"
            f"Company : {investor.get('company','')}\n\n"
            f"Our team will contact you within 48 hours to discuss "
            f"terms and next steps.\n\n"
            f"— CEO Office\nNexaCore Technologies\n"
            f"📞 +91-9876543210"
        )

        if send_to:
            send_whatsapp(send_to, msg)

        notify_ceo(
            f"Sales: {investor.get('company','')} selected as investor for {proj}. "
            f"WhatsApp sent.",
            priority="normal"
        )

    return {"selected": investor, "status": "investor_notified"}

@app.post("/project/final-approve")
async def final_approve(request: Request):
    body   = await request.json()
    proj   = body.get("project_name","")
    result = final_approve_project(proj)

    from state.project_status import set_status
    set_status(proj, "active",
               "Final approval given by CEO. Project officially active.")

    from tools.notifier import notify_ceo
    notify_ceo(
        message=(
            f"✅ FINAL APPROVAL RECORDED\n\n"
            f"Project: {proj}\n"
            f"Status : ACTIVE\n\n"
            f"Candidate and investor confirmed.\n"
            f"Project is now officially running.\n"
            f"Approve remaining items in Approval Inbox to complete."
        ),
        priority="normal"
    )
    return result
# Debug endpoint to check sheet headers and data structure
@app.get("/debug/sheet/{sheet_type}")
def debug_sheet(sheet_type: str):
    from tools.sheets import read_sheet_raw
    ids = {
        "resumes":  os.getenv("RESUMES_SHEET_ID",""),
        "leads":    os.getenv("LEADS_SHEET_ID",""),
        "projects": os.getenv("PROJECTS_SHEET_ID",""),
    }
    sheet_id = ids.get(sheet_type,"")
    if not sheet_id:
        return {"error": f"No sheet ID for {sheet_type}"}
    rows = read_sheet_raw(sheet_id)
    if not rows:
        return {"error": "Could not read sheet or sheet is empty"}
    return {
        "total_rows":     len(rows),
        "headers":        list(rows[0].keys()),
        "first_row":      rows[0],
        "second_row":     rows[1] if len(rows)>1 else {},
    }
    
def debug_sheet_headers(sheet_id: str) -> dict:
        """Show exact column headers from sheet — for debugging."""
        rows = read_sheet_raw(sheet_id)
        if not rows:
            return {"error": "Could not read sheet"}
        return {
            "first_row_keys": list(rows[0].keys()),
            "sample_row":     rows[0],
            "total_rows":     len(rows)
        }
        
from agents.approval_queue import resubmit_rejected, get_rejected

@app.get("/ceo/approvals/rejected")
def get_rejected_approvals():
    return {"rejected": get_rejected()}

@app.post("/ceo/approvals/resubmit")
async def resubmit_approval(request: Request):
    body = await request.json()
    new_id = resubmit_rejected(
        approval_id    = body.get("approval_id",""),
        modified_task  = body.get("modified_task",""),
        modified_cost  = body.get("modified_cost",""),
    )
    return {"new_approval_id": new_id, "status": "resubmitted" if new_id else "failed"}

# Project report API for CEO dashboard drill-down
@app.get("/project/report/{project_name}")
def get_project_report(project_name: str):
    from agents.project_flow   import get_projects
    from agents.approval_queue import get_all_approvals
    from state.project_status  import get_status
    from state.company_state   import get_activity_log

    # single source of truth
    projects = get_projects()
    project  = next((p for p in projects
                     if p["project_name"]==project_name), None)
    if not project:
        return {"error": "Project not found"}

    # get approvals for this project
    all_approvals = get_all_approvals()
    proj_approvals = [a for a in all_approvals
                      if a.get("project_name")==project_name
                      or project_name.lower() in a.get("task","").lower()]

    activities = [a for a in get_activity_log()
                  if project_name.lower() in a.get("message","").lower()]

    # dept work from steps
    dept_work = {}
    for s in project.get("steps",[]):
        key = s["step"].split()[0].lower()
        dept_work[key] = s

    return {
        "project_name":        project_name,
        "client":              project.get("client",""),
        "value":               project.get("value",0),
        "project_type":        project.get("project_type",""),
        "status":              project.get("status", get_status(project_name)),
        "started_at":          project.get("started_at",""),
        "completed_at":        project.get("completed_at",""),
        "total_time_s":        project.get("total_time_s",0),
        "on_time_steps":       project.get("on_time_steps",0),
        "total_steps":         project.get("total_steps",0),
        # single source — from project log
        "selected_candidates": project.get("selected_candidates",[]),
        "selected_investor":   project.get("selected_investor"),
        "dept_work":           dept_work,
        "approvals":           proj_approvals,
        "approved_costs":      project.get("total_approval_cost",0),
        "net_revenue":         project.get("net_revenue",0),
        "activities":          activities[:15],
        "roles_needed":        project.get("roles_needed",[]),
        "approvals_generated": project.get("approvals_generated",0),
    }
 # Debug endpoint to check Adiology integration   
@app.get("/notify/adiology/status")
def adiology_status():
    from tools.adiology_notifier import adiology_status
    return adiology_status()
from tools.adiology_notifier import adiology_status
@app.get("/notify/adiology/status")
def adiology_health():
    return adiology_status()
