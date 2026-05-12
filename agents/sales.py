from langchain_groq import ChatGroq
from state.schema import AgentState, new_state
from agents.ceo import should_escalate, ceo_review
from dotenv import load_dotenv
from datetime import datetime
import os, json, re
import csv
from state.company_state import increment_kpi, log_activity

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)
# Investors = former "leads" — companies offering funding/partnership
def load_investors(status_filter=None):
    """Load investors from CSV — same format as leads.csv."""
    leads    = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # check live sheet first
    for fname in ['investors_live.csv', 'leads_live.csv', 'leads.csv']:
        csv_path = os.path.normpath(os.path.join(base_dir, '..', 'data', fname))
        if os.path.exists(csv_path):
            break
    
    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row['budget_inr'] = int(row['budget_inr'])
                except:
                    row['budget_inr'] = 0
                if status_filter is None or row.get('status') == status_filter:
                    leads.append(row)
    except Exception as e:
        print(f"  ⚠️  Could not load investors: {e}")
    return leads
DEALS = [
    {"id":"D001","client":"Infosys Ltd",     "value":5000000,"stage":"negotiation","probability":75},
    {"id":"D002","client":"HDFC Bank",        "value":6000000,"stage":"proposal",   "probability":60},
    {"id":"D003","client":"Zomato",           "value":1500000,"stage":"demo",       "probability":40},
]

def load_leads(status_filter=None):
    """Same as load_investors — kept for backward compatibility."""
    return load_investors(status_filter)

def score_leads() -> dict:
    """Backward compatible — calls score_investors."""
    return score_investors()

# score investors based on interest, budget, and company size
def score_investors() -> dict:
    """Score top investors/fundraisers for CEO to choose from."""
    print(f"\n💼 Sales Agent — Scoring Investors & Fundraisers")
    print("─" * 55)

    investors = load_investors()[:15]
    scored    = []

    for inv in investors:
        interest_score = {"high": 50, "medium": 30, "low": 10}.get(
            inv.get('interest_level','medium'), 20)
        budget_score   = min(int(inv.get('budget_inr',0) / 200000), 30)
        size_score     = {"Enterprise": 20, "Mid-market": 15, "SME": 10}.get(
            inv.get('company_size','SME'), 10)
        total          = min(interest_score + budget_score + size_score, 100)

        scored.append({**inv, "score": total,
                       "type": "investor/fundraiser"})
        flag = "🟢" if total >= 70 else "🟡" if total >= 40 else "🔴"
        print(f"  {flag} {inv.get('company',''):20s} | "
              f"₹{inv.get('budget_inr',0):,} | "
              f"{inv.get('interest_level',''):8s} | Score: {total}/100")

    scored.sort(key=lambda x: x['score'], reverse=True)
    top5 = scored[:5]
    
    if top5:
        print(f"\n  🏆 Top Investor: {top5[0]['company']} "
              f"(₹{top5[0]['budget_inr']:,}) — Score: {top5[0]['score']}/100")
        print(f"  Showing top 5 for CEO selection")

    log_activity(
        f"Investment scored: {len(scored)} investors evaluated. "
        f"Top: {top5[0]['company'] if top5 else 'None'} "
        f"(₹{top5[0]['budget_inr'] if top5 else 0:,})",
        agent="sales", category="investment"
    )

    return {
        "total_evaluated": len(scored),
        "top5_for_ceo":    top5,
        "all_investors":   scored,
    }
# ════════════════════════════════════════════════════════════════════
#  2. PROPOSAL GENERATOR
# ════════════════════════════════════════════════════════════════════
def generate_proposal(lead_id: str) -> dict:
    leads = load_leads()
    lead  = next((l for l in leads if l["id"] == lead_id), None)
    if not lead:
        # try by index
        try:
            lead = leads[int(lead_id)-1]
        except:
            return {"error": f"Lead {lead_id} not found"}

    print(f"\n📝 Sales Agent — Generating Proposal for: {lead['company']}")
    print("─" * 45)

    budget   = lead.get("budget_inr", lead.get("budget", 0))
    interest = lead.get("interest_level", lead.get("interest", "medium"))

    prompt = f"""
Generate a professional sales proposal in JSON format only.
Client      : {lead['contact_name']}, {lead['company']}
Budget      : ₹{int(budget):,}
Interest    : {interest}
Requirement : {lead.get('requirement', 'Business automation')}
Our product : OrgMind — AI-powered business operating system for Indian SMEs

JSON format only, no extra text:
{{
  "title": "...",
  "executive_summary": "2 sentences about why OrgMind fits this client",
  "proposed_solution": "2 sentences on specific solution for their need",
  "pricing": {{"setup": 50000, "monthly": 15000, "annual": 150000}},
  "next_steps": ["Schedule discovery call", "Send NDA", "Demo in 1 week"],
  "validity": "30 days",
  "roi_estimate": "estimated ROI in 1 sentence"
}}
"""
    response = llm.invoke(prompt)
    raw      = response.content.strip().replace("```json","").replace("```","").strip()
    match    = re.search(r'\{.*\}', raw, re.DOTALL)
    try:
        proposal = json.loads(match.group()) if match else {}
    except:
        proposal = {
            "title": f"OrgMind Proposal for {lead['company']}",
            "executive_summary": f"OrgMind can automate {lead.get('requirement','business ops')} for {lead['company']}.",
            "proposed_solution": "Deploy 10 AI agents covering HR, Finance, Sales, Legal, and Operations.",
            "pricing": {"setup": 50000, "monthly": 15000, "annual": 150000},
            "next_steps": ["Schedule discovery call", "Send NDA", "Product demo"],
            "validity": "30 days",
            "roi_estimate": "Expected 40% reduction in operational overhead within 3 months."
        }

    print(f"  📋 Title    : {proposal.get('title','')}")
    print(f"  💰 Setup    : ₹{proposal.get('pricing',{}).get('setup',0):,}")
    print(f"  📅 Valid    : {proposal.get('validity','30 days')}")
    print(f"  ➡️  Next     : {proposal.get('next_steps',['Follow up'])[0]}")


    # CEO approval for high value leads
    if int(budget) > 1000000:
        from state.schema import new_state
        from agents.ceo import should_escalate, ceo_review
        state = new_state(task=f"Sales: High-value proposal for {lead['company']} — ₹{int(budget):,}. Approve to send?",
                         agent="sales", priority="high")
        state["needs_ceo_approval"] = True
        if should_escalate(state):
            ceo_review(state)

    return {
        "lead_id":  lead_id,
        "company":  lead["company"],
        "contact":  lead["contact_name"],
        "budget":   f"₹{int(budget):,}",
        "proposal": proposal,
    }


# ════════════════════════════════════════════════════════════════════
#  3. REVENUE FORECAST
# ════════════════════════════════════════════════════════════════════
def revenue_forecast() -> dict:
    print(f"\n📈 Sales Agent — Revenue Forecast")
    print("─" * 45)

    weighted = sum(d["value"] * d["probability"] / 100 for d in DEALS)
    best     = sum(d["value"] for d in DEALS)

    print(f"  Active Deals     : {len(DEALS)}")
    for d in DEALS:
        print(f"  {d['client']:22s} | ₹{d['value']:,} | {d['stage']:12s} | {d['probability']}% probability")

    print(f"\n  Weighted Forecast : ₹{weighted:,.0f}")
    print(f"  Best Case         : ₹{best:,}")

    prompt = f"""
Sales pipeline data:
Deals: {json.dumps(DEALS)}
Weighted forecast: ₹{weighted:,.0f}

Give 2 specific actions to improve conversion rate.
Reply as JSON array only: ["action1", "action2"]
"""
    response = llm.invoke(prompt)
    raw      = response.content.strip().replace("```json","").replace("```","").strip()
    match    = re.search(r'\[.*\]', raw, re.DOTALL)
    try:
        actions = json.loads(match.group()) if match else []
    except:
        actions = []

    print(f"\n  💡 AI Actions:")
    for i, a in enumerate(actions, 1):
        print(f"     {i}. {a}")

    return {
        "active_deals":      len(DEALS),
        "weighted_forecast": round(weighted, 0),
        "best_case":         best,
        "deals":             DEALS,
        "ai_actions":        actions,
    }


# ════════════════════════════════════════════════════════════════════
#  4. FOLLOW-UP GENERATOR
# ════════════════════════════════════════════════════════════════════
def generate_followups() -> dict:
    print(f"\n📧 Sales Agent — Generating Follow-ups")
    print("─" * 45)

    leads     = load_leads()
    followups = []

    for lead in leads[:8]:
        try:
            days_since = (datetime.now() -
                         datetime.strptime(lead["last_contact"], "%Y-%m-%d")).days
        except:
            days_since = 7

        if days_since >= 5:
            name     = lead.get("contact_name", lead.get("name",""))
            company  = lead.get("company","")
            interest = lead.get("interest_level", lead.get("interest","medium"))

            prompt = f"""
Write a 2-sentence WhatsApp follow-up message for:
Name   : {name} from {company}
Days since last contact: {days_since}
Interest level: {interest}
Reply with just the message text only.
"""
            try:
                response = llm.invoke(prompt)
                msg      = response.content.strip()
            except:
                msg = f"Hi {name}, following up on our discussion about OrgMind for {company}. Would love to schedule a quick demo at your convenience."

            followups.append({
                "lead":       name,
                "company":    company,
                "days_since": days_since,
                "message":    msg,
                "channel":    "WhatsApp" if interest == "high" else "Email",
            })
            print(f"  📬 {name:18s} | {days_since} days | via {followups[-1]['channel']}")
            print(f"     {msg[:70]}...")

    return {"followups_generated": len(followups), "followups": followups}

# ════════════════════════════════════════════════════════════════════
#  5. MAIN SALES AGENT RUNNER
# ════════════════════════════════════════════════════════════════════
def run_sales_agent(action: str, **kwargs) -> AgentState:
    state = new_state(task=f"Sales:{action}", agent="sales", priority="medium")

    if action == "score":
        result = score_investors()

    elif action == "proposal":
        result = generate_proposal(lead_id=kwargs.get("lead_id", "L001"))

    elif action == "forecast":
        result = revenue_forecast()

    elif action == "followup":
        result = generate_followups()

    else:
        result = {"error": f"Unknown action: {action}"}

    state["result"]     = result
    state["updated_at"] = datetime.now().isoformat()
    return state