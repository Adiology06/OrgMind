from langchain_groq import ChatGroq
from state.schema import AgentState, new_state
from agents.ceo import should_escalate, ceo_review
from dotenv import load_dotenv
from datetime import datetime
import os, json, re

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.4,
)

# ─── Mock data ───────────────────────────────────────────────────────
CAMPAIGNS = [
    {"id": "C001", "name": "May Launch",      "platform": "WhatsApp", "budget": 8000,  "status": "draft",   "audience": "SME owners"},
    {"id": "C002", "name": "Summer Sale",     "platform": "Email",    "budget": 3000,  "status": "active",  "audience": "existing customers"},
    {"id": "C003", "name": "Brand Awareness", "platform": "LinkedIn", "budget": 15000, "status": "draft",   "audience": "startup founders"},
]

CONTACTS = [
    {"name": "Amit Khanna",  "phone": "whatsapp:+91XXXXXXXXXX", "segment": "premium"},
    {"name": "Sunita Rao",   "phone": "whatsapp:+91XXXXXXXXXX", "segment": "standard"},
    {"name": "Dev Malhotra", "phone": "whatsapp:+91XXXXXXXXXX", "segment": "premium"},
]


# ════════════════════════════════════════════════════════════════════
#  1. CAMPAIGN CREATOR
# ════════════════════════════════════════════════════════════════════
def create_campaign(campaign_id: str) -> dict:
    camp = next((c for c in CAMPAIGNS if c["id"] == campaign_id), None)
    if not camp:
        return {"error": f"Campaign {campaign_id} not found"}

    print(f"\n📣 Marketing Agent — Creating Campaign: {camp['name']}")
    print("─" * 45)

    prompt = f"""
Create a marketing campaign plan in JSON format only.
Campaign : {camp['name']}
Platform : {camp['platform']}
Budget   : ₹{camp['budget']:,}
Audience : {camp['audience']}
Product  : OrgMind — AI business operating system for SMEs

JSON format:
{{
  "headline": "...",
  "tagline": "...",
  "message": "2-3 sentence campaign message",
  "cta": "call to action text",
  "posting_schedule": ["Day 1", "Day 3", "Day 7"],
  "expected_reach": 0,
  "expected_leads": 0
}}
"""
    response = llm.invoke(prompt)
    raw      = response.content.strip().replace("```json","").replace("```","").strip()
    match    = re.search(r'\{.*\}', raw, re.DOTALL)
    try:
        plan = json.loads(match.group()) if match else {}
    except:
        plan = {}

    print(f"  📢 Headline  : {plan.get('headline','')}")
    print(f"  💬 Tagline   : {plan.get('tagline','')}")
    schedule = plan.get('posting_schedule', [])
    schedule_str = ', '.join([s if isinstance(s, str) else str(s) for s in schedule])
    print(f"  📅 Schedule  : {schedule_str}")
    print(f"  👥 Est.Reach : {plan.get('expected_reach',0):,}")
    print(f"  🎯 Est.Leads : {plan.get('expected_leads',0)}")

    return {"campaign": camp, "plan": plan}


# ════════════════════════════════════════════════════════════════════
#  2. WHATSAPP MESSAGE GENERATOR
#     (generates message — sends if Twilio creds present)
# ════════════════════════════════════════════════════════════════════
def whatsapp_campaign(campaign_id: str) -> dict:
    camp = next((c for c in CAMPAIGNS if c["id"] == campaign_id), None)
    if not camp:
        return {"error": "Campaign not found"}

    print(f"\n📱 Marketing Agent — WhatsApp Campaign: {camp['name']}")
    print("─" * 45)

    # Generate message with AI
    prompt = f"""
Write a WhatsApp business message for:
Campaign : {camp['name']}
Audience : {camp['audience']}
Product  : OrgMind AI Business OS — automates HR, Finance, Sales, Operations
Keep it under 160 characters, friendly, with 1 emoji.
Reply with just the message text only.
"""
    response = llm.invoke(prompt)
    message  = response.content.strip().strip('"')
    print(f"  ✉️  Message  : {message}")

    # Try sending via Twilio if creds exist
    sid   = os.getenv("TWILIO_SID")
    token = os.getenv("TWILIO_TOKEN")
    from_ = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
    to_   = os.getenv("YOUR_WHATSAPP_NUMBER")

    results = []
    if sid and token and to_:
        try:
            from twilio.rest import Client
            client = Client(sid, token)
            msg    = client.messages.create(
                from_=from_,
                to=to_,
                body=f"[OrgMind Campaign: {camp['name']}]\n\n{message}"
            )
            results.append({"to": to_, "status": msg.status, "sid": msg.sid})
            print(f"  ✅ Sent to {to_} | Status: {msg.status}")
        except Exception as e:
            results.append({"to": to_, "status": "simulated", "note": str(e)[:60]})
            print(f"  📋 Simulated send to {to_} (add Twilio creds to .env to send real)")
    else:
        results.append({"status": "simulated", "note": "Add TWILIO creds to .env for real sending"})
        print(f"  📋 Simulated — add Twilio creds to .env to send real WhatsApp messages")

    return {
        "campaign":     camp["name"],
        "message":      message,
        "platform":     "WhatsApp",
        "send_results": results,
    }


# ════════════════════════════════════════════════════════════════════
#  3. AD PERFORMANCE ANALYZER
# ════════════════════════════════════════════════════════════════════
def analyze_ad_performance() -> dict:
    print(f"\n📊 Marketing Agent — Ad Performance Analysis")
    print("─" * 45)

    # Mock ad performance data
    ads = [
        {"platform": "Facebook",  "spent": 5000,  "impressions": 45000, "clicks": 320, "conversions": 12},
        {"platform": "LinkedIn",  "spent": 8000,  "impressions": 18000, "clicks": 210, "conversions": 18},
        {"platform": "Instagram", "spent": 3000,  "impressions": 62000, "clicks": 480, "conversions": 8},
        {"platform": "WhatsApp",  "spent": 1500,  "impressions": 850,   "clicks": 210, "conversions": 22},
    ]

    for ad in ads:
        ad["ctr"]     = round(ad["clicks"] / ad["impressions"] * 100, 2)
        ad["cpc"]     = round(ad["spent"] / ad["clicks"], 2)
        ad["cpa"]     = round(ad["spent"] / ad["conversions"], 2) if ad["conversions"] else 0
        ad["roas"]    = round(ad["conversions"] * 8000 / ad["spent"], 2)
        print(f"  {ad['platform']:10s} | CTR: {ad['ctr']}% | CPC: ₹{ad['cpc']} | ROAS: {ad['roas']}x")

    best = max(ads, key=lambda x: x["roas"])
    worst = min(ads, key=lambda x: x["roas"])
    print(f"\n  🏆 Best ROAS  : {best['platform']} ({best['roas']}x)")
    print(f"  ⚠️  Worst ROAS : {worst['platform']} ({worst['roas']}x)")

    prompt = f"""
Ad performance: {json.dumps(ads)}
Best: {best['platform']}, Worst: {worst['platform']}
Give 2 budget reallocation recommendations in JSON array only.
["rec1", "rec2"]
"""
    response = llm.invoke(prompt)
    raw      = response.content.strip().replace("```json","").replace("```","").strip()
    match    = re.search(r'\[.*\]', raw, re.DOTALL)
    try:
        recs = json.loads(match.group()) if match else []
    except:
        recs = []

    print(f"\n  💡 AI Recommendations:")
    for i, r in enumerate(recs, 1):
        print(f"     {i}. {r}")

    return {"platforms": ads, "best_platform": best, "recommendations": recs}


# ════════════════════════════════════════════════════════════════════
#  4. SOCIAL MEDIA CONTENT GENERATOR
# ════════════════════════════════════════════════════════════════════
def generate_social_content(platform: str, topic: str) -> dict:
    print(f"\n✍️  Marketing Agent — {platform} Content: {topic}")
    print("─" * 45)

    limits = {"LinkedIn": 700, "Twitter": 280, "Instagram": 300, "WhatsApp": 160}
    limit  = limits.get(platform, 300)

    prompt = f"""
Write a {platform} post about: {topic}
Product: OrgMind — AI-powered business OS for SMEs/startups
Character limit: {limit}
Include relevant hashtags for {platform}.
Reply with just the post text only.
"""
    response = llm.invoke(prompt)
    content  = response.content.strip()
    print(f"  📝 {platform} Post ({len(content)} chars):")
    print(f"  {content[:120]}...")

    return {"platform": platform, "topic": topic, "content": content, "char_count": len(content)}


# ════════════════════════════════════════════════════════════════════
#  5. MAIN MARKETING AGENT RUNNER
# ════════════════════════════════════════════════════════════════════
def run_marketing_agent(action: str, **kwargs) -> AgentState:
    state = new_state(task=f"Marketing:{action}", agent="marketing", priority="medium")

    if action == "campaign":
        result = create_campaign(campaign_id=kwargs.get("campaign_id", "C001"))
        if result.get("campaign", {}).get("budget", 0) > 10000:
            state["needs_ceo_approval"] = True
            state["task"] = f"Marketing: Campaign '{result['campaign']['name']}' budget ₹{result['campaign']['budget']:,} needs approval"
            if should_escalate(state):
                state = ceo_review(state)

    elif action == "whatsapp":
        result = whatsapp_campaign(campaign_id=kwargs.get("campaign_id", "C001"))

    elif action == "adperformance":
        result = analyze_ad_performance()

    elif action == "social":
        result = generate_social_content(
            platform=kwargs.get("platform", "LinkedIn"),
            topic=kwargs.get("topic", "AI automation for SMEs")
        )
    else:
        result = {"error": f"Unknown action: {action}"}

    state["result"]     = result
    state["updated_at"] = datetime.now().isoformat()
    return state
