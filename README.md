🤖 OrgMind — Agentic AI Business Operating System
10 autonomous AI department agents with CEO human-in-the-loop dashboard. Indian labour law compliance engine covering 8 major acts. Real data pipeline via Google Forms amd Whatsapp notification and alerts in real time using self made notifier application. OrgMind is an AI-native business operating system built specifically for Indian SMEs. 

> An autonomous multi-agent AI platform that runs an entire company — HR, Finance, Sales, Marketing, Legal, Operations, IT, Support, Analytics, and Admin — with a CEO Human-in-the-Loop approval system.

Built as a **Final Year 10-Credit Major Project** by a CS/IT student using LangGraph, Groq LLaMA, FastAPI, and React.

🎬 Demo

> CEO selects a project → chooses investor → selects candidates → launches → 9 AI agents deploy in sequence → WhatsApp notifications sent → CEO approves from dashboard → Project completes

**What happens in one click:**
- Legal agent checks Indian law compliance (8 major acts)
- HR agent screens real candidates from Google Forms
- Finance agent sets budget and generates PDF invoice
- Sales agent confirms selected investor
- Operations checks inventory and procurement
- Marketing sends WhatsApp/email campaign
- IT runs security audit
- Support activates client channel
- Analytics generates KPI baseline

---

 🏗️ Architecture

```
Layer 1 — CEO Command (Human-in-the-Loop approval dashboard)
    ↓
Layer 2 — 10 Autonomous Department Agents (LangGraph)
    ↓
Layer 3 — Tool Layer (APIs, WhatsApp, Email, Google Sheets, PDF)
```

---

 📦 Tech Stack

| Layer | Technology |
|---|---|
| Agent Framework | LangGraph + LangChain |
| LLM | Groq LLaMA 3.1 8B (free tier) |
| Backend | FastAPI + Python 3.11 |
| Frontend | React 18 + Vite |
| WhatsApp | Twilio API / Adiology Notifier(Self Build) |
| Email | Gmail SMTP |
| Data | Google Forms → Google Sheets → CSV |
| PDF | ReportLab |
| Persistence | JSON file storage |

---

 🚀 Quick Start

 Prerequisites

- Python 3.11+
- Node.js 18+
- Git

 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/orgmind.git
cd orgmind
```

 2. Backend setup

```bash
 Create virtual environment
python -m venv venv

 Activate it
 Windows:
venv\Scripts\activate
 Mac/Linux:
source venv/bin/activate

 Install dependencies
pip install -r requirements.txt
```

 3. Environment variables

```bash
 Copy the example file
cp .env.example .env

 Fill in your API keys (see Configuration section below)
```

 4. Frontend setup

```bash
cd dashboard
npm install
```

 5. Run the project

**Terminal 1 — Backend:**
```bash
 From root orgmind/ folder
uvicorn main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd dashboard
npm run dev
```

**Open:** `http://localhost:5176`

---

 ⚙️ Configuration

Create a `.env` file in the root folder with these keys:

```env
 Required — Get free at console.groq.com
GROQ_API_KEY=your_groq_key_here

Optional — Get free at aistudio.google.com
GEMINI_API_KEY=your_gemini_key_here

 Optional — WhatsApp notifications (twilio.com/try-twilio)
TWILIO_SID=your_twilio_sid
TWILIO_TOKEN=your_twilio_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
YOUR_WHATSAPP_NUMBER=whatsapp:+91XXXXXXXXXX

 Optional — Email notifications
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16char_app_password
CEO_EMAIL=your_email@gmail.com

 Optional — Google Sheets sync (sheet IDs from URL)
RESUMES_SHEET_ID=your_sheet_id
LEADS_SHEET_ID=your_sheet_id
PROJECTS_SHEET_ID=your_sheet_id

Self Made Notifier — Adiology WhatsApp Notifier
ADIOLOGY_URL=http://localhost:5000
ADIOLOGY_API_KEY=your_adiology_key
```

 Getting Free API Keys

| Service | URL | Time | Cost |
|---|---|---|---|
| Groq (LLM) | console.groq.com | 2 min | Free forever |
| Gemini | aistudio.google.com | 2 min | Free tier |
| Twilio WhatsApp | twilio.com/try-twilio | 10 min | Free sandbox |
| Gmail SMTP | myaccount.google.com → App Passwords | 5 min | Free |

---

 📁 Project Structure

```
orgmind/
├── main.py                     FastAPI entry point — all endpoints
├── requirements.txt            Python dependencies
├── .env.example                Environment template (safe to commit)
├── .gitignore                  Excludes venv, .env, data files
│
├── agents/                     10 AI department agents
│   ├── ceo.py                  CEO approval engine
│   ├── hr.py                   Hiring, payroll, performance
│   ├── finance.py              Budget, invoices, cashflow
│   ├── sales.py                Lead scoring, proposals, forecasts
│   ├── marketing.py            Campaigns, WhatsApp, ads
│   ├── legal.py                Contracts, compliance, law engine
│   ├── operations.py           Inventory, procurement, vendors
│   ├── support.py              Tickets, refunds, chatbot
│   ├── it_dev.py               Bugs, security, roadmap
│   ├── it_coder.py             AI code fixer
│   ├── analytics.py            KPIs, anomaly detection
│   ├── admin.py                Assets, meetings
│   ├── chatbot.py              Support chatbot
│   ├── approval_queue.py       Async CEO approval system
│   └── project_flow.py         Sequential project workflow
│
├── state/                      Shared state management
│   ├── schema.py               AgentState TypedDict
│   ├── company_state.py        KPI and activity tracking
│   ├── project_status.py       Project lifecycle tracking
│   └── project_approvals.py    Candidate/investor selections
│
├── tools/                      External integrations
│   ├── notifier.py             WhatsApp + Email (Twilio/Gmail)
│   ├── adiology_notifier.py    Custom WhatsApp notifier
│   ├── sheets.py               Google Sheets sync
│   ├── calendar_tool.py        Calendar integration
│   ├── email_tool.py           Email tools
│   ├── database.py             Database utilities
│   └── whatsapp.py             WhatsApp tools
│
├── data/                       Data files (gitignored except samples)
│   ├── resumes.csv             Sample candidate data
│   ├── leads.csv               Sample investor/lead data
│   ├── projects.csv            Sample project listings
│   └── indian_laws.json        Indian labour law database
│
└── dashboard/                  React frontend
    ├── src/
    │   ├── App.jsx             Main app — all pages and components
    │   ├── ThemeContext.jsx     Dark/light mode
    │   └── index.css           Global styles
    └── package.json
```

 🎯 Features

 CEO Dashboard
- Real-time KPI monitoring across all departments
- One-click Google Sheets sync (candidates, investors, projects)
- Live activity feed from all agents

 Start New Project (4-step flow)
1. Select project from list (Google Forms or fallback)
2. Choose investor (AI-scored top 5)
3. Select candidates per role (AI-screened)
4. Confirm and launch — all 9 agents fire in sequence

 CEO Approval Inbox
- All agent decisions queue here — no terminal needed
- Approve / Reject / Modify with notes
- Rejected items can be resubmitted with modifications
- Persistent across server restarts

 Project Report
- Auto-generated PDF for every project
- Shows: candidate details, investor details, agent timeline, approvals, financial summary

 IT Code Fixer
- Upload Python, JavaScript, or Java files
- AI detects bugs, fixes them, gives quality score

 Legal Compliance Engine
- Checks 8 major Indian acts: Industrial Disputes Act, PF Act, Gratuity Act, POSH, Maternity Benefits, Minimum Wages, Companies Act, Shops & Establishments

 Marketing
- WhatsApp broadcast to customer lists
- AI-generated campaign messages
- Email bulk send

---

 📊 Google Forms Setup

Create 3 Google Forms and link them to Google Sheets:

**Form 1 — Candidate Resumes**
Fields: Full Name, Email, Phone (WhatsApp), Position Applied For, Years of Experience, Education/College, Key Skills, Previous Company, City, Expected Salary, Notice Period

**Form 2 — Investor/Lead Interest**
Fields: Your Name, Designation, Company Name, Email, Phone, Industry, Company Size, Budget Range, Interest Level, Requirement, City, How did you hear about us

**Form 3 — Project Listings** (CEO fills this)
Fields: Project Name, Client Company, Client Email, Project Value, Project Type, Roles Required, Duration, Description

After creating each form → link to Google Sheet → share Sheet as "Anyone with link can view" → copy Sheet ID from URL → add to `.env`

---

 🌐 Deployment

 Local (Development)
```bash
uvicorn main:app --reload         Backend on :8005
cd dashboard && npm run dev       Frontend on :5176
```

 Production (Future scope)
```bash
 Backend
uvicorn main:app --host 0.0.0.0 --port 8005

 Frontend
cd dashboard
npm run build
Serve dist/ with nginx or Vercel
```

---

 📈 KPI Tracking

The system tracks these company metrics automatically:
- Revenue (updates after each project — base ₹5,00,000 + net project revenues)
- Active leads / investors
- Open support tickets
- Budget utilization %
- Employee attendance
- Active contracts
- Open bugs
- Active campaigns
- Candidates hired
- Invoices generated
- Expenses approved

---

 🇮🇳 Indian Law Compliance

The Legal Agent covers:

| Act | Section | Topic |
|---|---|---|
| Industrial Disputes Act 1947 | Section 25-F | Layoff & Retrenchment |
| Shops & Establishments Act | State-specific | Employee Termination |
| EPF Act 1952 | Section 7A | PF Compliance |
| Payment of Gratuity Act 1972 | Section 4 | Gratuity Payment |
| Maternity Benefit Act 1961 | Section 5 | Maternity Leave |
| POSH Act 2013 | Full Act | Workplace Safety |
| Minimum Wages Act 1948 | Section 12 | Minimum Wage |
| Companies Act 2013 | Section 149 | Board Compliance |

---

 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m 'Add: your feature description'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

 📄 License

MIT License — free to use, modify, and distribute with attribution.

---

 🙏 Acknowledgements

- [LangGraph](https://github.com/langchain-ai/langgraph) — Agent orchestration
- [Groq](https://groq.com) — Free LLM API
- [FastAPI](https://fastapi.tiangolo.com) — Backend framework
- [React](https://react.dev) — Frontend framework
- [Twilio](https://twilio.com) — WhatsApp sandbox

---

 📬 Contact

**NexaCore Technologies Pvt Ltd**
Built as Final Year Project — CS/IT Department

---

· Zero infrastructure cost · 100% open source APIs*
READMEEOF
