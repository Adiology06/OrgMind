from langchain_groq import ChatGroq
from state.schema import AgentState, new_state
from agents.ceo import should_escalate, ceo_review
from dotenv import load_dotenv
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os, json, re
from state.company_state import increment_kpi, log_activity

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)

# ─── Mock data ───────────────────────────────────────────────────────
EXPENSES = [
    {"id": "EXP001", "dept": "Marketing",   "amount": 15000, "desc": "Facebook Ads Campaign",  "status": "pending"},
    {"id": "EXP002", "dept": "Operations",  "amount": 4500,  "desc": "Office Supplies",         "status": "pending"},
    {"id": "EXP003", "dept": "IT",          "amount": 82000, "desc": "Server Upgrade",          "status": "pending"},
    {"id": "EXP004", "dept": "HR",          "amount": 3200,  "desc": "Recruitment Portal Fee",  "status": "pending"},
    {"id": "EXP005", "dept": "Sales",       "amount": 25000, "desc": "Client Entertainment",    "status": "pending"},
]

INVOICES = [
    {"id": "INV001", "client": "Raj Enterprises",  "amount": 125000, "due_date": "2026-05-10", "status": "unpaid"},
    {"id": "INV002", "client": "Mehta & Co",        "amount": 48000,  "due_date": "2026-05-03", "status": "overdue"},
    {"id": "INV003", "client": "TechStart Pvt Ltd", "amount": 95000,  "due_date": "2026-05-20", "status": "unpaid"},
]

BUDGET = {
    "total":     500000,
    "spent":     187000,
    "reserved":  75000,
}


# ════════════════════════════════════════════════════════════════════
#  1. EXPENSE TRACKER + CEO APPROVAL
# ════════════════════════════════════════════════════════════════════
def process_expenses(auto_approve_below: int = 5000) -> dict:
    print(f"\n💸 Finance Agent — Processing Expenses")
    print("─" * 45)

    approved, needs_approval, total_auto = [], [], 0

    for exp in EXPENSES:
        if exp["amount"] <= auto_approve_below:
            exp["status"] = "auto_approved"
            approved.append(exp)
            total_auto += exp["amount"]
            print(f"  ✅ AUTO  | {exp['id']} | {exp['dept']:12s} | ₹{exp['amount']:,} | {exp['desc']}")
        else:
            needs_approval.append(exp)
            print(f"  ⏳ CEO   | {exp['id']} | {exp['dept']:12s} | ₹{exp['amount']:,} | {exp['desc']}")

    increment_kpi("expenses_approved", len(approved))
    log_activity(
        f"Finance: {len(approved)} expenses auto-approved "
        f"(₹{total_auto:,}), {len(needs_approval)} sent to CEO",
        agent="finance", category="finance"
    )

    print(f"\n  Auto-approved : {len(approved)} items = ₹{total_auto:,}")
    print(f"  Needs CEO     : {len(needs_approval)} items")

    return {
        "approved":         approved,
        "pending_ceo":      needs_approval,
        "total_auto":       total_auto,
        "pending_count":    len(needs_approval),
    }


# ════════════════════════════════════════════════════════════════════
#  2. INVOICE GENERATOR (PDF)
# ════════════════════════════════════════════════════════════════════
def generate_invoice(invoice_id: str) -> dict:
    inv = next((i for i in INVOICES if i["id"] == invoice_id), None)
    if not inv:
        return {"error": f"Invoice {invoice_id} not found"}

    print(f"\n📄 Finance Agent — Generating Invoice: {invoice_id}")
    print("─" * 45)

    # ── AI payment reminder message ─────────────────────────────────
    prompt = f"""
Write a professional but friendly payment reminder for:
Client   : {inv['client']}
Amount   : ₹{inv['amount']:,}
Due Date : {inv['due_date']}
Status   : {inv['status']}
Keep it under 3 sentences. Be firm if overdue.
Reply with just the message text, no subject line.
"""
    response = llm.invoke(prompt)
    reminder = response.content.strip()

    # ── Generate PDF ─────────────────────────────────────────────────
    os.makedirs("outputs", exist_ok=True)
    pdf_path = f"outputs/{invoice_id}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4

    # Header
    c.setFillColorRGB(0.2, 0.2, 0.6)
    c.rect(0, h-80, w, 80, fill=True, stroke=False)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, h-50, "OrgMind")
    c.setFont("Helvetica", 11)
    c.drawString(40, h-68, "Autonomous Business Operating System")

    # Invoice details
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, h-120, f"INVOICE — {invoice_id}")
    c.setFont("Helvetica", 11)
    c.drawString(40,  h-150, f"Client   : {inv['client']}")
    c.drawString(40,  h-170, f"Amount   : ₹{inv['amount']:,}")
    c.drawString(40,  h-190, f"Due Date : {inv['due_date']}")
    c.drawString(40,  h-210, f"Status   : {inv['status'].upper()}")
    c.drawString(40,  h-240, f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")

    # Divider
    c.setStrokeColorRGB(0.2, 0.2, 0.6)
    c.line(40, h-260, w-40, h-260)

    # AI reminder
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, h-285, "Payment Reminder:")
    c.setFont("Helvetica", 10)
    # word wrap reminder text
    words = reminder.split()
    line, y = "", h - 305
    for word in words:
        test = f"{line} {word}".strip()
        if c.stringWidth(test, "Helvetica", 10) < w - 80:
            line = test
        else:
            c.drawString(40, y, line)
            y -= 16
            line = word
    if line:
        c.drawString(40, y, line)

    c.save()
    print(f"  📄 PDF saved  : {pdf_path}")
    print(f"  💬 Reminder   : {reminder[:80]}...")

    return {
        "invoice_id": invoice_id,
        "client":     inv["client"],
        "amount":     inv["amount"],
        "status":     inv["status"],
        "pdf_path":   pdf_path,
        "reminder":   reminder,
    }


# ════════════════════════════════════════════════════════════════════
#  3. BUDGET ALERT
# ════════════════════════════════════════════════════════════════════
def check_budget() -> dict:
    print(f"\n📊 Finance Agent — Budget Analysis")
    print("─" * 45)

    available  = BUDGET["total"] - BUDGET["spent"] - BUDGET["reserved"]
    used_pct   = (BUDGET["spent"] / BUDGET["total"]) * 100
    alert_level = "critical" if used_pct > 80 else "warning" if used_pct > 60 else "ok"

    print(f"  Total Budget : ₹{BUDGET['total']:,}")
    print(f"  Spent        : ₹{BUDGET['spent']:,} ({used_pct:.1f}%)")
    print(f"  Reserved     : ₹{BUDGET['reserved']:,}")
    print(f"  Available    : ₹{available:,}")
    print(f"  Alert Level  : {alert_level.upper()}")

    if alert_level in ("warning", "critical"):
        prompt = f"""
Budget status for a startup:
Total: ₹{BUDGET['total']:,}, Spent: ₹{BUDGET['spent']:,} ({used_pct:.1f}%), Available: ₹{available:,}
Give 3 specific cost-cutting recommendations in JSON array format only.
Example: ["Recommendation 1", "Recommendation 2", "Recommendation 3"]
"""
        response = llm.invoke(prompt)
        raw = response.content.strip().replace("```json","").replace("```","").strip()
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        try:
            recommendations = json.loads(match.group()) if match else []
        except:
            recommendations = []

        print(f"\n  💡 AI Recommendations:")
        for i, r in enumerate(recommendations, 1):
            print(f"     {i}. {r}")
    else:
        recommendations = []

    return {
        "total":           BUDGET["total"],
        "spent":           BUDGET["spent"],
        "available":       available,
        "used_pct":        round(used_pct, 1),
        "alert_level":     alert_level,
        "recommendations": recommendations,
    }


# ════════════════════════════════════════════════════════════════════
#  4. CASH FLOW SUMMARY
# ════════════════════════════════════════════════════════════════════
def cash_flow_summary() -> dict:
    print(f"\n💹 Finance Agent — Cash Flow Summary")
    print("─" * 45)

    total_receivable = sum(i["amount"] for i in INVOICES if i["status"] != "paid")
    overdue          = sum(i["amount"] for i in INVOICES if i["status"] == "overdue")
    available        = BUDGET["total"] - BUDGET["spent"] - BUDGET["reserved"]

    print(f"  Cash Available   : ₹{available:,}")
    print(f"  Total Receivable : ₹{total_receivable:,}")
    print(f"  Overdue Payments : ₹{overdue:,}")
    print(f"  Net Position     : ₹{available + total_receivable:,}")

    if overdue > 0:
        print(f"\n  ⚠️  ALERT: ₹{overdue:,} overdue — escalating to CEO")

    return {
        "cash_available":   available,
        "total_receivable": total_receivable,
        "overdue":          overdue,
        "net_position":     available + total_receivable,
        "needs_attention":  overdue > 0,
    }


# ════════════════════════════════════════════════════════════════════
#  5. MAIN FINANCE AGENT RUNNER
# ════════════════════════════════════════════════════════════════════
def run_finance_agent(action: str, **kwargs) -> AgentState:
    state = new_state(task=f"Finance:{action}", agent="finance", priority="medium")

    if action == "expenses":
        result = process_expenses(auto_approve_below=kwargs.get("threshold", 5000))
        if result["pending_count"] > 0:
            state["needs_ceo_approval"] = True
            state["task"] = f"Finance: {result['pending_count']} expenses need CEO approval. Total: ₹{sum(e['amount'] for e in result['pending_ceo']):,}"
            if should_escalate(state):
                state = ceo_review(state)

    elif action == "invoice":
        result = generate_invoice(invoice_id=kwargs.get("invoice_id", "INV001"))

    elif action == "budget":
        result = check_budget()
        if result["alert_level"] == "critical":
            state["needs_ceo_approval"] = True
            state["priority"]           = "critical"
            state["task"]               = f"CRITICAL: Budget {result['used_pct']}% used. Only ₹{result['available']:,} left."
            if should_escalate(state):
                state = ceo_review(state)

    elif action == "cashflow":
        result = cash_flow_summary()
        if result.get("needs_attention"):
            state["needs_ceo_approval"] = True
            state["task"]               = f"Finance: ₹{result['overdue']:,} overdue payments need CEO attention"
            if should_escalate(state):
                state = ceo_review(state)
    else:
        result = {"error": f"Unknown action: {action}"}

    state["result"]     = result
    state["updated_at"] = datetime.now().isoformat()
    return state
