from langchain_groq import ChatGroq
from dotenv import load_dotenv
from datetime import datetime
import os, json

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.5,
)

CHAT_HISTORY = []

def load_knowledge():
    kb_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'company_knowledge.json')
    with open(kb_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def is_confidential(query: str, knowledge: dict) -> bool:
    query_lower = query.lower()
    return any(topic in query_lower for topic in knowledge.get("confidential_topics", []))

def chat(query: str, session_id: str = "default") -> dict:
    knowledge = load_knowledge()

    # confidentiality check
    if is_confidential(query, knowledge):
        reply = ("I'm sorry, that information is confidential and cannot be shared. "
                 "For sensitive inquiries, please contact our team directly at "
                 f"{knowledge['company']['email']}.")
        CHAT_HISTORY.append({
            "session":   session_id,
            "query":     query,
            "response":  reply,
            "blocked":   True,
            "timestamp": datetime.now().isoformat(),
        })
        return {"response": reply, "blocked": True, "timestamp": datetime.now().isoformat()}

    # build context from knowledge base
    context = f"""
Company    : {knowledge['company']['name']}
Product    : {knowledge['product']['name']} — {knowledge['product']['tagline']}
Description: {knowledge['product']['description']}
Features   : {', '.join(knowledge['product']['key_features'][:5])}
Services   : {', '.join([s['name'] for s in knowledge['services']])}
Email      : {knowledge['company']['email']}
Phone      : {knowledge['company']['phone']}

FAQs:
{chr(10).join([f"Q: {f['q']} A: {f['a']}" for f in knowledge['faqs']])}

Current Projects:
{chr(10).join([f"- {p['name']} for {p['client']} ({p['status']})" for p in knowledge['current_projects']])}
"""

    # recent history for context
    recent = CHAT_HISTORY[-4:] if len(CHAT_HISTORY) >= 4 else CHAT_HISTORY
    history_text = "\n".join([
        f"User: {h['query']}\nBot: {h['response']}"
        for h in recent if h.get("session") == session_id
    ])

    prompt = f"""
You are OrgMind's intelligent customer support assistant for {knowledge['company']['name']}.
Be helpful, professional, and friendly. Keep responses concise (2-4 sentences max).
Never share confidential information. If unsure, direct to {knowledge['company']['email']}.

COMPANY KNOWLEDGE:
{context}

RECENT CONVERSATION:
{history_text}

USER QUESTION: {query}

Reply naturally and helpfully. If it's a greeting, be warm. If technical, be precise.
"""

    response = llm.invoke(prompt)
    reply    = response.content.strip()

    CHAT_HISTORY.append({
        "session":   session_id,
        "query":     query,
        "response":  reply,
        "blocked":   False,
        "timestamp": datetime.now().isoformat(),
    })

    return {
        "response":  reply,
        "blocked":   False,
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
    }

def get_chat_history(session_id: str = "default") -> list:
    return [h for h in CHAT_HISTORY if h.get("session") == session_id]

def clear_history(session_id: str = "default"):
    global CHAT_HISTORY
    CHAT_HISTORY = [h for h in CHAT_HISTORY if h.get("session") != session_id]