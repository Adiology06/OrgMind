from datetime import datetime, timedelta
import json, os
from state.project_approvals import (
    set_pending_candidates, set_pending_investors,
    get_project_approval
)
from state.project_status import set_status, mark_completed

LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'projects_log.json')
PROJECT_LOG = []


def _load_projects():
    global PROJECT_LOG
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                PROJECT_LOG = json.load(f)
    except:
        PROJECT_LOG = []

def _save_projects():
    try:
        with open(LOG_FILE, 'w') as f:
            json.dump(PROJECT_LOG, f, indent=2, default=str)
    except:
        pass

_load_projects()


def start_new_project(project_name: str, client: str,
                      value: int, lead_id: str = "",
                      roles_needed: str = "",
                      selected_candidates: list = None,
                      project_type: str = "") -> dict:

    # prevent duplicate
    now = datetime.now()
    _load_projects()
    for p in PROJECT_LOG:
        if p["project_name"] == project_name and p["client"] == client:
            started = datetime.fromisoformat(p["started_at"])
            if (now - started).total_seconds() < 3600:
                print(f"\n  ⏭️  DUPLICATE: {project_name} already started")
                return p

    from agents.hr         import run_hr_agent
    from agents.sales      import run_sales_agent, load_investors
    from agents.finance    import run_finance_agent
    from agents.legal      import run_legal_agent
    from agents.operations import run_operations_agent
    from agents.marketing  import run_marketing_agent
    from agents.it_dev     import run_it_agent
    from agents.support    import run_support_agent
    from agents.analytics  import run_analytics_agent
    from state.company_state import set_active_project, log_activity, update_kpi
    from state.project_status import set_status

    log        = []
    started_at = datetime.now()
    roles      = [r.strip() for r in roles_needed.split(",")] \
                 if roles_needed else ["Developer"]

    # get selected investor details
    selected_investor = None
    if lead_id:
        investors = load_investors()
        selected_investor = next(
            (l for l in investors if l["id"] == lead_id), None)

    set_active_project({
        "name": project_name, "client": client,
        "value": value, "lead_id": lead_id
    })
    set_status(project_name, "pending", "Workflow started")

    # generate project-specific approvals
    proj_approvals = _get_project_approvals(
        project_name, project_type, value,
        roles if isinstance(roles, list) else []
    )

    # queue approvals in background (non-blocking)
    from agents.approval_queue import request_approval as queue_req
    approval_ids = []
    for item in proj_approvals:
        aid = queue_req(
            agent        = item['dept'],
            task         = f"{project_name}: {item['item']} — ₹{item['cost']:,}",
            details      = {"cost": item['cost'], "category": item['dept']},
            priority     = item['priority'],
            project_name = project_name,
            max_per_project = 6,
        )
        if aid:
            approval_ids.append(aid)

    log_activity(
        f"Project approvals generated: {len(approval_ids)} items for {project_name}",
        agent="ceo", category="project"
    )

    deadlines = {
        "Legal Compliance Check":      started_at + timedelta(hours=2),
        "HR Candidate Screening":      started_at + timedelta(hours=4),
        "Finance Budget Setup":        started_at + timedelta(days=1),
        "Sales — Selected Investor":   started_at + timedelta(hours=6),
        "Operations Procurement":      started_at + timedelta(days=2),
        "Marketing Announcement":      started_at + timedelta(days=1),
        "IT Security Audit":           started_at + timedelta(hours=8),
        "Support Channel Activation":  started_at + timedelta(hours=3),
        "Analytics KPI Baseline":      started_at + timedelta(hours=1),
    }

    print(f"\n{'🌟'*20}")
    print(f"  PROJECT  : {project_name}")
    print(f"  CLIENT   : {client}")
    print(f"  VALUE    : ₹{value:,}")
    print(f"  TYPE     : {project_type}")
    print(f"  INVESTOR : {selected_investor.get('company','None') if selected_investor else 'Self-funded'}")
    print(f"  CANDIDATES: {[c.get('name','') for c in (selected_candidates or [])]}")
    print(f"{'🌟'*20}")

    def step(name, fn, deadline):
        print(f"\n  🚀 {name}")
        s = datetime.now()
        try:
            result  = fn()
            dur     = round((datetime.now()-s).total_seconds(), 1)
            on_time = datetime.now() <= deadline
            entry   = {
                "step":           name,
                "status":         "completed",
                "started":        s.isoformat(),
                "completed":      datetime.now().isoformat(),
                "duration_s":     dur,
                "deadline":       deadline.isoformat(),
                "on_time":        on_time,
                "result_summary": _summarize(result),
            }
            log.append(entry)
            log_activity(f"✅ {name} done in {dur}s",
                         agent=name.split()[0].lower(), category="project")
            print(f"  ✅ Done in {dur}s")
            return result
        except Exception as e:
            entry = {
                "step":           name,
                "status":         "error",
                "error":          str(e)[:120],
                "started":        s.isoformat(),
                "deadline":       deadline.isoformat(),
                "on_time":        False,
                "result_summary": f"Error: {str(e)[:80]}",
            }
            log.append(entry)
            print(f"  ❌ {e}")
            return {}

    # run all 9 agents
    step("Legal Compliance Check",
         lambda: run_legal_agent(action="compliance")["result"],
         deadlines["Legal Compliance Check"])

    for role in roles[:2]:
        step(f"HR Candidate Screening — {role}",
             lambda r=role: run_hr_agent(
                 action="screen", job_role=r,
                 skills=r.lower().split())["result"],
             deadlines["HR Candidate Screening"])

    step("Finance Budget Setup",
         lambda: run_finance_agent(action="budget")["result"],
         deadlines["Finance Budget Setup"])

    if selected_investor:
        step("Sales — Selected Investor",
             lambda: {"selected_investor": selected_investor,
                      "message": f"CEO selected {selected_investor['company']} "
                                 f"(₹{selected_investor['budget_inr']:,})",
                      "status": "confirmed"},
             deadlines["Sales — Selected Investor"])
    else:
        step("Sales — Self-funded Project",
             lambda: {"status": "self_funded",
                      "message": "No external investor — self-funded"},
             deadlines["Sales — Selected Investor"])

    step("Operations Procurement",
         lambda: run_operations_agent(action="inventory")["result"],
         deadlines["Operations Procurement"])

    step("Marketing Announcement",
         lambda: run_marketing_agent(action="whatsapp",
                                     campaign_id="C001")["result"],
         deadlines["Marketing Announcement"])

    step("IT Security Audit",
         lambda: run_it_agent(action="security")["result"],
         deadlines["IT Security Audit"])

    step("Support Channel Activation",
         lambda: run_support_agent(action="triage")["result"],
         deadlines["Support Channel Activation"])

    step("Analytics KPI Baseline",
         lambda: run_analytics_agent(action="kpi")["result"],
         deadlines["Analytics KPI Baseline"])

    completed_at  = datetime.now()
    total_time    = round((completed_at-started_at).total_seconds(), 1)
    on_time_steps = len([s for s in log if s.get("on_time")])

    # send WhatsApp to candidates
    if selected_candidates:
        from tools.notifier import send_whatsapp
        from agents.hr import schedule_interview
        import os
        ceo_num = os.getenv("YOUR_WHATSAPP_NUMBER","")
        for cand in selected_candidates:
            sched_r = schedule_interview(
                cand.get("name",""), cand.get("role",
                cand.get("role_applied","")))
            sched   = sched_r.get("schedule",{})
            msg = (
                f"🎉 Congratulations {cand.get('name','')}!\n\n"
                f"Shortlisted for *{cand.get('role',cand.get('role_applied',''))}* "
                f"at *NexaCore Technologies Pvt Ltd*.\n\n"
                f"Project : {project_name}\n"
                f"Client  : {client}\n\n"
                f"📅 Interview:\n"
                f"Date    : {sched.get('date','TBD')}\n"
                f"Time    : {sched.get('time','TBD')}\n"
                f"Mode    : {sched.get('mode','Google Meet')}\n\n"
                f"— HR Team, NexaCore Technologies"
            )
            phone   = cand.get("phone","")
            send_to = f"whatsapp:+91{phone}" \
                      if phone and len(str(phone))==10 else ceo_num
            if send_to:
                send_whatsapp(send_to, msg)
            log_activity(
                f"HR: Interview WhatsApp sent to {cand.get('name','')}",
                agent="hr", category="hr")

    # send WhatsApp to investor
    if selected_investor:
        from tools.notifier import send_whatsapp
        import os
        ceo_num = os.getenv("YOUR_WHATSAPP_NUMBER","")
        phone   = selected_investor.get("phone","")
        send_to = f"whatsapp:+91{phone}" \
                  if phone and len(str(phone))==10 else ceo_num
        msg = (
            f"🤝 Investment Partnership — NexaCore Technologies\n\n"
            f"Dear {selected_investor.get('contact_name','')},\n\n"
            f"Your investment interest has been selected by our CEO.\n\n"
            f"Project  : {project_name}\n"
            f"Client   : {client}\n"
            f"Amount   : ₹{selected_investor.get('budget_inr',0):,}\n\n"
            f"Our team will contact you within 48 hours.\n"
            f"— CEO Office, NexaCore Technologies"
        )
        if send_to:
            send_whatsapp(send_to, msg)
        log_activity(
            f"Sales: WhatsApp sent to investor {selected_investor.get('company','')}",
            agent="sales", category="investment")

    # calculate net revenue
    total_approval_cost = sum(
        item['cost'] for item in proj_approvals
    )
    net_revenue = value - total_approval_cost

    # update company revenue KPI
    from state.company_state import STATE, update_kpi
    current_revenue = STATE["revenue"]["current"]
    new_revenue     = current_revenue + net_revenue
    update_kpi("revenue", new_revenue,
               f"Project {project_name} net revenue: ₹{net_revenue:,}")
    log_activity(
        f"Finance: Revenue updated +₹{net_revenue:,} from {project_name}. "
        f"Company revenue now ₹{new_revenue:,}",
        agent="finance", category="finance")

    project = {
        "project_name":        project_name,
        "client":              client,
        "value":               value,
        "project_type":        project_type,
        "lead_id":             lead_id,
        "selected_investor":   selected_investor,
        "selected_candidates": selected_candidates or [],
        "roles_needed":        roles,
        "started_at":          started_at.isoformat(),
        "completed_at":        completed_at.isoformat(),
        "total_time_s":        total_time,
        "steps":               log,
        "total_steps":         len(log),
        "on_time_steps":       on_time_steps,
        "status":              "pending",
        "approvals_generated": len(approval_ids),
        "approval_ids":        approval_ids,
        "net_revenue":         net_revenue,
        "total_approval_cost": total_approval_cost,
    }

    PROJECT_LOG.append(project)
    _save_projects()

    print(f"\n{'✅'*20}")
    print(f"  WORKFLOW DONE in {total_time}s")
    print(f"  Revenue impact: ₹{net_revenue:,}")
    print(f"{'✅'*20}\n")

    return project


def _summarize(result: dict) -> str:
    """Convert agent result to 1 human-readable sentence."""
    if not result or not isinstance(result, dict):
        return "Completed"
    if "error" in result:
        return f"Error: {result['error'][:60]}"
    if "top_candidate" in result:
        tc = result["top_candidate"]
        return f"Top candidate: {tc.get('name','')} ({tc.get('score',0)}/100) from {tc.get('previous_company','')}"
    if "net_payable" in result:
        return f"Payroll: ₹{result['net_payable']:,} for {result.get('employee','')}"
    if "available" in result:
        return f"Budget available: ₹{result.get('available',0):,} of ₹{result.get('total',0):,}"
    if "total_leads" in result:
        tl = result.get("top_lead", {})
        return f"Top lead: {tl.get('company','')} ₹{tl.get('budget_inr',0):,}"
    if "message" in result:
        return str(result["message"])[:100]
    if "selected_lead" in result:
        sl = result["selected_lead"]
        return f"CEO selected: {sl.get('company','')} (₹{sl.get('budget_inr',0):,})"
    return "Completed successfully"


def get_projects():
    _load_projects()
    return PROJECT_LOG
# This function generates a list of approval items based on the project type and roles needed. It checks for keywords in the project type to determine which approvals are relevant, and also adds role-specific items (e.g., if a video editor is needed, it adds a workstation approval). Each approval item includes the cost, department responsible, and priority level.
def _get_project_approvals(project_name: str, project_type: str, value: int, roles: list) -> list:
    """Generate project-specific approval items based on type."""
    approvals = []
    ptype = (project_type or "").lower()
    is_tech      = any(t in ptype for t in ["tech","ai","ml","it","software","app","web","dev","data"])
    is_marketing = any(t in ptype for t in ["marketing","ads","campaign","media","brand","content"])
    is_legal     = any(t in ptype for t in ["legal","compliance","law","contract","audit"])
    is_ops       = any(t in ptype for t in ["operations","logistics","supply","procurement","franchise"])
    
    # common for all
    approvals.append({
        "item": "Legal contract signing with client",
        "cost": 0, "dept": "legal", "priority": "critical"
    })
    approvals.append({
        "item": f"Project budget allocation: ₹{value:,}",
        "cost": value, "dept": "finance", "priority": "critical"
    })
    
    if is_tech:
        approvals += [
            {"item":"Cloud server setup (AWS/GCP)", "cost":15000,"dept":"it","priority":"high"},
            {"item":"Developer software licenses (JetBrains/VS Code Pro)", "cost":8000,"dept":"it","priority":"medium"},
            {"item":"Security audit and pen testing", "cost":25000,"dept":"it","priority":"high"},
            {"item":"API service subscriptions", "cost":5000,"dept":"it","priority":"medium"},
            {"item":"Project management tool (Jira/Linear)", "cost":3000,"dept":"it","priority":"low"},
        ]
    if is_marketing:
        approvals += [
            {"item":"Camera and video equipment rental", "cost":20000,"dept":"marketing","priority":"high"},
            {"item":"Canva Pro subscription", "cost":4000,"dept":"marketing","priority":"medium"},
            {"item":"Meta/Google Ads budget", "cost":50000,"dept":"marketing","priority":"high"},
            {"item":"Influencer/YouTuber contract", "cost":30000,"dept":"marketing","priority":"high"},
            {"item":"Content studio booking", "cost":10000,"dept":"marketing","priority":"medium"},
            {"item":"Social media scheduling tool", "cost":2000,"dept":"marketing","priority":"low"},
        ]
    if is_legal:
        approvals += [
            {"item":"Legal research database subscription", "cost":12000,"dept":"legal","priority":"high"},
            {"item":"Compliance filing fees", "cost":8000,"dept":"legal","priority":"high"},
            {"item":"Notary and registration charges", "cost":5000,"dept":"legal","priority":"medium"},
        ]
    if is_ops:
        approvals += [
            {"item":"Warehouse/storage space rental", "cost":25000,"dept":"operations","priority":"high"},
            {"item":"Logistics and delivery partners", "cost":15000,"dept":"operations","priority":"high"},
            {"item":"Inventory management software", "cost":6000,"dept":"operations","priority":"medium"},
        ]
        
    for role in roles:
        role_lower = role.lower()
        if "video" in role_lower or "animator" in role_lower:
            approvals.append({"item":f"Workstation for {role} (GPU required)","cost":80000,"dept":"it","priority":"high"})
        if "ml" in role_lower or "ai" in role_lower:
            approvals.append({"item":f"GPU compute credits for {role}","cost":20000,"dept":"it","priority":"high"})
        if "app" in role_lower or "mobile" in role_lower:
            approvals.append({"item":f"Apple Developer + Play Store accounts","cost":10000,"dept":"it","priority":"high"})
            
    return approvals