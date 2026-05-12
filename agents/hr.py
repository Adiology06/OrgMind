from langchain_google_genai import ChatGoogleGenerativeAI
from state.company_state import log_activity
from state.schema import AgentState, new_state
from agents.ceo import should_escalate, ceo_review
from dotenv import load_dotenv
from datetime import datetime
import os, json, re
import csv
import os
from state.company_state import log_activity

load_dotenv()

# REPLACE WITH:
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)

# ───  candidate database ────────────────────────────────────────
def load_resumes(role_filter=None):
    resumes  = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '..', 'data', 'resumes.csv')
    csv_path = os.path.normpath(csv_path)

    # also check for live sheet data
    live_path = os.path.join(base_dir, '..', 'data', 'resumes_live.csv')
    live_path = os.path.normpath(live_path)
    if os.path.exists(live_path):
        csv_path = live_path

    if not os.path.exists(csv_path):
        print(f"  ⚠️  resumes.csv not found at {csv_path}")
        return []

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if role_filter is None or role_filter.lower() in row['role_applied'].lower():
                row['skills']           = [s.strip() for s in row['skills'].split(',')]
                row['experience_years'] = int(row.get('experience_years', 0))
                row['expected_salary']  = int(row.get('expected_salary', 0))
                resumes.append(row)
    return resumes

# ─── Mock employee database ──────────────────────────────────────────
EMPLOYEES = [
    {"id": "E001", "name": "Rahul Das",    "dept": "IT",      "salary": 55000, "attendance": 22, "working_days": 26},
    {"id": "E002", "name": "Anjali Singh", "dept": "Sales",   "salary": 48000, "attendance": 25, "working_days": 26},
    {"id": "E003", "name": "Karan Patel",  "dept": "Finance", "salary": 62000, "attendance": 20, "working_days": 26},
]


# ════════════════════════════════════════════════════════════════════
#  1. RESUME SCREENER
# ════════════════════════════════════════════════════════════════════
def screen_resumes(job_role: str, required_skills: list) -> dict:
    print(f"\n📋 HR Agent — Screening Resumes for: {job_role}")
    print("─" * 55)

    # try role-specific first
    candidates = load_resumes(role_filter=job_role)

    # fallback 1 — all resumes if role not found
    if not candidates:
        print(f"  ℹ️  No exact match for '{job_role}' — showing all candidates")
        candidates = load_resumes()

    # fallback 2 — hardcoded if CSV missing
    if not candidates:
        print(f"  ⚠️  CSV not found — using default candidates")
        candidates = [
            {"name":"Arjun Sharma",  "role_applied":"ML Engineer",       "experience_years":3,
             "skills":["python","fastapi","ml","langchain"],
             "previous_company":"Wipro",    "education":"B.Tech IIT Delhi",
             "expected_salary":850000, "notice_period":"30","location":"Delhi",
             "email":"arjun.sharma@gmail.com","phone":"9876543210"},
            {"name":"Sneha Iyer",    "role_applied":"Data Scientist",     "experience_years":4,
             "skills":["python","pytorch","nlp","mlflow"],
             "previous_company":"Google",   "education":"M.Tech IIT Bombay",
             "expected_salary":1500000,"notice_period":"90","location":"Bangalore",
             "email":"sneha.iyer@gmail.com","phone":"9867453210"},
            {"name":"Rohit Verma",   "role_applied":"Backend Developer",  "experience_years":5,
             "skills":["java","spring","docker","kubernetes"],
             "previous_company":"TCS",      "education":"B.Tech BITS Pilani",
             "expected_salary":1200000,"notice_period":"60","location":"Pune",
             "email":"rohit.verma@gmail.com","phone":"9812345670"},
            {"name":"Vikram Nair",   "role_applied":"DevOps Engineer",    "experience_years":6,
             "skills":["aws","docker","terraform","jenkins"],
             "previous_company":"Amazon",   "education":"B.Tech NIT Trichy",
             "expected_salary":1400000,"notice_period":"45","location":"Hyderabad",
             "email":"vikram.nair@gmail.com","phone":"9845123456"},
            {"name":"Priya Mehta",   "role_applied":"Frontend Developer", "experience_years":2,
             "skills":["react","typescript","nodejs","figma"],
             "previous_company":"Infosys",  "education":"B.Tech VJTI Mumbai",
             "expected_salary":650000, "notice_period":"15","location":"Mumbai",
             "email":"priya.mehta@gmail.com","phone":"9823456781"},
        ]

    results = []
    for candidate in candidates[:8]:
        skills = candidate.get('skills', [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',')]

        skill_match = len([s for s in required_skills
                          if any(s.lower() in cs.lower() for cs in skills)])
        skill_score = min(int((skill_match / max(len(required_skills),1)) * 40), 40)
        exp         = candidate.get('experience_years', 0)
        if isinstance(exp, str):
            exp = int(exp) if exp.isdigit() else 0
        exp_score   = min(exp * 5, 30)
        edu         = candidate.get('education','')
        edu_score   = 20 if any(x in edu for x in
                        ['IIT','IIM','BITS','NIT','XLRI','SP Jain','Symbiosis']) else 12
        co          = candidate.get('previous_company','')
        co_score    = 10 if any(c in co for c in
                        ['Google','Amazon','Microsoft','Flipkart','Zomato',
                         'Infosys','TCS','Wipro','Accenture','KPMG','Deloitte']) else 5
        total       = min(skill_score + exp_score + edu_score + co_score, 100)
        status      = "🟢 Strong" if total>=75 else "🟡 Average" if total>=50 else "🔴 Weak"
        sal         = candidate.get('expected_salary', 0)
        if isinstance(sal, str):
            sal = int(sal) if sal.isdigit() else 0

        results.append({
            "name":             candidate.get('name',''),
            "role":             candidate.get('role_applied',''),
            "experience":       f"{exp} years",
            "previous_company": co,
            "education":        edu,
            "expected_salary":  f"₹{int(sal):,}/month",
            "notice_period":    f"{candidate.get('notice_period',30)} days",
            "location":         candidate.get('location',''),
            "score":            total,
            "status":           status,
            "email":            candidate.get('email',''),
            "phone":            candidate.get('phone',''),
            "skills":           skills[:5],
        })
        print(f"  {status} {candidate.get('name',''):20s} | "
              f"{co:12s} | Score: {total:3}/100 | ₹{int(sal):,}")

    results.sort(key=lambda x: x['score'], reverse=True)
    top = results[0] if results else {}
    if top:
        print(f"\n  🏆 Top: {top['name']} ({top['score']}/100) from {top['previous_company']}")
        log_activity(
            f"HR: Screened {len(results)} candidates for {job_role}. "
            f"Top: {top['name']} ({top['score']}/100)",
            agent="hr", category="hr"
        )

    return {
        "job_role":       job_role,
        "total_screened": len(results),
        "candidates":     results,
        "top_candidate":  top,
    }
# ════════════════════════════════════════════════════════════════════
#  2. INTERVIEW SCHEDULER
# ════════════════════════════════════════════════════════════════════
def schedule_interview(candidate_name: str, job_role: str) -> dict:
    """Generate interview schedule and questions using Gemini."""

    print(f"\n📅 HR Agent — Scheduling interview for: {candidate_name}")
    print("─" * 45)

    prompt = f"""
You are an HR manager scheduling an interview.
Candidate : {candidate_name}
Role      : {job_role}
Today     : {datetime.now().strftime('%A, %d %B %Y')}

Generate a professional interview schedule and 5 technical questions.
Reply in this exact JSON format only:
{{
  "date": "Monday, 05 May 2025",
  "time": "11:00 AM",
  "mode": "Google Meet",
  "duration": "45 minutes",
  "interviewer": "Technical Lead",
  "questions": ["Q1", "Q2", "Q3", "Q4", "Q5"]
}}
"""
    response = llm.invoke(prompt)
    raw = response.content.strip().replace("```json","").replace("```","").strip()
    
    try:
        # extract JSON even if surrounded by text
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            schedule = json.loads(match.group())
        else:
            schedule = json.loads(raw)
    except:
        schedule = {"date": "TBD", "time": "TBD", "mode": "Google Meet", "questions": []}

    print(f"  📆 Date      : {schedule.get('date')}")
    print(f"  🕐 Time      : {schedule.get('time')}")
    print(f"  💻 Mode      : {schedule.get('mode')}")
    print(f"  ⏱️  Duration  : {schedule.get('duration','45 min')}")
    print(f"  👤 Interviewer: {schedule.get('interviewer','HR Manager')}")
    print(f"\n  Interview Questions:")
    for i, q in enumerate(schedule.get("questions", []), 1):
        print(f"    {i}. {q}")

    return {"candidate": candidate_name, "schedule": schedule}

# ════════════════════════════════════════════════════════════════════
#  3. PAYROLL CALCULATOR
# ════════════════════════════════════════════════════════════════════
def calculate_payroll(employee_id: str) -> dict:
    """Calculate salary after attendance deduction."""

    emp = next((e for e in EMPLOYEES if e["id"] == employee_id), None)
    if not emp:
        print(f"  ❌ Employee {employee_id} not found")
        return {"error": "Employee not found"}

    print(f"\n💰 HR Agent — Payroll for: {emp['name']}")
    print("─" * 45)

    attendance_pct = emp["attendance"] / emp["working_days"]
    payable = round(emp["salary"] * attendance_pct, 2)
    deduction = emp["salary"] - payable

    print(f"  Employee   : {emp['name']} ({emp['dept']})")
    print(f"  Attendance : {emp['attendance']}/{emp['working_days']} days ({attendance_pct*100:.1f}%)")
    print(f"  Base Salary: ₹{emp['salary']:,}")
    print(f"  Deduction  : ₹{deduction:,}")
    print(f"  Net Payable: ₹{payable:,}")

    # needs CEO approval if payroll > 50000
    needs_approval = payable > 50000

    return {
        "employee":        emp["name"],
        "department":      emp["dept"],
        "base_salary":     emp["salary"],
        "attendance_pct":  round(attendance_pct * 100, 1),
        "deduction":       deduction,
        "net_payable":     payable,
        "needs_approval":  needs_approval,
    }


# ════════════════════════════════════════════════════════════════════
#  4. PERFORMANCE REVIEW
# ════════════════════════════════════════════════════════════════════
def performance_review(employee_name: str, metrics: dict) -> dict:
    """AI-generated performance review."""

    print(f"\n📊 HR Agent — Performance review for: {employee_name}")
    print("─" * 45)

    prompt = f"""
You are an HR performance review AI.
Employee : {employee_name}
Metrics  : {json.dumps(metrics)}

Write a short professional performance review (3 sentences).
Then give a rating: Excellent / Good / Average / Poor.
Reply in this exact JSON format only:
{{"review": "...", "rating": "Good", "recommendation": "..."}}
"""
    response = llm.invoke(prompt)
    raw = response.content.strip().replace("```json","").replace("```","").strip()
    try:
        result = json.loads(raw)
    except:
        result = {"review": response.content, "rating": "N/A", "recommendation": ""}

    print(f"  Rating         : {result.get('rating')}")
    print(f"  Review         : {result.get('review')}")
    print(f"  Recommendation : {result.get('recommendation')}")

    return result


# ════════════════════════════════════════════════════════════════════
#  5. MAIN HR AGENT RUNNER
# ════════════════════════════════════════════════════════════════════
def run_hr_agent(action: str, **kwargs) -> AgentState:
    """
    Entry point. Call this from main graph.
    action: 'screen' | 'schedule' | 'payroll' | 'performance'
    """
    state = new_state(task=f"HR:{action}", agent="hr", priority="medium")

    if action == "screen":
        result = screen_resumes(
            job_role=kwargs.get("job_role", "ML Engineer"),
            required_skills=kwargs.get("skills", []),
        )
    elif action == "schedule":
        result = schedule_interview(
            candidate_name=kwargs.get("candidate_name", ""),
            job_role=kwargs.get("job_role", ""),
        )
    elif action == "payroll":
        result = calculate_payroll(employee_id=kwargs.get("employee_id", "E001"))
        # escalate to CEO if needed
        if result.get("needs_approval"):
            state["needs_ceo_approval"] = True
            state["task"] = f"Payroll approval needed: ₹{result['net_payable']:,} for {result['employee']}"
            if should_escalate(state):
                state = ceo_review(state)
    elif action == "performance":
        result = performance_review(
            employee_name=kwargs.get("employee_name", ""),
            metrics=kwargs.get("metrics", {}),
        )
    else:
        result = {"error": f"Unknown HR action: {action}"}

    state["result"] = result
    state["updated_at"] = datetime.now().isoformat()
    return state