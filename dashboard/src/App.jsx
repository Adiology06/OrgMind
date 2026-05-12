import { useState, useEffect, useCallback, useRef } from "react";
import { ThemeProvider, ThemeToggleButton } from "./ThemeContext";

const API = "http://localhost:8000";

const AGENTS = [
  {
    id: "hr",
    name: "HR",
    icon: "👥",
    color: "#7c6af7",
    desc: "Hiring, Payroll, Performance",
    actions: [
      { label: "Screen Resumes", endpoint: "/hr/screen" },
      { label: "Schedule Interview", endpoint: "/hr/schedule" },
      { label: "Payroll E001", endpoint: "/hr/payroll/E001" },
      { label: "Performance Review", endpoint: "/hr/performance" },
    ],
  },
  {
    id: "finance",
    name: "Finance",
    icon: "💰",
    color: "#48bb78",
    desc: "Budget, Invoices, Cashflow",
    actions: [
      { label: "Process Expenses", endpoint: "/finance/expenses" },
      { label: "Invoice INV002", endpoint: "/finance/invoice/INV002" },
      { label: "Budget Check", endpoint: "/finance/budget" },
      { label: "Cash Flow", endpoint: "/finance/cashflow" },
    ],
  },
  {
    id: "sales",
    name: "Sales",
    icon: "🎯",
    color: "#f6ad55",
    desc: "Leads, Proposals, Forecast",
    actions: [
      { label: "Score Leads", endpoint: "/sales/score" },
      { label: "Generate Proposal", endpoint: "/sales/proposal/L003" },
      { label: "Revenue Forecast", endpoint: "/sales/forecast" },
      { label: "Follow-ups", endpoint: "/sales/followup" },
    ],
  },
  {
    id: "marketing",
    name: "Marketing",
    icon: "📣",
    color: "#fc8181",
    desc: "Campaigns, WhatsApp, Ads",
    actions: [
      { label: "Create Campaign", endpoint: "/marketing/campaign/C001" },
      { label: "WhatsApp Campaign", endpoint: "/marketing/whatsapp/C001" },
      { label: "Ad Performance", endpoint: "/marketing/adperformance" },
      { label: "Social Content", endpoint: "/marketing/social" },
    ],
  },
  {
    id: "legal",
    name: "Legal",
    icon: "⚖️",
    color: "#63b3ed",
    desc: "Contracts, Compliance, Policy",
    actions: [
      { label: "Review Contracts", endpoint: "/legal/contracts" },
      { label: "Compliance Check", endpoint: "/legal/compliance" },
      { label: "Generate Policy", endpoint: "/legal/policy" },
    ],
  },
  {
    id: "operations",
    name: "Operations",
    icon: "⚙️",
    color: "#9f7aea",
    desc: "Inventory, Tasks, Vendors",
    actions: [
      { label: "Inventory Check", endpoint: "/ops/inventory" },
      { label: "Manage Tasks", endpoint: "/ops/tasks" },
      { label: "Vendor Coordination", endpoint: "/ops/vendors" },
    ],
  },
  {
    id: "support",
    name: "Support",
    icon: "🎫",
    color: "#f687b3",
    desc: "Tickets, Refunds, Chatbot",
    actions: [
      { label: "Triage Tickets", endpoint: "/support/triage" },
      { label: "Process Refund", endpoint: "/support/refund/TK003" },
      { label: "Chatbot Query", endpoint: "/support/chatbot" },
    ],
  },
  {
    id: "it",
    name: "IT / Dev",
    icon: "💻",
    color: "#76e4f7",
    desc: "Bugs, Security, Roadmap",
    actions: [
      { label: "Bug Triage", endpoint: "/it/bugs" },
      { label: "Security Audit", endpoint: "/it/security" },
      { label: "Product Roadmap", endpoint: "/it/roadmap" },
    ],
  },
  {
    id: "analytics",
    name: "Analytics",
    icon: "📊",
    color: "#68d391",
    desc: "KPIs, Summary, Anomalies",
    actions: [
      { label: "KPI Dashboard", endpoint: "/analytics/kpi" },
      { label: "Daily Summary", endpoint: "/analytics/summary" },
      { label: "Anomaly Detection", endpoint: "/analytics/anomaly" },
    ],
  },
  {
    id: "admin",
    name: "Admin",
    icon: "🏢",
    color: "#fbb6ce",
    desc: "Assets, Meetings, MoM",
    actions: [
      { label: "Asset Management", endpoint: "/admin/assets" },
      { label: "Meeting Schedule", endpoint: "/admin/meetings" },
    ],
  },
];

const NAV = [
  { id: "overview", label: "CEO Overview", icon: "👑" },
  { id: "newproject", label: "Start Project", icon: "🚀" }, // ADD THIS
  { id: "agents", label: "All Agents", icon: "🤖" },
  { id: "approvals", label: "Approval Inbox", icon: "📥" },
  { id: "kpi", label: "KPI Dashboard", icon: "📊" },
  { id: "codefixer", label: "IT Code Fixer", icon: "🔧" },
  { id: "marketing", label: "Marketing", icon: "📣" },
  { id: "projectapprovals", label: "Project Approvals", icon: "🎯" },
  { id: "report", label: "Project Report", icon: "📋" },
];

function Loading() {
  return (
    <div className="loading">
      <div className="spinner" />
      Agent working...
    </div>
  );
}

function KpiBar({ value, target, unit, name, isLower }) {
  const pct = Math.min((value / target) * 100, 100);
  const good = isLower ? value <= target : pct >= 70;
  const color = good ? "#48bb78" : pct >= 40 ? "#f6ad55" : "#fc8181";
  return (
    <div style={{ marginBottom: 14 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: 4,
        }}
      >
        <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
          {name.replace(/_/g, " ")}
        </span>
        <span style={{ fontSize: 12, color: "var(--text-main)" }}>
          {value} / {target} {unit}
        </span>
      </div>
      <div className="kpi-bar-bg">
        <div
          className="kpi-bar-fill"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
    </div>
  );
}
// A simple live activity feed component that polls the backend every 5 seconds for new activities and displays them in a card. Each activity shows a colored dot based on the agent, the message, and a timestamp.
function ActivityFeed() {
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    const fetch_ = () =>
      fetch(`${API}/state/activity`)
        .then((r) => r.json())
        .then((d) => setActivities(d.activities || []))
        .catch(() => {});
    fetch_();
    const iv = setInterval(fetch_, 5000);
    return () => clearInterval(iv);
  }, []);

  const colors = {
    hr: "#7c6af7",
    finance: "#48bb78",
    sales: "#f6ad55",
    legal: "#63b3ed",
    project: "#fc8181",
    system: "#4a5568",
  };

  if (activities.length === 0) return null;

  return (
    <div className="card" style={{ marginTop: 16 }}>
      <div className="card-title" style={{ marginBottom: 12 }}>
        ⚡ Live Activity Feed
      </div>
      {activities.slice(0, 10).map((a, i) => (
        <div
          key={i}
          style={{
            display: "flex",
            gap: 10,
            alignItems: "flex-start",
            marginBottom: 8,
            paddingBottom: 8,
            borderBottom: i < 9 ? "1px solid var(--border-color)" : "none",
          }}
        >
          <div
            style={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              marginTop: 5,
              flexShrink: 0,
              background: colors[a.agent] || "#4a5568",
            }}
          />
          <div style={{ flex: 1 }}>
            <div
              style={{
                fontSize: 12,
                color: "var(--text-main)",
                lineHeight: 1.4,
              }}
            >
              {a.message}
            </div>
            <div
              style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 2 }}
            >
              {a.agent} · {a.time}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
// ── Project Approvals for CEO ─────────────────────────────────────────

function ProjectApprovals() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    fetch(`${API}/ceo/projects`)
      .then((r) => r.json())
      .then((d) => {
        setProjects(d.projects || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    load();
    const iv = setInterval(load, 8000);
    return () => clearInterval(iv);
  }, []);

  const deptIcons = {
    legal: "⚖️",
    hr: "👥",
    finance: "💰",
    sales: "🎯",
    operations: "⚙️",
    marketing: "📣",
    it: "💻",
    support: "🎫",
    analytics: "📊",
    admin: "🏢",
  };

  if (loading) return <Loading />;

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">🎯 Project Overview</div>
          <div className="page-sub">
            All projects — candidates, investors, timelines, approvals
          </div>
        </div>
        <span className="badge badge-purple">{projects.length} projects</span>
      </div>

      {projects.length === 0 && (
        <div className="card" style={{ textAlign: "center", padding: 40 }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>📋</div>
          <div style={{ color: "var(--text-muted)", fontSize: 13 }}>
            No projects yet — start one from Start Project
          </div>
        </div>
      )}

      {projects.map((p, i) => {
        const cands = p.selected_candidates || [];
        const inv = p.selected_investor;

        return (
          <div key={i} className="card" style={{ marginBottom: 20 }}>
            {/* Project Header */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                marginBottom: 16,
                paddingBottom: 16,
                borderBottom: "1px solid var(--border-color)",
              }}
            >
              <div>
                <div
                  style={{
                    fontSize: 17,
                    fontWeight: 500,
                    color: "var(--text-main)",
                    marginBottom: 4,
                  }}
                >
                  {p.project_name}
                </div>
                <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                  {p.client} · {p.project_type || "General"} ·{" "}
                  {p.roles_needed?.join(", ") || ""}
                </div>
                <div style={{ fontSize: 11, color: "#4a5568", marginTop: 4 }}>
                  Started:{" "}
                  {new Date(p.started_at).toLocaleString("en-IN", {
                    dateStyle: "medium",
                    timeStyle: "short",
                  })}
                </div>
              </div>
              <div
                style={{ textAlign: "right", flexShrink: 0, marginLeft: 16 }}
              >
                <div
                  style={{
                    fontSize: 20,
                    fontWeight: 700,
                    color: "#48bb78",
                    marginBottom: 4,
                  }}
                >
                  ₹{(p.value || 0).toLocaleString()}
                </div>
                <span
                  className={`badge ${
                    p.status === "completed"
                      ? "badge-blue"
                      : p.status === "active"
                        ? "badge-green"
                        : "badge-yellow"
                  }`}
                  style={{ fontSize: 11 }}
                >
                  {(p.status || "pending").toUpperCase()}
                </span>
                {p.net_revenue !== undefined && (
                  <div
                    style={{
                      fontSize: 11,
                      marginTop: 4,
                      color: p.net_revenue >= 0 ? "#48bb78" : "#fc8181",
                    }}
                  >
                    Net: ₹{(p.net_revenue || 0).toLocaleString()}
                  </div>
                )}
              </div>
            </div>

            <div className="grid grid-2" style={{ marginBottom: 16 }}>
              {/* Selected Candidates */}
              <div>
                <div
                  style={{
                    fontSize: 11,
                    fontWeight: 500,
                    color: "var(--text-muted)",
                    textTransform: "uppercase",
                    letterSpacing: ".06em",
                    marginBottom: 10,
                  }}
                >
                  👥 Selected Candidate(s)
                </div>
                {cands.length > 0 ? (
                  cands.map((c, ci) => (
                    <div
                      key={ci}
                      style={{
                        padding: "10px 12px",
                        borderRadius: 8,
                        marginBottom: 8,
                        background: "#0d2818",
                        border: "1px solid #48bb78",
                      }}
                    >
                      <div
                        style={{
                          fontSize: 13,
                          fontWeight: 500,
                          color: "var(--text-main)",
                          marginBottom: 2,
                        }}
                      >
                        {c.name}
                      </div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                        {c.role || c.role_applied} · {c.experience} ·
                        {c.previous_company}
                      </div>
                      <div
                        style={{
                          fontSize: 11,
                          color: "var(--text-muted)",
                          marginTop: 2,
                        }}
                      >
                        {c.expected_salary} · {c.notice_period} · {c.location}
                      </div>
                      <div
                        style={{
                          display: "flex",
                          gap: 4,
                          marginTop: 4,
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <span style={{ fontSize: 10, color: "#4a5568" }}>
                          📧 {c.email}
                        </span>
                        <span
                          style={{
                            fontSize: 11,
                            fontWeight: 700,
                            color:
                              c.score >= 75
                                ? "#48bb78"
                                : c.score >= 50
                                  ? "#f6ad55"
                                  : "#fc8181",
                          }}
                        >
                          {c.score}/100
                        </span>
                      </div>
                      <div
                        style={{ fontSize: 10, color: "#48bb78", marginTop: 4 }}
                      >
                        ✅ Interview WhatsApp sent
                      </div>
                    </div>
                  ))
                ) : (
                  <div
                    style={{
                      fontSize: 12,
                      color: "var(--text-muted)",
                      padding: "12px 0",
                      textAlign: "center",
                    }}
                  >
                    No candidate selected
                  </div>
                )}
              </div>

              {/* Selected Investor */}
              <div>
                <div
                  style={{
                    fontSize: 11,
                    fontWeight: 500,
                    color: "var(--text-muted)",
                    textTransform: "uppercase",
                    letterSpacing: ".06em",
                    marginBottom: 10,
                  }}
                >
                  💼 Investor / Partner
                </div>
                {inv ? (
                  <div
                    style={{
                      padding: "10px 12px",
                      borderRadius: 8,
                      background: "#0a1240",
                      border: "1px solid #7c6af7",
                    }}
                  >
                    <div
                      style={{
                        fontSize: 13,
                        fontWeight: 500,
                        color: "var(--text-main)",
                        marginBottom: 4,
                      }}
                    >
                      {inv.company}
                    </div>
                    {[
                      ["Contact", inv.contact_name],
                      ["Designation", inv.designation],
                      ["Industry", inv.industry],
                      [
                        "Investment",
                        `₹${parseInt(inv.budget_inr || 0).toLocaleString()}`,
                      ],
                      ["Interest", inv.interest_level],
                      ["Score", `${inv.score}/100`],
                    ].map(
                      ([k, v]) =>
                        v && (
                          <div
                            key={k}
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              padding: "3px 0",
                              fontSize: 11,
                            }}
                          >
                            <span style={{ color: "var(--text-muted)" }}>
                              {k}
                            </span>
                            <span
                              style={{
                                color: "var(--text-main)",
                                fontWeight: 500,
                              }}
                            >
                              {v}
                            </span>
                          </div>
                        ),
                    )}
                    <div
                      style={{ fontSize: 10, color: "#9f7aea", marginTop: 6 }}
                    >
                      ✅ Partnership WhatsApp sent
                    </div>
                  </div>
                ) : (
                  <div
                    style={{
                      padding: "10px 12px",
                      borderRadius: 8,
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border-color)",
                      fontSize: 12,
                      color: "var(--text-muted)",
                    }}
                  >
                    Self-funded — no external investor
                  </div>
                )}
              </div>
            </div>

            {/* Agent Timeline */}
            <div style={{ marginBottom: 16 }}>
              <div
                style={{
                  fontSize: 11,
                  fontWeight: 500,
                  color: "var(--text-muted)",
                  textTransform: "uppercase",
                  letterSpacing: ".06em",
                  marginBottom: 10,
                }}
              >
                🤖 Agent Timeline — {p.on_time_steps}/{p.total_steps} on time ·{" "}
                {p.total_time_s}s total
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {(p.steps || []).map((s, si) => (
                  <div
                    key={si}
                    style={{
                      padding: "6px 10px",
                      borderRadius: 6,
                      fontSize: 11,
                      background:
                        s.status === "completed"
                          ? s.on_time
                            ? "#0a1f0a"
                            : "#1f1200"
                          : "#1f0a0a",
                      border: `1px solid ${
                        s.status === "completed"
                          ? s.on_time
                            ? "#48bb78"
                            : "#f6ad55"
                          : "#fc8181"
                      }`,
                      color:
                        s.status === "completed"
                          ? s.on_time
                            ? "#48bb78"
                            : "#f6ad55"
                          : "#fc8181",
                    }}
                  >
                    {deptIcons[s.step.split(" ")[0].toLowerCase()] || "📋"}{" "}
                    {s.step.split("—")[0].trim()}
                    {s.duration_s ? ` · ${s.duration_s}s` : ""}
                  </div>
                ))}
              </div>
            </div>

            {/* Approvals Summary */}
            <div
              style={{
                display: "flex",
                gap: 16,
                padding: "10px 14px",
                background: "var(--bg-secondary)",
                borderRadius: 8,
                border: "1px solid var(--border-color)",
                flexWrap: "wrap",
                fontSize: 12,
              }}
            >
              <span style={{ color: "var(--text-muted)" }}>
                Approvals generated:
                <strong style={{ color: "var(--text-main)", marginLeft: 4 }}>
                  {p.approvals_generated || 0}
                </strong>
              </span>
              <span style={{ color: "var(--text-muted)" }}>
                Project value:
                <strong style={{ color: "#48bb78", marginLeft: 4 }}>
                  ₹{(p.value || 0).toLocaleString()}
                </strong>
              </span>
              <span style={{ color: "var(--text-muted)" }}>
                Operational cost:
                <strong style={{ color: "#f6ad55", marginLeft: 4 }}>
                  ₹{(p.total_approval_cost || 0).toLocaleString()}
                </strong>
              </span>
              <span style={{ color: "var(--text-muted)" }}>
                Net revenue:
                <strong
                  style={{
                    color: (p.net_revenue || 0) >= 0 ? "#7c6af7" : "#fc8181",
                    marginLeft: 4,
                  }}
                >
                  ₹{(p.net_revenue || 0).toLocaleString()}
                </strong>
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
// ── CEO Overview ─────────────────────────────────────────────────────
function Overview({ approvals }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState(null);
  const [adiologyOnline, setAdiologyOnline] = useState(false);
  const [newItems, setNewItems] = useState({
    candidates: 0,
    projects: 0,
    investors: 0,
  });

  const loadKPI = () => {
    const timer = setTimeout(() => {
      setLoading(false);
      setError(true);
    }, 8000);
    fetch(`${API}/analytics/kpi`)
      .then((r) => r.json())
      .then((d) => {
        clearTimeout(timer);
        setData(d);
        setLoading(false);
      })
      .catch(() => {
        clearTimeout(timer);
        setLoading(false);
        setError(true);
      });
  };

  useEffect(() => {
    loadKPI();
  }, []);

  const syncAll = async () => {
    setSyncing(true);
    setSyncResult(null);
    try {
      const r = await fetch(`${API}/sync/all`);
      const d = await r.json();
      setSyncResult(d);
      // update new items count
      setNewItems({
        candidates: d.resumes?.count || 0,
        investors: d.leads?.count || 0,
        projects: d.projects?.count || 0,
      });
    } catch (e) {
      setSyncResult({ error: e.message });
    }
    setSyncing(false);
  };

  const stats = [
    {
      label: "Active Agents",
      value: "10",
      sub: "All systems operational",
      color: "#7c6af7",
    },
    {
      label: "Pending Approvals",
      value: approvals.length,
      sub: "Waiting for your decision",
      color: "#f6ad55",
    },
    {
      label: "API Calls Today",
      value: "42+",
      sub: "Groq LLM requests",
      color: "#48bb78",
    },
    {
      label: "Departments Live",
      value: "10",
      sub: "HR · Finance · Sales · +7",
      color: "#63b3ed",
    },
  ];
  // Check Adiology status on load
  useEffect(() => {
    fetch(`${API}/notify/adiology/status`)
      .then((r) => r.json())
      .then((d) => setAdiologyOnline(d.online || false))
      .catch(() => {});
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">👑 CEO Command Center</div>
          <div className="page-sub">
            You have full control — all agents report to you
          </div>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <button
            onClick={syncAll}
            disabled={syncing}
            style={{
              padding: "8px 14px",
              borderRadius: 8,
              background: syncing ? "var(--bg-secondary)" : "#1a1240",
              border: "1px solid #7c6af7",
              color: "#9f7aea",
              cursor: syncing ? "not-allowed" : "pointer",
              fontSize: 12,
              fontWeight: 500,
            }}
          >
            {syncing ? "⏳ Syncing..." : "🔄 Sync Google Sheets"}
          </button>

          {/* PASTE THE NEW STATUS BLOCK HERE */}
          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
              <span
                className={`status-dot ${adiologyOnline ? "dot-green" : "dot-yellow"}`}
              />
              <span
                style={{
                  fontSize: 11,
                  color: adiologyOnline ? "#48bb78" : "#f6ad55",
                }}
              >
                {adiologyOnline ? "Adiology Online" : "Adiology Offline"}
              </span>
            </div>
            <span className="status-dot dot-green" />
            <span style={{ fontSize: 12, color: "#48bb78" }}>
              All systems live
            </span>
          </div>
        </div>
      </div>

      {/* sync result banner */}
      {syncResult && !syncResult.error && (
        <div
          style={{
            padding: "10px 14px",
            borderRadius: 8,
            marginBottom: 16,
            background: "#0d2818",
            border: "1px solid #48bb78",
            display: "flex",
            gap: 20,
            flexWrap: "wrap",
            fontSize: 12,
          }}
        >
          <span style={{ color: "#48bb78", fontWeight: 500 }}>
            ✅ Sync complete
          </span>
          <span style={{ color: "var(--text-muted)" }}>
            Candidates:{" "}
            <strong style={{ color: "var(--text-main)" }}>
              {syncResult.resumes?.count || 0}
            </strong>
          </span>
          <span style={{ color: "var(--text-muted)" }}>
            Investors:{" "}
            <strong style={{ color: "var(--text-main)" }}>
              {syncResult.leads?.count || 0}
            </strong>
          </span>
          <span style={{ color: "var(--text-muted)" }}>
            Projects:{" "}
            <strong style={{ color: "var(--text-main)" }}>
              {syncResult.projects?.count || 0}
            </strong>
          </span>
          <span
            style={{
              color: "var(--text-muted)",
              marginLeft: "auto",
              fontSize: 11,
            }}
          >
            Sources: {syncResult.resumes?.source} · {syncResult.leads?.source}
          </span>
        </div>
      )}

      <div className="grid grid-4" style={{ marginBottom: 20 }}>
        {stats.map((s) => (
          <div className="card" key={s.label}>
            <div className="card-title">{s.label}</div>
            <div className="card-value" style={{ color: s.color }}>
              {s.value}
            </div>
            <div className="card-sub">{s.sub}</div>
          </div>
        ))}
      </div>

      {/* new submissions from Google Forms */}
      {(newItems.candidates > 0 ||
        newItems.investors > 0 ||
        newItems.projects > 0) && (
        <div className="card" style={{ marginBottom: 16 }}>
          <div className="card-title" style={{ marginBottom: 12 }}>
            📬 New Submissions from Google Forms
          </div>
          <div className="grid grid-3">
            {[
              {
                label: "Candidates",
                count: newItems.candidates,
                color: "#7c6af7",
                icon: "👥",
                page: "hr",
              },
              {
                label: "Investors",
                count: newItems.investors,
                color: "#48bb78",
                icon: "💼",
                page: "sales",
              },
              {
                label: "Projects",
                count: newItems.projects,
                color: "#f6ad55",
                icon: "🚀",
                page: "newproject",
              },
            ].map((item) => (
              <div
                key={item.label}
                style={{
                  padding: "14px",
                  borderRadius: 8,
                  textAlign: "center",
                  background: "var(--bg-secondary)",
                  border: `1px solid ${item.count > 0 ? item.color : "var(--border-color)"}`,
                }}
              >
                <div style={{ fontSize: 24, marginBottom: 4 }}>{item.icon}</div>
                <div
                  style={{ fontSize: 22, fontWeight: 500, color: item.color }}
                >
                  {item.count}
                </div>
                <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                  {item.label}
                </div>
                {item.count > 0 && (
                  <div
                    style={{ fontSize: 10, color: item.color, marginTop: 4 }}
                  >
                    ● Just synced
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {loading && (
        <div className="card" style={{ padding: 30, textAlign: "center" }}>
          <div className="loading" style={{ justifyContent: "center" }}>
            <div className="spinner" />
            Loading KPI data...
          </div>
        </div>
      )}

      {error && !loading && (
        <div className="card" style={{ padding: 20, marginBottom: 16 }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <span style={{ color: "var(--text-muted)", fontSize: 13 }}>
              KPI data loading...
            </span>
            <button
              onClick={() => {
                setError(false);
                setLoading(true);
                loadKPI();
              }}
              style={{
                color: "#7c6af7",
                background: "none",
                border: "none",
                cursor: "pointer",
                fontSize: 13,
              }}
            >
              Retry
            </button>
          </div>
          <div
            style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 12 }}
          >
            {AGENTS.map((a) => (
              <div
                key={a.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "4px 10px",
                  background: "var(--bg-secondary)",
                  borderRadius: 20,
                  fontSize: 12,
                }}
              >
                <span>{a.icon}</span>
                <span style={{ color: "var(--text-main)" }}>{a.name}</span>
                <span
                  className="badge badge-green"
                  style={{ padding: "1px 6px" }}
                >
                  Live
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {data && !loading && (
        <div className="grid grid-2">
          <div className="card">
            <div className="card-title">Company KPIs</div>
            {Object.entries(data.kpis || {}).map(([k, v]) => (
              <KpiBar
                key={k}
                name={k}
                value={v.current}
                target={v.target}
                unit={v.unit}
                isLower={k === "open_tickets" || k === "bugs_open"}
              />
            ))}
          </div>
          <div className="card">
            <div className="card-title" style={{ marginBottom: 12 }}>
              Agent Status
            </div>
            {AGENTS.map((a) => (
              <div
                key={a.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  marginBottom: 10,
                }}
              >
                <span style={{ fontSize: 18 }}>{a.icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 12, color: "var(--text-main)" }}>
                    {a.name}
                  </div>
                  <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
                    {a.desc}
                  </div>
                </div>
                <span className="badge badge-green">● Live</span>
              </div>
            ))}
          </div>
        </div>
      )}
      <ActivityFeed />
    </div>
  );
}

// ── All Agents ────────────────────────────────────────────────────────
function Agents() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [active, setActive] = useState(null);

  const run = useCallback(async (endpoint, label) => {
    setLoading(true);
    setActive(label);
    setResult(null);
    try {
      const r = await fetch(`${API}${endpoint}`);
      const d = await r.json();
      setResult(JSON.stringify(d, null, 2));
    } catch (e) {
      setResult(`Error: ${e.message}`);
    }
    setLoading(false);
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">🤖 Agent Control Panel</div>
          <div className="page-sub">
            Trigger any agent action — watch terminal for CEO approval prompts
          </div>
        </div>
      </div>

      <div className="grid grid-2" style={{ marginBottom: 20 }}>
        {AGENTS.map((agent) => (
          <div className="agent-card" key={agent.id}>
            <div className="agent-header">
              <div
                className="agent-icon"
                style={{ background: agent.color + "22" }}
              >
                {agent.icon}
              </div>
              <div>
                <div className="agent-name">{agent.name} Agent</div>
                <div className="agent-desc">{agent.desc}</div>
              </div>
              <span
                className="badge badge-green"
                style={{ marginLeft: "auto" }}
              >
                Live
              </span>
            </div>
            <div className="agent-actions">
              {agent.actions.map((a) => (
                <button
                  key={a.label}
                  className="action-btn"
                  disabled={loading}
                  onClick={() => run(a.endpoint, a.label)}
                >
                  {loading && active === a.label ? "..." : a.label}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {loading && <Loading />}
      {result && (
        <div>
          <div
            style={{
              fontSize: 12,
              color: "var(--text-muted)",
              marginBottom: 8,
            }}
          >
            ↳ Result: <span style={{ color: "var(--accent)" }}>{active}</span>
          </div>
          <div className="result-panel">{result}</div>
        </div>
      )}
    </div>
  );
}

// ── Approval Inbox ────────────────────────────────────────────────────
// eslint-disable-next-line no-unused-vars
function Approvals({ approvals: _approvals, onRefresh }) {
  const [pending, setPending] = useState([]);
  const [done, setDone] = useState([]);
  const [rejected, setRejected] = useState([]);
  const [deciding, setDeciding] = useState({});
  const [notes, setNotes] = useState({});
  const [modifiedTask, setModifiedTask] = useState({});
  const [resubmitting, setResubmitting] = useState({});

  const fetchAll = () => {
    fetch(`${API}/ceo/approvals/all`)
      .then((r) => r.json())
      .then((d) => {
        const all = d.approvals || [];
        setPending(all.filter((a) => a.status === "pending"));
        setDone(all.filter((a) => a.status === "decided"));
      })
      .catch(() => {});

    fetch(`${API}/ceo/approvals/rejected`)
      .then((r) => r.json())
      .then((d) => setRejected(d.rejected || []))
      .catch(() => {});
  };

  useEffect(() => {
    fetchAll();
    const iv = setInterval(fetchAll, 3000);
    return () => clearInterval(iv);
  }, []);

  const decide = async (approval_id, decision) => {
    setDeciding((d) => ({ ...d, [approval_id]: true }));
    try {
      await fetch(`${API}/ceo/approvals/decide`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          approval_id,
          decision,
          notes: notes[approval_id] || "",
        }),
      });
    } catch (e) {
      /* handled */
    }
    setDeciding((d) => ({ ...d, [approval_id]: false }));
    fetchAll();
    if (onRefresh) onRefresh();
  };

  const resubmit = async (approval_id) => {
    setResubmitting((r) => ({ ...r, [approval_id]: true }));
    try {
      await fetch(`${API}/ceo/approvals/resubmit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          approval_id,
          modified_task: modifiedTask[approval_id] || "",
        }),
      });
    } catch (e) {
      /* handled */
    }
    setResubmitting((r) => ({ ...r, [approval_id]: false }));
    fetchAll();
    if (onRefresh) onRefresh();
  };

  const priorityColor = (p) =>
    p === "critical" ? "#fc8181" : p === "high" ? "#f6ad55" : "#63b3ed";

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">📥 CEO Approval Inbox</div>
          <div className="page-sub">
            Approve, reject, or resubmit — no terminal needed
          </div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <span className="badge badge-red">{pending.length} pending</span>
          <span className="badge badge-yellow">{rejected.length} rejected</span>
          <span className="badge badge-green">{done.length} decided</span>
        </div>
      </div>

      {/* ── PENDING ─────────────────────────────────── */}
      {pending.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <div
            style={{
              fontSize: 11,
              fontWeight: 500,
              color: "#fc8181",
              marginBottom: 10,
              textTransform: "uppercase",
              letterSpacing: ".06em",
            }}
          >
            ⏳ Pending Your Decision ({pending.length})
          </div>

          {pending.map((a) => (
            <div
              key={a.approval_id}
              style={{
                background: "var(--bg-secondary)",
                border: `1px solid ${priorityColor(a.priority)}44`,
                borderRadius: 10,
                padding: 16,
                marginBottom: 12,
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  marginBottom: 10,
                }}
              >
                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      display: "flex",
                      gap: 8,
                      alignItems: "center",
                      marginBottom: 6,
                      flexWrap: "wrap",
                    }}
                  >
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 600,
                        color: "#f6ad55",
                        textTransform: "uppercase",
                        letterSpacing: ".06em",
                      }}
                    >
                      {a.agent} dept
                    </span>
                    <span
                      className={`badge ${
                        a.priority === "critical"
                          ? "badge-red"
                          : a.priority === "high"
                            ? "badge-yellow"
                            : "badge-blue"
                      }`}
                    >
                      {a.priority}
                    </span>
                    <span style={{ fontSize: 10, color: "#4a5568" }}>
                      #{a.approval_id}
                    </span>
                    {a.resubmission && (
                      <span className="badge badge-purple">resubmitted</span>
                    )}
                    {a.project_name && (
                      <span
                        style={{
                          fontSize: 10,
                          color: "#7c6af7",
                          background: "#1a1240",
                          padding: "2px 8px",
                          borderRadius: 10,
                        }}
                      >
                        {a.project_name}
                      </span>
                    )}
                  </div>
                  <div
                    style={{
                      fontSize: 14,
                      color: "var(--text-main)",
                      marginBottom: 4,
                    }}
                  >
                    {a.task}
                  </div>
                  {a.details?.summary && (
                    <div
                      style={{
                        fontSize: 12,
                        color: "var(--text-muted)",
                        fontStyle: "italic",
                        lineHeight: 1.5,
                      }}
                    >
                      {a.details.summary}
                    </div>
                  )}
                </div>
                <div
                  style={{
                    fontSize: 10,
                    color: "#4a5568",
                    whiteSpace: "nowrap",
                    marginLeft: 12,
                  }}
                >
                  {new Date(a.requested_at).toLocaleTimeString("en-IN")}
                </div>
              </div>

              <input
                style={{
                  width: "100%",
                  background: "#1a1a2e",
                  border: "1px solid #2d2d4a",
                  borderRadius: 6,
                  padding: "6px 10px",
                  color: "var(--text-main)",
                  fontSize: 12,
                  marginBottom: 10,
                }}
                placeholder="Add notes or modification (optional)..."
                value={notes[a.approval_id] || ""}
                onChange={(e) =>
                  setNotes((n) => ({
                    ...n,
                    [a.approval_id]: e.target.value,
                  }))
                }
              />

              <div style={{ display: "flex", gap: 8 }}>
                <button
                  onClick={() => decide(a.approval_id, "approve")}
                  disabled={deciding[a.approval_id]}
                  style={{
                    flex: 1,
                    padding: "9px 0",
                    borderRadius: 8,
                    background: "#0d2818",
                    color: "#48bb78",
                    cursor: "pointer",
                    fontSize: 13,
                    fontWeight: 500,
                    outline: "1px solid #48bb78",
                    border: "none",
                  }}
                >
                  {deciding[a.approval_id] ? "..." : "✅ Approve"}
                </button>
                <button
                  onClick={() => decide(a.approval_id, "reject")}
                  disabled={deciding[a.approval_id]}
                  style={{
                    flex: 1,
                    padding: "9px 0",
                    borderRadius: 8,
                    background: "#2d1515",
                    color: "#fc8181",
                    cursor: "pointer",
                    fontSize: 13,
                    fontWeight: 500,
                    outline: "1px solid #fc8181",
                    border: "none",
                  }}
                >
                  {deciding[a.approval_id] ? "..." : "❌ Reject"}
                </button>
                <button
                  onClick={() => decide(a.approval_id, "modify")}
                  disabled={deciding[a.approval_id]}
                  style={{
                    padding: "9px 16px",
                    borderRadius: 8,
                    background: "#2d2510",
                    color: "#f6ad55",
                    cursor: "pointer",
                    fontSize: 13,
                    fontWeight: 500,
                    outline: "1px solid #f6ad55",
                    border: "none",
                  }}
                >
                  ✏️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── REJECTED — resubmit ──────────────────────── */}
      {rejected.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <div
            style={{
              fontSize: 11,
              fontWeight: 500,
              color: "#f6ad55",
              marginBottom: 10,
              textTransform: "uppercase",
              letterSpacing: ".06em",
            }}
          >
            ❌ Rejected — Modify & Resubmit ({rejected.length})
          </div>

          {rejected.map((a) => (
            <div
              key={a.approval_id}
              style={{
                background: "var(--bg-secondary)",
                border: "1px solid #2d2510",
                borderRadius: 10,
                padding: 16,
                marginBottom: 12,
              }}
            >
              <div
                style={{
                  display: "flex",
                  gap: 8,
                  alignItems: "center",
                  marginBottom: 6,
                  flexWrap: "wrap",
                }}
              >
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 600,
                    color: "#f6ad55",
                    textTransform: "uppercase",
                  }}
                >
                  {a.agent} dept
                </span>
                <span className="badge badge-red">Rejected</span>
                <span style={{ fontSize: 10, color: "#4a5568" }}>
                  #{a.approval_id}
                </span>
                {a.project_name && (
                  <span
                    style={{
                      fontSize: 10,
                      color: "#7c6af7",
                      background: "#1a1240",
                      padding: "2px 8px",
                      borderRadius: 10,
                    }}
                  >
                    {a.project_name}
                  </span>
                )}
              </div>

              <div
                style={{
                  fontSize: 13,
                  color: "var(--text-main)",
                  marginBottom: 6,
                }}
              >
                {a.task}
              </div>

              {a.notes && (
                <div
                  style={{
                    fontSize: 11,
                    color: "#fc8181",
                    fontStyle: "italic",
                    marginBottom: 8,
                  }}
                >
                  Your note: {a.notes}
                </div>
              )}

              <input
                style={{
                  width: "100%",
                  background: "#1a1a2e",
                  border: "1px solid #2d2d4a",
                  borderRadius: 6,
                  padding: "6px 10px",
                  color: "var(--text-main)",
                  fontSize: 12,
                  marginBottom: 8,
                }}
                placeholder="Modify the request before resubmitting..."
                value={modifiedTask[a.approval_id] || ""}
                onChange={(e) =>
                  setModifiedTask((m) => ({
                    ...m,
                    [a.approval_id]: e.target.value,
                  }))
                }
              />

              <button
                onClick={() => resubmit(a.approval_id)}
                disabled={resubmitting[a.approval_id]}
                style={{
                  width: "100%",
                  padding: "8px 0",
                  borderRadius: 8,
                  background: "#2d2510",
                  color: "#f6ad55",
                  cursor: "pointer",
                  fontSize: 12,
                  fontWeight: 500,
                  outline: "1px solid #f6ad55",
                  border: "none",
                }}
              >
                {resubmitting[a.approval_id]
                  ? "⏳ Resubmitting..."
                  : "🔄 Resubmit with Modification"}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* ── DECIDED ─────────────────────────────────── */}
      {done.length > 0 && (
        <div>
          <div
            style={{
              fontSize: 11,
              fontWeight: 500,
              color: "#4a5568",
              marginBottom: 10,
              textTransform: "uppercase",
              letterSpacing: ".06em",
            }}
          >
            ✅ Decided ({done.length})
          </div>

          {done.map((a) => (
            <div
              key={a.approval_id}
              style={{
                background: "var(--bg-secondary)",
                border: "1px solid var(--border-color)",
                borderRadius: 10,
                padding: 14,
                marginBottom: 8,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  style={{
                    display: "flex",
                    gap: 8,
                    alignItems: "center",
                    marginBottom: 4,
                    flexWrap: "wrap",
                  }}
                >
                  <span
                    style={{
                      fontSize: 10,
                      color: "#4a5568",
                      textTransform: "uppercase",
                    }}
                  >
                    {a.agent}
                  </span>
                  <span style={{ fontSize: 10, color: "#4a5568" }}>
                    #{a.approval_id}
                  </span>
                  {a.project_name && (
                    <span
                      style={{
                        fontSize: 10,
                        color: "#7c6af7",
                        background: "#1a1240",
                        padding: "1px 6px",
                        borderRadius: 10,
                      }}
                    >
                      {a.project_name}
                    </span>
                  )}
                </div>
                <div
                  style={{
                    fontSize: 13,
                    color: "var(--text-muted)",
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}
                >
                  {a.task}
                </div>
                {a.notes && (
                  <div
                    style={{
                      fontSize: 11,
                      color: "#4a5568",
                      fontStyle: "italic",
                      marginTop: 2,
                    }}
                  >
                    Note: {a.notes}
                  </div>
                )}
              </div>
              <div
                style={{
                  display: "flex",
                  gap: 8,
                  alignItems: "center",
                  flexShrink: 0,
                  marginLeft: 12,
                }}
              >
                <span style={{ fontSize: 10, color: "#4a5568" }}>
                  {a.decided_at
                    ? new Date(a.decided_at).toLocaleTimeString("en-IN")
                    : ""}
                </span>
                <span
                  className={`badge ${
                    a.decision === "approve"
                      ? "badge-green"
                      : a.decision === "reject"
                        ? "badge-red"
                        : "badge-yellow"
                  }`}
                >
                  {a.decision?.toUpperCase()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── EMPTY STATE ──────────────────────────────── */}
      {pending.length === 0 && rejected.length === 0 && done.length === 0 && (
        <div className="card" style={{ textAlign: "center", padding: 40 }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>📭</div>
          <div style={{ color: "#4a5568", fontSize: 13 }}>
            No approvals yet — run agents to trigger requests
          </div>
        </div>
      )}
    </div>
  );
}
// ── KPI Dashboard ─────────────────────────────────────────────────────
function KPIs() {
  const [data, setData] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    Promise.all([
      fetch(`${API}/analytics/kpi`, { signal: controller.signal }).then((r) =>
        r.json(),
      ),
      fetch(`${API}/analytics/summary`, { signal: controller.signal }).then(
        (r) => r.json(),
      ),
    ])
      .then(([k, s]) => {
        setData(k);
        setSummary(s);
        setLoading(false);
      })
      .catch((err) => {
        // Ignore AbortErrors if we switch tabs, otherwise turn off loading
        if (err.name !== "AbortError") {
          console.error("API Error:", err);
          setLoading(false);
        }
      });

    // 🔴 THIS LINE IS CRITICAL: It cancels the request if you navigate away
    return () => controller.abort();
  }, []);

  if (loading) return <Loading />;

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">📊 KPI Dashboard</div>
          <div className="page-sub">
            Live company health metrics across all departments
          </div>
        </div>
        {data && (
          <span className="badge badge-purple">
            Health:{" "}
            {Math.round(
              (data.on_track?.length / Object.keys(data.kpis || {}).length) *
                100,
            )}
            %
          </span>
        )}
      </div>

      {data && (
        <div className="grid grid-2" style={{ marginBottom: 20 }}>
          <div className="card">
            <div className="card-title">All KPIs</div>
            {Object.entries(data.kpis || {}).map(([k, v]) => (
              <KpiBar
                key={k}
                name={k}
                value={v.current}
                target={v.target}
                unit={v.unit}
                isLower={k === "open_tickets" || k === "bugs_open"}
              />
            ))}
          </div>
          <div>
            <div className="card" style={{ marginBottom: 16 }}>
              <div className="card-title">On Track</div>
              {(data.on_track || []).map((k) => (
                <div
                  key={k}
                  style={{
                    fontSize: 12,
                    color: "var(--text-main)",
                    marginBottom: 4,
                  }}
                >
                  ✅ {k.replace(/_/g, " ")}
                </div>
              ))}
            </div>
            <div className="card">
              <div className="card-title">Needs Attention</div>
              {(data.needs_attention || []).map((k) => (
                <div
                  key={k}
                  style={{
                    fontSize: 12,
                    color: "var(--text-muted)",
                    marginBottom: 4,
                  }}
                >
                  ⚠️ {k.replace(/_/g, " ")}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {summary && (
        <div className="grid grid-3">
          <div className="card">
            <div className="card-title">
              🏆 {summary.today_wins || "Today's Wins"}
            </div>
            {(summary.wins || []).map((w, i) => (
              <div
                key={i}
                style={{
                  fontSize: 12,
                  color: "var(--text-main)",
                  marginBottom: 6,
                }}
              >
                + {w}
              </div>
            ))}
          </div>
          <div className="card">
            <div className="card-title">⚠️ Concerns</div>
            {(summary.concerns || []).map((c, i) => (
              <div
                key={i}
                style={{
                  fontSize: 12,
                  color: "var(--text-muted)",
                  marginBottom: 6,
                }}
              >
                - {c}
              </div>
            ))}
          </div>
          <div className="card">
            <div className="card-title">💡 Recommended Action</div>
            <div
              style={{
                fontSize: 12,
                color: "var(--text-muted)",
                lineHeight: 1.6,
              }}
            >
              {summary.recommended_action ||
                "Run analytics/summary for AI recommendations"}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
// ── Marketing Campaigns ─────────────────────────────────────────────
function Marketing() {
  const [tab, setTab] = useState("broadcast");
  const [numbers, setNumbers] = useState("+91AAAAAAAAAA\n+91XXXXXXXXXX");
  const [emails, setEmails] = useState("user1@email.com\nuser2@email.com");
  const [message, setMessage] = useState("");
  const [subject, setSubject] = useState("");
  const [campaign, setCampaign] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);

  const generateAIMessage = async (type) => {
    setAiLoading(true);
    try {
      const r = await fetch(
        `${API}/marketing/social?platform=WhatsApp&topic=${encodeURIComponent(type)}`,
      );
      const d = await r.json();
      if (type === "whatsapp") setMessage(d.content || "");
      else setMessage(d.content || "");
    } catch (_e) {
      /* empty */
    }
    setAiLoading(false);
  };

  const send = async () => {
    if (!message && !subject) return;
    setLoading(true);
    setResult(null);
    try {
      const endpoint =
        tab === "whatsapp"
          ? "/notify/broadcast/whatsapp"
          : "/notify/broadcast/email";

      const body =
        tab === "whatsapp"
          ? {
              numbers: numbers
                .split("\n")
                .map((n) => n.trim())
                .filter(Boolean),
              message,
              campaign_name: campaign,
            }
          : {
              emails: emails
                .split("\n")
                .map((e) => e.trim())
                .filter(Boolean),
              subject,
              body: message,
              campaign_name: campaign,
            };

      const r = await fetch(`${API}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const d = await r.json();
      setResult(d);
    } catch (e) {
      setResult({ error: e.message });
    }
    setLoading(false);
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">📣 Marketing</div>
          <div className="page-sub">
            Send campaigns via WhatsApp and Email to customers, leads, and
            investors
          </div>
        </div>
      </div>

      {/* tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        {[
          { id: "broadcast", label: "📢 Broadcast Campaign" },
          { id: "whatsapp", label: "📱 WhatsApp Only" },
          { id: "email", label: "📧 Email Only" },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className="action-btn"
            style={{
              borderColor: tab === t.id ? "#7c6af7" : "var(--border-color)",
              color: tab === t.id ? "#9f7aea" : "var(--text-muted)",
              background: tab === t.id ? "#1a1240" : "var(--bg-secondary)",
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-title" style={{ marginBottom: 12 }}>
            Compose Campaign
          </div>

          <div style={{ marginBottom: 10 }}>
            <div
              style={{
                fontSize: 11,
                color: "var(--text-muted)",
                marginBottom: 4,
              }}
            >
              Campaign Name
            </div>
            <input
              style={{
                width: "100%",
                background: "var(--bg-secondary)",
                border: "1px solid var(--border-color)",
                borderRadius: 6,
                padding: "7px 10px",
                color: "var(--text-main)",
                fontSize: 12,
              }}
              placeholder="e.g. May Product Update"
              value={campaign}
              onChange={(e) => setCampaign(e.target.value)}
            />
          </div>

          {tab !== "email" && (
            <div style={{ marginBottom: 10 }}>
              <div
                style={{
                  fontSize: 11,
                  color: "var(--text-muted)",
                  marginBottom: 4,
                }}
              >
                WhatsApp Numbers (one per line, include +91)
              </div>
              <textarea
                style={{
                  width: "100%",
                  height: 80,
                  background: "var(--bg-secondary)",
                  border: "1px solid var(--border-color)",
                  borderRadius: 6,
                  padding: "7px 10px",
                  color: "var(--text-main)",
                  fontSize: 12,
                  resize: "vertical",
                }}
                value={numbers}
                onChange={(e) => setNumbers(e.target.value)}
              />
            </div>
          )}

          {tab !== "whatsapp" && (
            <div style={{ marginBottom: 10 }}>
              <div
                style={{
                  fontSize: 11,
                  color: "var(--text-muted)",
                  marginBottom: 4,
                }}
              >
                Email Addresses (one per line)
              </div>
              <textarea
                style={{
                  width: "100%",
                  height: 80,
                  background: "var(--bg-secondary)",
                  border: "1px solid var(--border-color)",
                  borderRadius: 6,
                  padding: "7px 10px",
                  color: "var(--text-main)",
                  fontSize: 12,
                  resize: "vertical",
                }}
                value={emails}
                onChange={(e) => setEmails(e.target.value)}
              />
            </div>
          )}

          {tab === "email" && (
            <div style={{ marginBottom: 10 }}>
              <div
                style={{
                  fontSize: 11,
                  color: "var(--text-muted)",
                  marginBottom: 4,
                }}
              >
                Email Subject
              </div>
              <input
                style={{
                  width: "100%",
                  background: "var(--bg-secondary)",
                  border: "1px solid var(--border-color)",
                  borderRadius: 6,
                  padding: "7px 10px",
                  color: "var(--text-main)",
                  fontSize: 12,
                }}
                placeholder="Subject line"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              />
            </div>
          )}

          <div style={{ marginBottom: 10 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 4,
              }}
            >
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                Message
              </div>
              <button
                onClick={() =>
                  generateAIMessage(campaign || "OrgMind product update")
                }
                disabled={aiLoading}
                style={{
                  fontSize: 10,
                  color: "#9f7aea",
                  background: "none",
                  border: "1px solid #7c6af7",
                  borderRadius: 4,
                  padding: "2px 8px",
                  cursor: "pointer",
                }}
              >
                {aiLoading ? "..." : "✨ AI Write"}
              </button>
            </div>
            <textarea
              style={{
                width: "100%",
                height: 120,
                background: "var(--bg-secondary)",
                border: "1px solid var(--border-color)",
                borderRadius: 6,
                padding: "7px 10px",
                color: "var(--text-main)",
                fontSize: 12,
                resize: "vertical",
              }}
              placeholder="Type your message or click AI Write..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
          </div>

          <button
            className="btn btn-primary"
            style={{ width: "100%", padding: 12 }}
            onClick={send}
            disabled={loading || !message}
          >
            {loading
              ? "⏳ Sending..."
              : tab === "broadcast"
                ? "📢 Send WhatsApp + Email"
                : tab === "whatsapp"
                  ? "📱 Send WhatsApp"
                  : "📧 Send Email"}
          </button>
        </div>

        <div>
          {/* quick templates */}
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title" style={{ marginBottom: 10 }}>
              Quick Templates
            </div>
            {[
              {
                label: "🎉 Product Update",
                msg: "Hi! NexaCore has just launched new AI features for your business. OrgMind now automates 10 departments with 100% accuracy. Try it today! 🚀",
              },
              {
                label: "📅 Meeting Reminder",
                msg: "Reminder: Your meeting with NexaCore Technologies is scheduled. Please confirm your availability. We look forward to connecting!",
              },
              {
                label: "💼 Investment Opportunity",
                msg: "NexaCore Technologies is raising funds for AI-powered business automation. Strong pipeline, proven product. Contact us for pitch deck.",
              },
              {
                label: "🎯 Project Kickoff",
                msg: "Your project with NexaCore has officially started! Our team is fully deployed and working. Kickoff call scheduled within 24 hours.",
              },
            ].map((t) => (
              <div
                key={t.label}
                onClick={() => setMessage(t.msg)}
                style={{
                  padding: "8px 10px",
                  marginBottom: 6,
                  borderRadius: 6,
                  cursor: "pointer",
                  border: "1px solid var(--border-color)",
                  background: "var(--bg-secondary)",
                  fontSize: 12,
                  color: "var(--text-muted)",
                  transition: "all .15s",
                }}
                onMouseEnter={(e) => (e.target.style.borderColor = "#7c6af7")}
                onMouseLeave={(e) =>
                  (e.target.style.borderColor = "var(--border-color)")
                }
              >
                {t.label}
              </div>
            ))}
          </div>

          {/* result */}
          {result && !result.error && (
            <div className="card">
              <div className="card-title" style={{ marginBottom: 10 }}>
                Send Results
              </div>
              <div className="grid grid-3" style={{ marginBottom: 12 }}>
                {[
                  {
                    label: "Total",
                    value: result.total,
                    color: "var(--text-main)",
                  },
                  { label: "Sent", value: result.sent, color: "#48bb78" },
                  {
                    label: "Simulated",
                    value: result.simulated,
                    color: "#f6ad55",
                  },
                ].map((s) => (
                  <div
                    key={s.label}
                    style={{
                      textAlign: "center",
                      padding: "10px 0",
                      background: "var(--bg-secondary)",
                      borderRadius: 8,
                    }}
                  >
                    <div
                      style={{ fontSize: 22, fontWeight: 700, color: s.color }}
                    >
                      {s.value || 0}
                    </div>
                    <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
                      {s.label}
                    </div>
                  </div>
                ))}
              </div>
              {result.simulated > 0 && (
                <div
                  style={{
                    fontSize: 11,
                    color: "var(--text-muted)",
                    padding: "8px 10px",
                    background: "var(--bg-secondary)",
                    borderRadius: 6,
                  }}
                >
                  💡 Add Twilio + Gmail credentials to .env for real sending
                </div>
              )}
            </div>
          )}

          {result?.error && (
            <div className="card">
              <div style={{ color: "#fc8181", fontSize: 12 }}>
                Error: {result.error}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
//  ── New Project Launch ───────────────────────────────────────────────
function NewProject({ draft, setDraft }) {
  const selected = draft.selected;
  const selInv = draft.selInv;
  const selCands = draft.selCands;
  const phase = draft.phase;
  const result = draft.result;

  const setSelected = (v) => setDraft((d) => ({ ...d, selected: v }));
  const setSelInv = (v) => setDraft((d) => ({ ...d, selInv: v }));
  const setSelCands = (v) =>
    setDraft((d) => ({
      ...d,
      selCands: typeof v === "function" ? v(d.selCands) : v,
    }));
  const setPhase = (v) => setDraft((d) => ({ ...d, phase: v }));
  const setResult = (v) => setDraft((d) => ({ ...d, result: v }));

  // keep these as local (don't need to persist)
  const [projects, setProjects] = useState([]);
  const [investors, setInvestors] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [running, setRunning] = useState(false);
  const [launched, setLaunched] = useState([]);
  const [loadingCands, setLoadingCands] = useState(false);

  // eslint-disable-next-line no-unused-vars
  const stepDefs = [
    { n: 1, icon: "⚖️", label: "Legal — Law + project compliance" },
    { n: 2, icon: "👥", label: "HR — Candidate screening" },
    { n: 3, icon: "💰", label: "Finance — Project budget" },
    { n: 4, icon: "🎯", label: "Sales — Investor analysis" },
    { n: 5, icon: "⚙️", label: "Operations — Procurement" },
    { n: 6, icon: "📣", label: "Marketing — Announcement" },
    { n: 7, icon: "💻", label: "IT/Dev — Security audit" },
    { n: 8, icon: "🎫", label: "Support — Channel setup" },
    { n: 9, icon: "📊", label: "Analytics — KPI baseline" },
  ];

  const loadData = () => {
    fetch(`${API}/projects/list`)
      .then((r) => r.json())
      .then((d) => setProjects(d.projects || []));
    fetch(`${API}/ceo/projects`)
      .then((r) => r.json())
      .then((d) => setLaunched(d.projects || []));
  };

  useEffect(() => {
    loadData();
  }, [result]);

  // load investors when project selected
  const onSelectProject = async (p) => {
    setSelected(p);
    setSelInv(null);
    setSelCands([]);
    setPhase(2);
    const r = await fetch(`${API}/investors/top5`);
    const d = await r.json();
    setInvestors(d.top5_for_ceo || []);
  };

  // load candidates when moving to phase 3
  const onGoToCandidates = async () => {
    if (!selected) return;
    setPhase(3);
    setLoadingCands(true);
    setCandidates([]);

    try {
      const roles = selected.roles
        ? selected.roles
            .split(",")
            .map((r) => r.trim())
            .filter(Boolean)
        : ["Developer"];

      // fetch all roles in parallel — safer than sequential await in loop
      const results = await Promise.allSettled(
        roles.slice(0, 3).map((role) =>
          fetch(`${API}/hr/screen?role=${encodeURIComponent(role)}`)
            .then((r) => r.json())
            .then((d) =>
              (d.candidates || []).slice(0, 3).map((c) => ({
                ...c,
                role_needed: role,
              })),
            )
            .catch(() => []),
        ),
      );

      const allCands = results
        .filter((r) => r.status === "fulfilled")
        .flatMap((r) => r.value || []);

      // deduplicate by name
      const seen = new Set();
      const unique = allCands.filter((c) => {
        if (!c.name || seen.has(c.name)) return false;
        seen.add(c.name);
        return true;
      });

      setCandidates(unique.slice(0, 6));
    } catch (e) {
      console.error("Candidate load error:", e);
      setCandidates([]);
    }
    setLoadingCands(false);
  };

  const toggleCandidate = (c) => {
    setSelCands((prev) => {
      const exists = prev.find((x) => x.name === c.name);

      if (exists) {
        return prev.filter((x) => x.name !== c.name);
      }

      if (prev.length >= 3) return prev;

      return [...prev, c];
    });
  };

  const isProjectUsed = (p) =>
    launched.some((l) => l.project_name === p.name && l.client === p.client);
  const isInvUsed = (inv) =>
    launched.some((l) => l.selected_lead?.id === inv.id);

  const launch = async () => {
    if (!selected || running) return;
    setRunning(true);

    try {
      const r = await fetch(`${API}/ceo/new-project`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_name: selected.name,
          client: selected.client,
          value: parseInt(selected.value),
          lead_id: selInv?.id || "",
          roles_needed: selected.roles || "",
          selected_candidates: selCands,
          project_type: selected.type || "",
        }),
      });
      const d = await r.json();
      setResult(d);
      loadData();

      // ✅ reset to phase 1 after 3 seconds so CEO can start another project
      setTimeout(() => {
        setDraft({
          selected: null,
          selInv: null,
          selCands: [],
          phase: 1,
          result: null,
        });
      }, 4000);
    } catch (e) {
      setResult({ error: e.message });
    }
    setRunning(false);
  };

  // phase labels
  const phases = [
    "Select Project",
    "Choose Investor",
    "Select Candidates",
    "Confirm & Launch",
  ];

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">🚀 CEO — Start New Project</div>
          <div className="page-sub">
            4 steps: project → investor → candidates → launch
          </div>
        </div>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {phases.map((p, i) => (
            <div
              key={i}
              onClick={() => {
                if (!running && i < phase - 1) setPhase(i + 1);
              }}
              style={{
                padding: "4px 10px",
                borderRadius: 20,
                fontSize: 10,
                cursor: i < phase - 1 && !running ? "pointer" : "default",
                background:
                  phase > i + 1
                    ? "#0d2818"
                    : phase === i + 1
                      ? "#1a1240"
                      : "var(--bg-secondary)",
                border: `1px solid ${phase > i + 1 ? "#48bb78" : phase === i + 1 ? "#7c6af7" : "var(--border-color)"}`,
                color:
                  phase > i + 1
                    ? "#48bb78"
                    : phase === i + 1
                      ? "#9f7aea"
                      : "var(--text-muted)",
              }}
            >
              {phase > i + 1 ? "✓ " : ""}
              {i + 1}. {p}
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-2" style={{ marginBottom: 20 }}>
        {/* LEFT PANEL */}
        <div>
          {/* PHASE 1 — Project */}
          {phase === 1 && (
            <div className="card">
              <div className="card-title" style={{ marginBottom: 12 }}>
                Step 1 — Select Project
              </div>
              {projects.length === 0 && (
                <div
                  style={{
                    color: "var(--text-muted)",
                    fontSize: 13,
                    padding: 20,
                    textAlign: "center",
                  }}
                >
                  No projects available — sync Google Sheets or add projects
                </div>
              )}
              {projects.map((p) => (
                <div
                  key={p.id || p.name}
                  onClick={() => {
                    if (!isProjectUsed(p)) onSelectProject(p);
                  }}
                  style={{
                    padding: 12,
                    borderRadius: 8,
                    marginBottom: 8,
                    cursor: isProjectUsed(p) ? "not-allowed" : "pointer",
                    opacity: isProjectUsed(p) ? 0.5 : 1,
                    border: `1px solid ${selected?.id === p.id ? "#7c6af7" : "var(--border-color)"}`,
                    background:
                      selected?.id === p.id ? "#1a1240" : "var(--bg-secondary)",
                    position: "relative",
                    transition: "all .15s",
                  }}
                >
                  {isProjectUsed(p) && (
                    <span
                      style={{
                        position: "absolute",
                        top: 8,
                        right: 8,
                        fontSize: 9,
                        padding: "2px 6px",
                        borderRadius: 10,
                        background: "#2d2510",
                        color: "#f6ad55",
                      }}
                    >
                      Already launched
                    </span>
                  )}
                  <div
                    style={{ display: "flex", justifyContent: "space-between" }}
                  >
                    <div>
                      <div
                        style={{
                          fontSize: 13,
                          fontWeight: 500,
                          color: "var(--text-main)",
                        }}
                      >
                        {p.name}
                      </div>
                      <div
                        style={{
                          fontSize: 11,
                          color: "var(--text-muted)",
                          marginTop: 2,
                        }}
                      >
                        {p.client} · {p.type}
                      </div>
                      <div
                        style={{
                          fontSize: 11,
                          color: "var(--text-muted)",
                          marginTop: 2,
                        }}
                      >
                        {p.description}
                      </div>
                    </div>
                    <div
                      style={{
                        textAlign: "right",
                        flexShrink: 0,
                        marginLeft: 12,
                      }}
                    >
                      <div
                        style={{
                          fontSize: 13,
                          fontWeight: 600,
                          color: "#48bb78",
                        }}
                      >
                        ₹{parseInt(p.value || 0).toLocaleString()}
                      </div>
                      <div
                        style={{
                          fontSize: 10,
                          color: "var(--text-muted)",
                          marginTop: 2,
                        }}
                      >
                        {p.duration}
                      </div>
                    </div>
                  </div>
                  {p.roles && (
                    <div
                      style={{
                        marginTop: 6,
                        display: "flex",
                        flexWrap: "wrap",
                        gap: 4,
                      }}
                    >
                      {p.roles.split(",").map((r) => (
                        <span
                          key={r}
                          className="badge badge-purple"
                          style={{ fontSize: 9 }}
                        >
                          {r.trim()}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* PHASE 2 — Investor */}
          {phase === 2 && (
            <div className="card">
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  marginBottom: 16,
                }}
              >
                <button
                  onClick={() => setPhase(1)}
                  style={{
                    background: "none",
                    border: "none",
                    color: "var(--text-muted)",
                    cursor: "pointer",
                    fontSize: 18,
                  }}
                >
                  ←
                </button>
                <div className="card-title" style={{ marginBottom: 0 }}>
                  Step 2 — Choose Investor
                </div>
              </div>

              <div
                style={{
                  fontSize: 12,
                  color: "var(--text-muted)",
                  marginBottom: 12,
                  padding: "8px 10px",
                  background: "var(--bg-secondary)",
                  borderRadius: 6,
                }}
              >
                💡 Top 5 investors scored by AI for this project type. Select
                one or skip.
              </div>

              <div
                onClick={() => setSelInv(null)}
                style={{
                  padding: 10,
                  borderRadius: 8,
                  marginBottom: 8,
                  cursor: "pointer",
                  border: `1px solid ${!selInv ? "#7c6af7" : "var(--border-color)"}`,
                  background: !selInv ? "#1a1240" : "var(--bg-secondary)",
                }}
              >
                <div style={{ fontSize: 12, color: "var(--text-main)" }}>
                  🚫 No investor — self-funded project
                </div>
              </div>

              {investors.map((inv, i) => (
                <div
                  key={i}
                  onClick={() => {
                    if (!isInvUsed(inv)) {
                      setSelInv(inv);
                    }
                  }}
                  style={{
                    padding: 12,
                    borderRadius: 8,
                    marginBottom: 8,
                    cursor: isInvUsed(inv) ? "not-allowed" : "pointer",
                    opacity: isInvUsed(inv) ? 0.5 : 1,
                    border: `1px solid ${selInv?.id === inv.id ? "#48bb78" : "var(--border-color)"}`,
                    background:
                      selInv?.id === inv.id ? "#0d2818" : "var(--bg-secondary)",
                    position: "relative",
                    transition: "all .15s",
                  }}
                >
                  {isInvUsed(inv) && (
                    <span
                      style={{
                        position: "absolute",
                        top: 6,
                        right: 8,
                        fontSize: 9,
                        padding: "2px 6px",
                        borderRadius: 10,
                        background: "#0d2818",
                        color: "#48bb78",
                      }}
                    >
                      Already chosen
                    </span>
                  )}
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                    }}
                  >
                    <div>
                      <div
                        style={{
                          fontSize: 13,
                          fontWeight: 500,
                          color: "var(--text-main)",
                        }}
                      >
                        {inv.company}
                      </div>
                      <div
                        style={{
                          fontSize: 11,
                          color: "var(--text-muted)",
                          marginTop: 2,
                        }}
                      >
                        {inv.contact_name} · {inv.designation}
                      </div>
                      <div
                        style={{
                          fontSize: 11,
                          color: "var(--text-muted)",
                          marginTop: 2,
                        }}
                      >
                        {inv.industry} · {inv.city || inv.location || ""}
                      </div>
                    </div>
                    <div
                      style={{
                        textAlign: "right",
                        flexShrink: 0,
                        marginLeft: 12,
                      }}
                    >
                      <div
                        style={{
                          fontSize: 13,
                          fontWeight: 600,
                          color: "#48bb78",
                        }}
                      >
                        ₹{parseInt(inv.budget_inr || 0).toLocaleString()}
                      </div>
                      <span
                        className={`badge ${
                          inv.interest_level === "high"
                            ? "badge-green"
                            : inv.interest_level === "medium"
                              ? "badge-yellow"
                              : "badge-red"
                        }`}
                        style={{ marginTop: 4, display: "block" }}
                      >
                        {inv.interest_level} · {inv.score}/100
                      </span>
                    </div>
                  </div>
                </div>
              ))}

              <button
                className="btn btn-primary"
                style={{ width: "100%", marginTop: 8, padding: 12 }}
                onClick={onGoToCandidates}
              >
                Next → Select Candidates
              </button>
            </div>
          )}

          {/* PHASE 3 — Candidates */}
          {phase === 3 && (
            <div className="card">
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  marginBottom: 12,
                }}
              >
                <button
                  onClick={() => setPhase(2)}
                  style={{
                    background: "none",
                    border: "none",
                    color: "var(--text-muted)",
                    cursor: "pointer",
                    fontSize: 18,
                  }}
                >
                  ←
                </button>
                <div className="card-title" style={{ marginBottom: 0 }}>
                  Step 3 — Select Candidates (max 3)
                </div>
              </div>

              <div
                style={{
                  fontSize: 12,
                  color: "var(--text-muted)",
                  marginBottom: 12,
                  padding: "8px 10px",
                  background: "var(--bg-secondary)",
                  borderRadius: 6,
                }}
              >
                💡 Top candidates for roles:{" "}
                <strong style={{ color: "var(--text-main)" }}>
                  {selected?.roles || "All roles"}
                </strong>
                . Select up to 3 for interview.
              </div>

              {loadingCands && (
                <div className="loading">
                  <div className="spinner" />
                  Screening candidates for project roles...
                </div>
              )}

              {!loadingCands && candidates.length === 0 && (
                <div
                  style={{
                    fontSize: 12,
                    color: "var(--text-muted)",
                    padding: 20,
                    textAlign: "center",
                    background: "var(--bg-secondary)",
                    borderRadius: 8,
                  }}
                >
                  No candidates found for roles: {selected?.roles || "any"}
                  <br />
                  <span
                    style={{ fontSize: 11, marginTop: 4, display: "block" }}
                  >
                    Add candidates via Google Form → Sync Sheets → try again
                  </span>
                </div>
              )}

              {!loadingCands &&
                candidates.map((c, i) => {
                  // safety check — skip malformed candidates
                  if (!c || !c.name) return null;
                  const isSelected = selCands.find((x) => x.name === c.name);
                  return (
                    <div
                      key={i}
                      onClick={() => toggleCandidate(c)}
                      style={{
                        padding: 12,
                        borderRadius: 8,
                        marginBottom: 8,
                        cursor: "pointer",
                        border: `1px solid ${isSelected ? "#48bb78" : "var(--border-color)"}`,
                        background: isSelected
                          ? "#0d2818"
                          : "var(--bg-secondary)",
                        transition: "all .15s",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "flex-start",
                        }}
                      >
                        <div style={{ flex: 1 }}>
                          <div
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: 6,
                            }}
                          >
                            <div
                              style={{
                                fontSize: 13,
                                fontWeight: 500,
                                color: "var(--text-main)",
                              }}
                            >
                              {c.name}
                            </div>
                            {isSelected && (
                              <span
                                style={{
                                  fontSize: 9,
                                  padding: "1px 6px",
                                  borderRadius: 10,
                                  background: "#48bb78",
                                  color: "white",
                                }}
                              >
                                Selected
                              </span>
                            )}
                          </div>
                          <div
                            style={{
                              fontSize: 11,
                              color: "var(--text-muted)",
                              marginTop: 2,
                            }}
                          >
                            {c.role || c.role_applied} · {c.experience} ·
                            {c.previous_company || ""}
                          </div>
                          <div
                            style={{
                              fontSize: 11,
                              color: "var(--text-muted)",
                              marginTop: 2,
                            }}
                          >
                            {c.expected_salary} · {c.notice_period} ·{" "}
                            {c.location}
                          </div>
                          <div
                            style={{
                              fontSize: 10,
                              color: "var(--text-muted)",
                              marginTop: 2,
                            }}
                          >
                            📧 {c.email}
                          </div>
                          <div
                            style={{
                              display: "flex",
                              gap: 4,
                              marginTop: 4,
                              flexWrap: "wrap",
                            }}
                          >
                            {(c.skills || []).slice(0, 4).map((s) => (
                              <span
                                key={s}
                                className="badge badge-purple"
                                style={{ fontSize: 9 }}
                              >
                                {s}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div
                          style={{
                            textAlign: "right",
                            flexShrink: 0,
                            marginLeft: 8,
                          }}
                        >
                          <div
                            style={{
                              fontSize: 18,
                              fontWeight: 700,
                              color:
                                c.score >= 75
                                  ? "#48bb78"
                                  : c.score >= 50
                                    ? "#f6ad55"
                                    : "#fc8181",
                            }}
                          >
                            {c.score}/100
                          </div>
                          <div
                            style={{
                              fontSize: 10,
                              color: "var(--text-muted)",
                              marginTop: 2,
                            }}
                          >
                            {c.role_needed || c.role_applied}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}

              {selCands.length > 0 && (
                <div
                  style={{
                    padding: "8px 10px",
                    marginBottom: 8,
                    borderRadius: 6,
                    background: "#0d2818",
                    border: "1px solid #48bb78",
                    fontSize: 11,
                    color: "#48bb78",
                  }}
                >
                  ✅ {selCands.length} candidate{selCands.length > 1 ? "s" : ""}{" "}
                  selected:
                  {selCands.map((c) => ` ${c.name}`).join(",")}
                </div>
              )}

              <button
                className="btn btn-primary"
                style={{ width: "100%", marginTop: 8, padding: 12 }}
                onClick={() => setPhase(4)}
              >
                Next → Confirm & Launch
              </button>
            </div>
          )}

          {/* PHASE 4 — Confirm */}
          {phase === 4 && (
            <div className="card">
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  marginBottom: 16,
                }}
              >
                {!running && (
                  <button
                    onClick={() => setPhase(3)}
                    style={{
                      background: "none",
                      border: "none",
                      color: "var(--text-muted)",
                      cursor: "pointer",
                      fontSize: 18,
                    }}
                  >
                    ←
                  </button>
                )}
                <div className="card-title" style={{ marginBottom: 0 }}>
                  Step 4 — Confirm & Launch
                </div>
              </div>

              {[
                ["Project", selected?.name],
                ["Client", selected?.client],
                [
                  "Value",
                  `₹${parseInt(selected?.value || 0).toLocaleString()}`,
                ],
                ["Type", selected?.type || ""],
                ["Duration", selected?.duration || ""],
                [
                  "Investor",
                  selInv
                    ? `${selInv.company} (${selInv.score}/100)`
                    : "Self-funded",
                ],
                [
                  "Candidates",
                  selCands.length > 0
                    ? selCands.map((c) => c.name).join(", ")
                    : "None selected",
                ],
                ["Roles", selected?.roles || "As per project"],
              ].map(([k, v]) => (
                <div
                  key={k}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    padding: "7px 0",
                    borderBottom: "1px solid var(--border-color)",
                    fontSize: 12,
                  }}
                >
                  <span style={{ color: "var(--text-muted)" }}>{k}</span>
                  <span
                    style={{
                      color: "var(--text-main)",
                      fontWeight: 500,
                      maxWidth: "60%",
                      textAlign: "right",
                    }}
                  >
                    {v}
                  </span>
                </div>
              ))}

              <button
                className="btn btn-primary"
                style={{
                  width: "100%",
                  padding: 14,
                  fontSize: 14,
                  marginTop: 16,
                }}
                onClick={launch}
                disabled={!selected || running}
              >
                {running
                  ? "⏳ All Agents Working..."
                  : `🚀 Launch — ${selected?.client}`}
              </button>

              {result && !result.error && (
                <div
                  style={{
                    marginTop: 12,
                    padding: "12px 14px",
                    background: "#0d2818",
                    borderRadius: 8,
                    border: "1px solid #48bb78",
                    fontSize: 13,
                    color: "#48bb78",
                    textAlign: "center",
                  }}
                >
                  ✅ {result.project_name} launched successfully!
                  <div
                    style={{
                      fontSize: 11,
                      color: "var(--text-muted)",
                      marginTop: 4,
                    }}
                  >
                    Resetting in 4 seconds... Check Project Approvals and
                    Approval Inbox.
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* RIGHT — Agent Deployment */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: 12 }}>
            Agent Deployment
          </div>

          {!result && (
            <div
              style={{
                color: "var(--text-muted)",
                fontSize: 13,
                padding: "40px 0",
                textAlign: "center",
              }}
            >
              Complete all 4 steps and click Launch
            </div>
          )}

          {running && !result && (
            <div className="loading">
              <div className="spinner" />
              All 9 agents working...
            </div>
          )}

          {result &&
            !result.error &&
            (result.steps || []).map((s, i) => {
              // safety — skip malformed steps
              if (!s || typeof s !== "object") return null;
              const stepName =
                typeof s.step === "string" ? s.step : "Step " + (i + 1);
              const isCompleted = s.status === "completed";
              const onTime = s.on_time !== false;

              return (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: 10,
                    marginBottom: 8,
                    padding: "8px 12px",
                    borderRadius: 8,
                    background: isCompleted
                      ? onTime
                        ? "#0a1f0a"
                        : "#1f1200"
                      : "#1f0a0a",
                    border: `1px solid ${isCompleted ? (onTime ? "#48bb78" : "#f6ad55") : "#fc8181"}`,
                  }}
                >
                  <div
                    style={{
                      width: 22,
                      height: 22,
                      borderRadius: "50%",
                      flexShrink: 0,
                      background: isCompleted
                        ? onTime
                          ? "#48bb78"
                          : "#f6ad55"
                        : "#fc8181",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 10,
                      color: "white",
                      fontWeight: 700,
                    }}
                  >
                    {isCompleted ? "✓" : i + 1}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{
                        fontSize: 12,
                        color: "var(--text-main)",
                        fontWeight: 500,
                      }}
                    >
                      {stepName}
                    </div>
                    <div
                      style={{
                        fontSize: 11,
                        color: "var(--text-muted)",
                        marginTop: 3,
                        lineHeight: 1.4,
                      }}
                    >
                      {s.result_summary || s.error || "Completed"}
                    </div>
                    <div
                      style={{
                        fontSize: 10,
                        color: "var(--text-muted)",
                        marginTop: 2,
                      }}
                    >
                      {s.duration_s ? `${s.duration_s}s` : ""}
                      {s.duration_s && s.deadline ? " · " : ""}
                      {s.deadline
                        ? `Deadline: ${new Date(s.deadline).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" })}`
                        : ""}
                    </div>
                  </div>
                  <span
                    className={`badge ${!isCompleted ? "badge-red" : onTime ? "badge-green" : "badge-yellow"}`}
                    style={{ flexShrink: 0 }}
                  >
                    {!isCompleted ? "Failed" : onTime ? "✓ On Time" : "Delayed"}
                  </span>
                </div>
              );
            })}
          {result && !result.error && (
            <div
              style={{
                marginTop: 8,
                padding: "10px 12px",
                background: "#0a1f0a",
                borderRadius: 8,
                border: "1px solid #48bb78",
                fontSize: 12,
                color: "var(--text-muted)",
              }}
            >
              ✅{" "}
              <strong style={{ color: "#48bb78" }}>
                {result.on_time_steps}/{result.total_steps} on time
              </strong>{" "}
              · {result.total_time_s}s · Check{" "}
              <strong style={{ color: "var(--text-main)" }}>
                Project Approvals
              </strong>{" "}
              for candidate/investor selection
            </div>
          )}
        </div>
      </div>

      {/* Active Projects */}
      {launched.length > 0 && (
        <div className="card">
          <div className="card-title" style={{ marginBottom: 12 }}>
            Active Projects
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>Project</th>
                <th>Client</th>
                <th>Value</th>
                <th>Type</th>
                <th>Investor</th>
                <th>Steps</th>
                <th>Status</th>
                <th>Started</th>
              </tr>
            </thead>
            <tbody>
              {launched.map((p, i) => (
                <tr key={i}>
                  <td style={{ color: "var(--text-main)", fontWeight: 500 }}>
                    {p.project_name}
                  </td>
                  <td>{p.client}</td>
                  <td style={{ color: "#48bb78" }}>
                    ₹{(p.value || 0).toLocaleString()}
                  </td>
                  <td style={{ color: "var(--text-muted)", fontSize: 11 }}>
                    {p.project_type || "General"}
                  </td>
                  <td style={{ fontSize: 11 }}>
                    {p.selected_lead?.company || "Self-funded"}
                    {p.selected_lead && (
                      <span
                        className="badge badge-green"
                        style={{ marginLeft: 4, fontSize: 9 }}
                      >
                        chosen
                      </span>
                    )}
                  </td>
                  <td>{p.total_steps}/9</td>
                  <td>
                    <span
                      className={`badge ${
                        p.status === "completed"
                          ? "badge-blue"
                          : p.status === "active"
                            ? "badge-green"
                            : "badge-yellow"
                      }`}
                    >
                      {p.status || "pending"}
                    </span>
                  </td>
                  <td style={{ color: "var(--text-muted)", fontSize: 11 }}>
                    {new Date(p.started_at).toLocaleDateString("en-IN")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
//  ── IT Code Fixer ───────────────────────────────────────────────────
const SAMPLE_BUGS = {
  python: `# Buggy Python code
def calculate_salary(employee_list):
    total = 0
    for emp in employee_list
        if emp['salary'] > 0
            total =+ emp['salary']  # wrong operator
    return total / len(employee_list)  # division by zero risk

employees = [
    {'name': 'Rahul', 'salary': 55000},
    {'name': 'Anjali', 'salary': 0},
    {'name': 'Karan', 'salary': -1000}  # negative salary
]
print(calculate_salary([]))  # empty list crash
`,
  javascript: `// Buggy JavaScript
function fetchLeadData(leadId) {
    const leads = null
    const lead = leads[leadId]  // null reference
    
    if (lead.status = 'qualified') {  // assignment not comparison
        console.log('Lead value: ' + lead.budget * 1.18)
        return lead
    }
}

fetchLeadData(undefined)  // undefined key
`,
  java: `// Buggy Java
public class InvoiceCalculator {
    public static double calculateTotal(int[] amounts) {
        int total = 0;
        for (int i = 0; i <= amounts.length; i++) {  // off by one
            total += amounts[i];
        }
        return total / amounts.length;  // integer division
    }
    
    public static void main(String[] args) {
        int[] invoices = {};
        System.out.println(calculateTotal(invoices));  // empty array
    }
}
`,
};

function CodeFixer() {
  const [code, setCode] = useState(SAMPLE_BUGS.python);
  const [filename, setFilename] = useState("salary_calculator.py");
  const [language, setLanguage] = useState("python");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState("fix");

  const loadSample = (lang) => {
    setLanguage(lang);
    setCode(SAMPLE_BUGS[lang]);
    setFilename(
      lang === "python"
        ? "salary_calculator.py"
        : lang === "javascript"
          ? "leads.js"
          : "InvoiceCalculator.java",
    );
    setResult(null);
  };

  const run = async () => {
    if (!code.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const r = await fetch(`${API}/it/${tab}-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, filename, language }),
      });
      const d = await r.json();
      setResult(d);
    } catch (e) {
      setResult({ error: e.message });
    }
    setLoading(false);
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">🔧 IT Code Fixer</div>
          <div className="page-sub">
            Upload or paste code — AI finds bugs and fixes them instantly
          </div>
        </div>
      </div>

      <div className="grid grid-2" style={{ marginBottom: 16 }}>
        <div className="card">
          <div
            style={{
              display: "flex",
              gap: 8,
              marginBottom: 12,
              flexWrap: "wrap",
            }}
          >
            <div style={{ display: "flex", gap: 6 }}>
              {["python", "javascript", "java"].map((l) => (
                <button
                  key={l}
                  className="action-btn"
                  style={{
                    borderColor: language === l ? "#7c6af7" : "#2d2d4a",
                    color: language === l ? "#7c6af7" : "#a0aec0",
                  }}
                  onClick={() => loadSample(l)}
                >
                  {l}
                </button>
              ))}
            </div>
            <div style={{ display: "flex", gap: 6, marginLeft: "auto" }}>
              {["fix", "review"].map((t) => (
                <button
                  key={t}
                  className="action-btn"
                  style={{
                    borderColor: tab === t ? "#48bb78" : "#2d2d4a",
                    color: tab === t ? "#48bb78" : "#a0aec0",
                  }}
                  onClick={() => setTab(t)}
                >
                  {t === "fix" ? "🔧 Fix Bugs" : "🔍 Review"}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: 8 }}>
            <input
              style={{
                width: "100%",
                background: "#1a1a2e",
                border: "1px solid #2d2d4a",
                borderRadius: 6,
                padding: "6px 10px",
                color: "#e2e8f0",
                fontSize: 12,
              }}
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              placeholder="filename.py"
            />
          </div>

          <textarea
            style={{
              width: "100%",
              height: 280,
              background: "#080810",
              border: "1px solid #2d2d4a",
              borderRadius: 8,
              padding: 12,
              color: "#68d391",
              fontSize: 12,
              fontFamily: "Courier New, monospace",
              resize: "vertical",
            }}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your code here or select a sample above..."
          />

          <button
            className="btn btn-primary"
            style={{ width: "100%", marginTop: 10 }}
            onClick={run}
            disabled={loading}
          >
            {loading
              ? "⏳ AI Analyzing..."
              : tab === "fix"
                ? "🔧 Fix My Code"
                : "🔍 Review Code"}
          </button>
        </div>

        <div>
          {loading && (
            <div className="card">
              <div className="loading">
                <div className="spinner" />
                AI reading your code...
              </div>
            </div>
          )}

          {result && !result.error && tab === "fix" && (
            <div>
              <div className="card" style={{ marginBottom: 12 }}>
                <div className="card-title">Analysis Result</div>
                <div
                  style={{
                    display: "flex",
                    gap: 8,
                    flexWrap: "wrap",
                    margin: "10px 0",
                  }}
                >
                  <span
                    className={`badge ${result.has_errors ? "badge-red" : "badge-green"}`}
                  >
                    {result.has_errors
                      ? `${result.errors_found?.length} Errors Found`
                      : "No Errors"}
                  </span>
                  <span className="badge badge-blue">{result.language}</span>
                  <span className="badge badge-purple">
                    {result.original_lines} lines
                  </span>
                </div>
                <div
                  style={{ fontSize: 13, color: "#a0aec0", lineHeight: 1.6 }}
                >
                  {result.explanation}
                </div>
              </div>

              {result.errors_found?.length > 0 && (
                <div className="card" style={{ marginBottom: 12 }}>
                  <div className="card-title">Errors Found</div>
                  {result.errors_found.map((e, i) => (
                    <div
                      key={i}
                      style={{
                        display: "flex",
                        gap: 8,
                        marginBottom: 8,
                        padding: "6px 8px",
                        background: "#1a0a0a",
                        borderRadius: 6,
                        border: "1px solid #2d1515",
                      }}
                    >
                      <span
                        className={`badge ${e.severity === "high" ? "badge-red" : "badge-yellow"}`}
                      >
                        L{e.line}
                      </span>
                      <span style={{ fontSize: 12, color: "#a0aec0" }}>
                        {e.error}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {result.changes_made?.length > 0 && (
                <div className="card" style={{ marginBottom: 12 }}>
                  <div className="card-title">Changes Made</div>
                  {result.changes_made.map((c, i) => (
                    <div
                      key={i}
                      style={{
                        fontSize: 12,
                        color: "#68d391",
                        marginBottom: 4,
                      }}
                    >
                      ✅ {c}
                    </div>
                  ))}
                </div>
              )}

              <div className="card">
                <div className="card-title" style={{ marginBottom: 8 }}>
                  Fixed Code
                </div>
                <div className="result-panel" style={{ maxHeight: 300 }}>
                  {result.fixed_code}
                </div>
              </div>
            </div>
          )}

          {result && !result.error && tab === "review" && (
            <div>
              <div className="card" style={{ marginBottom: 12 }}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div className="card-title">Code Quality</div>
                  <span
                    style={{
                      fontSize: 28,
                      fontWeight: 700,
                      color:
                        result.quality_score >= 70
                          ? "#48bb78"
                          : result.quality_score >= 40
                            ? "#f6ad55"
                            : "#fc8181",
                    }}
                  >
                    {result.quality_score}/100
                  </span>
                </div>
                <div style={{ fontSize: 12, color: "#a0aec0", marginTop: 8 }}>
                  {result.summary}
                </div>
              </div>
              {result.security_issues?.length > 0 && (
                <div className="card" style={{ marginBottom: 12 }}>
                  <div className="card-title">Security Issues</div>
                  {result.security_issues.map((s, i) => (
                    <div
                      key={i}
                      style={{
                        fontSize: 12,
                        color: "#fc8181",
                        marginBottom: 4,
                      }}
                    >
                      🔴 {s}
                    </div>
                  ))}
                </div>
              )}
              {result.suggestions?.length > 0 && (
                <div className="card">
                  <div className="card-title">Suggestions</div>
                  {result.suggestions.map((s, i) => (
                    <div
                      key={i}
                      style={{
                        fontSize: 12,
                        color: "#68d391",
                        marginBottom: 4,
                      }}
                    >
                      💡 {s}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {result?.error && (
            <div className="card">
              <div style={{ color: "#fc8181", fontSize: 13 }}>
                Error: {result.error}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState([
    { role: "bot", text: "👋 Hi! I'm OrgMind's support assistant." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const q = input.trim();
    setInput("");
    setMsgs((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const r = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, session_id: "widget" }),
      });
      const d = await r.json();
      setMsgs((m) => [
        ...m,
        {
          role: "bot",
          text: d.response,
          blocked: d.blocked,
        },
      ]);
    } catch (e) {
      setMsgs((m) => [
        ...m,
        {
          role: "bot",
          text: "Sorry, I'm having trouble connecting. Please try again.",
        },
      ]);
    }
    setLoading(false);
  };

  return (
    <>
      {/* floating button */}
      <div
        onClick={() => setOpen(!open)}
        style={{
          position: "fixed",
          bottom: 24,
          right: 24,
          width: 52,
          height: 52,
          borderRadius: "50%",
          background: "linear-gradient(135deg,#7c6af7,#06b6d4)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          boxShadow: "0 4px 20px rgba(124,106,247,0.4)",
          fontSize: 22,
          zIndex: 1000,
          transition: "transform .2s",
        }}
      >
        {open ? "✕" : "💬"}
      </div>

      {/* chat window */}
      {open && (
        <div
          style={{
            position: "fixed",
            bottom: 88,
            right: 24,
            width: 340,
            height: 480,
            background: "#0d0d1a",
            border: "1px solid #2d2d4a",
            borderRadius: 16,
            display: "flex",
            flexDirection: "column",
            boxShadow: "0 8px 40px rgba(0,0,0,0.6)",
            zIndex: 999,
          }}
        >
          {/* header */}
          <div
            style={{
              padding: "12px 16px",
              background: "linear-gradient(135deg,#7c6af7,#06b6d4)",
              borderRadius: "16px 16px 0 0",
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            <div style={{ fontSize: 24 }}>🤖</div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 600, color: "white" }}>
                OrgMind Assistant
              </div>
              <div style={{ fontSize: 10, color: "rgba(255,255,255,0.8)" }}>
                <span
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: "50%",
                    background: "#4ade80",
                    display: "inline-block",
                    marginRight: 4,
                  }}
                />
                Online — Ask me anything
              </div>
            </div>
          </div>

          {/* messages */}
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: 12,
              display: "flex",
              flexDirection: "column",
              gap: 8,
            }}
          >
            {msgs.map((m, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: m.role === "user" ? "flex-end" : "flex-start",
                }}
              >
                <div
                  style={{
                    maxWidth: "80%",
                    padding: "8px 12px",
                    borderRadius:
                      m.role === "user"
                        ? "12px 12px 2px 12px"
                        : "12px 12px 12px 2px",
                    background:
                      m.role === "user"
                        ? "linear-gradient(135deg,#7c6af7,#06b6d4)"
                        : m.blocked
                          ? "#2d1515"
                          : "#1a1a2e",
                    border: m.blocked ? "1px solid #fc8181" : "none",
                    fontSize: 12,
                    color: "#e2e8f0",
                    lineHeight: 1.5,
                  }}
                >
                  {m.blocked && (
                    <div
                      style={{
                        fontSize: 10,
                        color: "#fc8181",
                        marginBottom: 4,
                      }}
                    >
                      🔒 Confidential
                    </div>
                  )}
                  {m.text}
                </div>
              </div>
            ))}
            {loading && (
              <div
                style={{
                  display: "flex",
                  gap: 4,
                  padding: "8px 12px",
                  background: "#1a1a2e",
                  borderRadius: 12,
                  width: "fit-content",
                }}
              >
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    style={{
                      width: 6,
                      height: 6,
                      borderRadius: "50%",
                      background: "#7c6af7",
                      animation: `bounce .8s ${i * 0.15}s infinite`,
                    }}
                  />
                ))}
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* input */}
          <div
            style={{
              padding: "8px 12px",
              borderTop: "1px solid #1e1e3a",
              display: "flex",
              gap: 8,
              alignItems: "center",
            }}
          >
            <input
              style={{
                flex: 1,
                background: "#1a1a2e",
                border: "1px solid #2d2d4a",
                borderRadius: 20,
                padding: "8px 14px",
                color: "#e2e8f0",
                fontSize: 12,
                outline: "none",
              }}
              placeholder="Ask about OrgMind..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
            />
            <button
              onClick={send}
              disabled={loading || !input.trim()}
              style={{
                width: 34,
                height: 34,
                borderRadius: "50%",
                background: "linear-gradient(135deg,#7c6af7,#06b6d4)",
                border: "none",
                color: "white",
                cursor: "pointer",
                fontSize: 14,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              ➤
            </button>
          </div>
        </div>
      )}

      <style>{`
        @keyframes bounce {
          0%,80%,100% { transform:scale(0.6); opacity:.4 }
          40% { transform:scale(1); opacity:1 }
        }
      `}</style>
    </>
  );
}
//  ── Project Report ───────────────────────────────────────────────────
function ProjectReport() {
  const [projects, setProjects] = useState([]);
  const [selected, setSelected] = useState("");
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API}/ceo/projects`)
      .then((r) => r.json())
      .then((d) => setProjects(d.projects || []));
  }, []);

  const loadReport = async (name) => {
    setSelected(name);
    setLoading(true);
    setReport(null);
    const r = await fetch(`${API}/project/report/${encodeURIComponent(name)}`);
    const d = await r.json();
    setReport(d);
    setLoading(false);
  };

  const deptIcons = {
    legal: "⚖️",
    hr: "👥",
    finance: "💰",
    sales: "🎯",
    operations: "⚙️",
    marketing: "📣",
    it: "💻",
    support: "🎫",
    analytics: "📊",
    admin: "🏢",
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <div className="page-title">📋 Project Report</div>
          <div className="page-sub">
            Complete professional report — what every agent did for each project
          </div>
        </div>
        {report && (
          <button
            onClick={() => window.print()}
            style={{
              padding: "8px 14px",
              borderRadius: 8,
              background: "#1a1240",
              border: "1px solid #7c6af7",
              color: "#9f7aea",
              cursor: "pointer",
              fontSize: 12,
            }}
          >
            🖨️ Print / Save PDF
          </button>
        )}
      </div>

      {/* Project selector */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-title" style={{ marginBottom: 10 }}>
          Select Project
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {projects.map((p, i) => (
            <button
              key={i}
              onClick={() => loadReport(p.project_name)}
              style={{
                padding: "7px 14px",
                borderRadius: 20,
                fontSize: 12,
                cursor: "pointer",
                border: "1px solid var(--border-color)",
                background:
                  selected === p.project_name
                    ? "#1a1240"
                    : "var(--bg-secondary)",
                color:
                  selected === p.project_name ? "#9f7aea" : "var(--text-muted)",
                borderColor:
                  selected === p.project_name
                    ? "#7c6af7"
                    : "var(--border-color)",
              }}
            >
              {p.project_name}
              <span
                className={`badge ${
                  p.status === "completed"
                    ? "badge-blue"
                    : p.status === "active"
                      ? "badge-green"
                      : "badge-yellow"
                }`}
                style={{ marginLeft: 6, fontSize: 9 }}
              >
                {p.status || "pending"}
              </span>
            </button>
          ))}
        </div>
      </div>

      {loading && <Loading />}

      {report && !report.error && (
        <div id="project-report">
          {/* Header */}
          <div
            style={{
              background: "linear-gradient(135deg,#1a1240,#0a1f0a)",
              border: "1px solid #7c6af7",
              borderRadius: 12,
              padding: "24px 28px",
              marginBottom: 16,
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
              }}
            >
              <div>
                <div
                  style={{
                    fontSize: 11,
                    color: "#9f7aea",
                    textTransform: "uppercase",
                    letterSpacing: ".1em",
                    marginBottom: 6,
                  }}
                >
                  Project Report — NexaCore Technologies Pvt Ltd
                </div>
                <div
                  style={{
                    fontSize: 22,
                    fontWeight: 500,
                    color: "var(--text-main)",
                    marginBottom: 4,
                  }}
                >
                  {report.project_name}
                </div>
                <div style={{ fontSize: 14, color: "var(--text-muted)" }}>
                  Client: {report.client}
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div
                  style={{ fontSize: 28, fontWeight: 700, color: "#48bb78" }}
                >
                  ₹{(report.value || 0).toLocaleString()}
                </div>
                <span
                  className={`badge ${
                    report.status === "completed"
                      ? "badge-blue"
                      : report.status === "active"
                        ? "badge-green"
                        : "badge-yellow"
                  }`}
                  style={{ fontSize: 12, padding: "4px 12px" }}
                >
                  {(report.status || "pending").toUpperCase()}
                </span>
              </div>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(4,1fr)",
                gap: 12,
                marginTop: 20,
              }}
            >
              {[
                {
                  label: "Started",
                  value: report.started_at
                    ? new Date(report.started_at).toLocaleDateString("en-IN")
                    : "—",
                },
                {
                  label: "Completed",
                  value: report.completed_at
                    ? new Date(report.completed_at).toLocaleDateString("en-IN")
                    : "In Progress",
                },
                { label: "Total Time", value: `${report.total_time_s || 0}s` },
                {
                  label: "Steps On Time",
                  value: `${report.on_time_steps || 0}/${report.total_steps || 0}`,
                },
              ].map((item) => (
                <div
                  key={item.label}
                  style={{
                    background: "rgba(0,0,0,0.3)",
                    borderRadius: 8,
                    padding: "10px 14px",
                  }}
                >
                  <div
                    style={{
                      fontSize: 10,
                      color: "#4a5568",
                      textTransform: "uppercase",
                      marginBottom: 4,
                    }}
                  >
                    {item.label}
                  </div>
                  <div
                    style={{
                      fontSize: 14,
                      fontWeight: 500,
                      color: "var(--text-main)",
                    }}
                  >
                    {item.value}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-2" style={{ marginBottom: 16 }}>
            {/* Selected Candidate */}
            {/* Selected Candidates — supports multiple */}
            <div className="card">
              <div className="card-title" style={{ marginBottom: 12 }}>
                👥 Selected Candidate(s)
              </div>
              {report.selected_candidates &&
              report.selected_candidates.length > 0 ? (
                report.selected_candidates.map((c, idx) => (
                  <div
                    key={idx}
                    style={{
                      marginBottom:
                        idx < report.selected_candidates.length - 1 ? 16 : 0,
                      paddingBottom:
                        idx < report.selected_candidates.length - 1 ? 16 : 0,
                      borderBottom:
                        idx < report.selected_candidates.length - 1
                          ? "1px solid var(--border-color)"
                          : "none",
                    }}
                  >
                    <div
                      style={{
                        fontSize: 15,
                        fontWeight: 500,
                        color: "var(--text-main)",
                        marginBottom: 8,
                      }}
                    >
                      {c.name}
                      {report.selected_candidates.length > 1 && (
                        <span
                          style={{
                            fontSize: 10,
                            color: "#7c6af7",
                            marginLeft: 8,
                            background: "#1a1240",
                            padding: "2px 8px",
                            borderRadius: 10,
                          }}
                        >
                          Candidate {idx + 1}
                        </span>
                      )}
                    </div>
                    {[
                      ["Role", c.role || c.role_applied],
                      ["Experience", c.experience],
                      ["Company", c.previous_company],
                      ["Education", c.education],
                      ["Salary", c.expected_salary],
                      ["Notice", c.notice_period],
                      ["Location", c.location],
                      ["Score", `${c.score}/100`],
                      ["Email", c.email],
                      ["Phone", c.phone],
                    ].map(
                      ([k, v]) =>
                        v && (
                          <div
                            key={k}
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              padding: "4px 0",
                              borderBottom: "1px solid var(--border-color)",
                              fontSize: 12,
                            }}
                          >
                            <span style={{ color: "var(--text-muted)" }}>
                              {k}
                            </span>
                            <span
                              style={{
                                color: "var(--text-main)",
                                fontWeight: 500,
                              }}
                            >
                              {v}
                            </span>
                          </div>
                        ),
                    )}
                    <div
                      style={{
                        marginTop: 8,
                        padding: "6px 10px",
                        background: "#0d2818",
                        borderRadius: 6,
                        fontSize: 11,
                        color: "#48bb78",
                      }}
                    >
                      ✅ Interview scheduled · WhatsApp sent
                    </div>
                  </div>
                ))
              ) : (
                <div style={{ color: "var(--text-muted)", fontSize: 13 }}>
                  No candidate selected yet
                </div>
              )}
            </div>
            {/* Selected Investor */}
            <div className="card">
              <div className="card-title" style={{ marginBottom: 12 }}>
                💼 Selected Investor / Partner
              </div>
              {report.selected_investor ? (
                <div>
                  <div
                    style={{
                      fontSize: 16,
                      fontWeight: 500,
                      color: "var(--text-main)",
                      marginBottom: 4,
                    }}
                  >
                    {report.selected_investor.company}
                  </div>
                  {[
                    ["Contact", report.selected_investor.contact_name],
                    ["Designation", report.selected_investor.designation],
                    ["Industry", report.selected_investor.industry],
                    [
                      "Investment",
                      `₹${parseInt(
                        report.selected_investor.budget_inr || 0,
                      ).toLocaleString()}`,
                    ],
                    ["Interest", report.selected_investor.interest_level],
                    ["Score", `${report.selected_investor.score}/100`],
                    ["Email", report.selected_investor.email],
                  ].map(
                    ([k, v]) =>
                      v && (
                        <div
                          key={k}
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            padding: "5px 0",
                            borderBottom: "1px solid var(--border-color)",
                            fontSize: 12,
                          }}
                        >
                          <span style={{ color: "var(--text-muted)" }}>
                            {k}
                          </span>
                          <span
                            style={{
                              color: "var(--text-main)",
                              fontWeight: 500,
                            }}
                          >
                            {v}
                          </span>
                        </div>
                      ),
                  )}
                  <div
                    style={{
                      marginTop: 8,
                      padding: "8px 10px",
                      background: "#0a1240",
                      borderRadius: 6,
                      fontSize: 11,
                      color: "#9f7aea",
                    }}
                  >
                    ✅ Partnership confirmed · WhatsApp notification sent
                  </div>
                </div>
              ) : (
                <div style={{ color: "var(--text-muted)", fontSize: 13 }}>
                  Self-funded project — no external investor
                </div>
              )}
            </div>
          </div>

          {/* Department Work */}
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title" style={{ marginBottom: 14 }}>
              🤖 Agent Work — What Each Department Did
            </div>
            {Object.entries(report.dept_work || {}).map(([dept, work]) => (
              <div
                key={dept}
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 14,
                  marginBottom: 12,
                  padding: "12px 14px",
                  borderRadius: 8,
                  background: work.on_time ? "#0a1f0a" : "#1f1200",
                  border: `1px solid ${work.on_time ? "#48bb78" : "#f6ad55"}`,
                }}
              >
                <div
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: 8,
                    flexShrink: 0,
                    background: "rgba(0,0,0,0.3)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 18,
                  }}
                >
                  {deptIcons[dept] || "📋"}
                </div>
                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: 4,
                    }}
                  >
                    <div
                      style={{
                        fontSize: 13,
                        fontWeight: 500,
                        color: "var(--text-main)",
                        textTransform: "capitalize",
                      }}
                    >
                      {work.step}
                    </div>
                    <div style={{ display: "flex", gap: 8 }}>
                      {work.duration && (
                        <span
                          style={{ fontSize: 10, color: "var(--text-muted)" }}
                        >
                          {work.duration}s
                        </span>
                      )}
                      <span
                        className={`badge ${work.on_time ? "badge-green" : "badge-yellow"}`}
                      >
                        {work.on_time ? "On Time" : "Delayed"}
                      </span>
                    </div>
                  </div>
                  <div
                    style={{
                      fontSize: 12,
                      color: "var(--text-muted)",
                      lineHeight: 1.5,
                    }}
                  >
                    {work.summary}
                  </div>
                  {work.deadline && (
                    <div
                      style={{ fontSize: 10, color: "#4a5568", marginTop: 4 }}
                    >
                      Deadline:{" "}
                      {new Date(work.deadline).toLocaleString("en-IN", {
                        dateStyle: "medium",
                        timeStyle: "short",
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Approvals Table */}
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title" style={{ marginBottom: 12 }}>
              ✅ Project Approvals — CEO Decisions
            </div>
            {report.approvals?.length === 0 ? (
              <div style={{ color: "var(--text-muted)", fontSize: 13 }}>
                No approvals for this project yet
              </div>
            ) : (
              <table className="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Department</th>
                    <th>Request</th>
                    <th>Priority</th>
                    <th>Decision</th>
                    <th>Notes</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {(report.approvals || []).map((a, i) => (
                    <tr key={i}>
                      <td style={{ fontSize: 10, color: "#4a5568" }}>
                        #{a.approval_id}
                      </td>
                      <td
                        style={{
                          textTransform: "uppercase",
                          fontSize: 11,
                          color: "#f6ad55",
                        }}
                      >
                        {a.agent}
                      </td>
                      <td style={{ color: "var(--text-main)", maxWidth: 300 }}>
                        {a.task?.substring(0, 80)}
                        {a.task?.length > 80 ? "..." : ""}
                      </td>
                      <td>
                        <span
                          className={`badge ${
                            a.priority === "critical"
                              ? "badge-red"
                              : a.priority === "high"
                                ? "badge-yellow"
                                : "badge-blue"
                          }`}
                        >
                          {a.priority}
                        </span>
                      </td>
                      <td>
                        <span
                          className={`badge ${
                            a.decision === "approve"
                              ? "badge-green"
                              : a.decision === "reject"
                                ? "badge-red"
                                : a.status === "pending"
                                  ? "badge-yellow"
                                  : "badge-blue"
                          }`}
                        >
                          {a.decision || a.status}
                        </span>
                      </td>
                      <td style={{ fontSize: 11, color: "var(--text-muted)" }}>
                        {a.notes || "—"}
                      </td>
                      <td style={{ fontSize: 10, color: "#4a5568" }}>
                        {a.decided_at
                          ? new Date(a.decided_at).toLocaleTimeString("en-IN")
                          : "Pending"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Activity Timeline */}
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="card-title" style={{ marginBottom: 12 }}>
              ⚡ Activity Timeline
            </div>
            {(report.activities || []).length === 0 ? (
              <div style={{ color: "var(--text-muted)", fontSize: 13 }}>
                No activity logged yet
              </div>
            ) : (
              (report.activities || []).map((a, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    gap: 10,
                    alignItems: "flex-start",
                    marginBottom: 8,
                    paddingBottom: 8,
                    borderBottom:
                      i < report.activities.length - 1
                        ? "1px solid var(--border-color)"
                        : "none",
                  }}
                >
                  <div
                    style={{
                      width: 6,
                      height: 6,
                      borderRadius: "50%",
                      marginTop: 5,
                      flexShrink: 0,
                      background:
                        a.category === "project"
                          ? "#7c6af7"
                          : a.category === "hr"
                            ? "#48bb78"
                            : a.category === "finance"
                              ? "#f6ad55"
                              : a.category === "sales"
                                ? "#63b3ed"
                                : "#4a5568",
                    }}
                  />
                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        fontSize: 12,
                        color: "var(--text-main)",
                        lineHeight: 1.4,
                      }}
                    >
                      {a.message}
                    </div>
                    <div
                      style={{ fontSize: 10, color: "#4a5568", marginTop: 2 }}
                    >
                      {a.agent} · {a.time}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Financial Summary */}
          <div className="card">
            <div className="card-title" style={{ marginBottom: 14 }}>
              💰 Financial Summary
            </div>
            <div className="grid grid-3">
              {[
                {
                  label: "Project Value",
                  value: `₹${(report.value || 0).toLocaleString()}`,
                  color: "#48bb78",
                },
                {
                  label: "Approved Spend",
                  value: `₹${(report.approved_costs || 0).toLocaleString()}`,
                  color: "#f6ad55",
                },
                {
                  label: "Net Revenue",
                  value: `₹${((report.value || 0) - (report.approved_costs || 0)).toLocaleString()}`,
                  color: "#7c6af7",
                },
              ].map((item) => (
                <div
                  key={item.label}
                  style={{
                    padding: "16px",
                    background: "var(--bg-secondary)",
                    borderRadius: 8,
                    textAlign: "center",
                  }}
                >
                  <div
                    style={{ fontSize: 22, fontWeight: 700, color: item.color }}
                  >
                    {item.value}
                  </div>
                  <div
                    style={{
                      fontSize: 11,
                      color: "var(--text-muted)",
                      marginTop: 4,
                    }}
                  >
                    {item.label}
                  </div>
                </div>
              ))}
            </div>

            <div
              style={{
                marginTop: 14,
                padding: "10px 14px",
                background: "#0d0d1a",
                borderRadius: 8,
                border: "1px solid var(--border-color)",
                fontSize: 11,
                color: "var(--text-muted)",
                lineHeight: 1.7,
              }}
            >
              <strong style={{ color: "var(--text-main)" }}>
                Report generated by OrgMind
              </strong>{" "}
              · NexaCore Technologies Pvt Ltd ·{" "}
              {new Date().toLocaleDateString("en-IN", { dateStyle: "full" })} ·
              All data verified by AI agents
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── APP ───────────────────────────────────────────────────────────────
export default function App() {
  // Persisted new project state — survives tab switches
  const [projectDraft, setProjectDraft] = useState({
    selected: null,
    selInv: null,
    selCands: [],
    phase: 1,
    result: null,
  });
  const [page, setPage] = useState("overview");
  const [approvals, setApprovals] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    const fetchApprovals = () => {
      fetch(`${API}/ceo/approvals/all`)
        .then((r) => r.json())
        .then((d) => {
          const all = d.approvals || [];
          const pend = all.filter((a) => a.status === "pending");
          setApprovals(pend);
        })
        .catch(() => {});
    };
    fetchApprovals();
    const interval = setInterval(fetchApprovals, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <ThemeProvider>
      {" "}
      {/* 1. WRAP THE WHOLE APP */}
      <div className="app">
        <div
          className="sidebar"
          style={{
            width: sidebarOpen ? 220 : 56,
            transition: "all 0.25s ease",
            flexShrink: 0,
          }}
        >
          {/* ── Logo ── */}
          <div
            className="logo"
            style={{
              padding: sidebarOpen ? "20px 16px" : "20px 8px",
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            {/* Box Logo */}
            <div
              style={{
                width: 34,
                height: 34,
                borderRadius: 10,
                background: "linear-gradient(135deg, #7c6af7, #06b6d4)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 700,
                color: "white",
                fontSize: 13,
                boxShadow: "0 4px 12px rgba(124,106,247,0.3)",
              }}
            >
              OM
            </div>

            {sidebarOpen && (
              <div>
                <h1 style={{ fontSize: 14, margin: 0 }}>OrgMind</h1>
                <p style={{ fontSize: 10, margin: 0, color: "#4a5568" }}>
                  AI OS
                </p>
              </div>
            )}

            {/* Toggle Button */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              style={{
                position: "absolute",
                right: -10,
                top: 20,
                width: 22,
                height: 22,
                borderRadius: "50%",
                background: "#111827",
                border: "1px solid #2d2d4a",
                color: "#9f7aea",
                cursor: "pointer",
                fontSize: 11,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 0 10px rgba(0,0,0,0.4)",
              }}
            >
              {sidebarOpen ? "‹" : "›"}
            </button>
          </div>

          {/* ── Command Section ── */}
          <div className="nav-section">
            {sidebarOpen && <div className="nav-label">Command</div>}

            {NAV.map((n) => (
              <div
                key={n.id}
                className={`nav-item ${page === n.id ? "active" : ""}`}
                onClick={() => setPage(n.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: sidebarOpen ? "flex-start" : "center",
                  padding: sidebarOpen ? "10px 16px" : "10px",
                }}
              >
                <span className="nav-icon">{n.icon}</span>

                {sidebarOpen && (
                  <>
                    <span style={{ marginLeft: 10 }}>{n.label}</span>

                    {n.id === "approvals" && approvals.length > 0 && (
                      <span
                        className="badge badge-yellow"
                        style={{ marginLeft: "auto", padding: "1px 6px" }}
                      >
                        {approvals.length}
                      </span>
                    )}
                  </>
                )}
              </div>
            ))}
          </div>

          {/* ── Departments ── */}
          <div className="nav-section">
            {sidebarOpen && <div className="nav-label">Departments</div>}

            {AGENTS.map((a) => (
              <div
                key={a.id}
                className="nav-item"
                onClick={() => setPage("agents")}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: sidebarOpen ? "flex-start" : "center",
                  padding: sidebarOpen ? "10px 16px" : "10px",
                }}
              >
                <span className="nav-icon">{a.icon}</span>
                {sidebarOpen && (
                  <span style={{ marginLeft: 10 }}>{a.name}</span>
                )}
              </div>
            ))}
          </div>

          <div
            style={{
              padding: 16,
              marginTop: "auto",
              borderTop: "1px solid var(--border-color)",
            }}
          >
            {/* Show button only when sidebar is open */}
            {sidebarOpen && <ThemeToggleButton />}

            <div
              style={{
                fontSize: 10,
                color: "#4a5568",
                marginBottom: 4,
                marginTop: 10,
              }}
            >
              Stack
            </div>
            <div
              style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 8 }}
            >
              LangGraph · Groq · FastAPI · React
            </div>
          </div>
        </div>

        <div className="main">
          {page === "overview" && <Overview approvals={approvals} />}
          {page === "agents" && <Agents />}
          {page === "approvals" && (
            <Approvals
              approvals={approvals}
              onRefresh={() =>
                fetch(`${API}/ceo/approvals/all`)
                  .then((r) => r.json())
                  .then((d) => setApprovals(d.approvals || []))
              }
            />
          )}{" "}
          {page === "kpi" && <KPIs />}
          {/* CHANGE THIS: */}
          {page === "newproject" && (
            <NewProject draft={projectDraft} setDraft={setProjectDraft} />
          )}
          {page === "codefixer" && <CodeFixer />}
          {page === "marketing" && <Marketing />}
          {page === "projectapprovals" && <ProjectApprovals />}
          {page === "report" && <ProjectReport />}
        </div>
        <ChatWidget />
      </div>
    </ThemeProvider>
  );
}
