import os, requests
from dotenv import load_dotenv
load_dotenv()

ADIOLOGY_URL = os.getenv("ADIOLOGY_URL", "http://localhost:5000")
ADIOLOGY_KEY = os.getenv("ADIOLOGY_API_KEY", "")


def _headers():
    return {"x-api-key": ADIOLOGY_KEY, "Content-Type": "application/json"}


def adiology_send(number: str, message: str,
                  project_header: str = "🏢 OrgMind",
                  project_footer: str = "— OrgMind HR Team") -> dict:
    """Send WhatsApp via Adiology Notifier."""
    if not number or not ADIOLOGY_KEY:
        print(f"  📋 Adiology simulated → {number}: {message[:60]}")
        return {"status": "simulated"}

    # clean number — remove +91, spaces
    clean = number.replace("whatsapp:", "").replace("+91", "").replace("+", "").strip()
    if len(clean) != 10:
        print(f"  ⚠️  Adiology: invalid number {number}")
        return {"status": "invalid_number"}

    try:
        resp = requests.post(
            f"{ADIOLOGY_URL}/api/send",
            headers=_headers(),
            json={
                "number":        clean,
                "projectName":   "OrgMind",
                "projectHeader": project_header,
                "projectFooter": project_footer,
                "message":       message,
            },
            timeout=10,
        )
        data = resp.json()
        if resp.status_code == 200:
            print(f"  ✅ Adiology sent → {clean}")
            return {"status": "sent", "data": data}
        else:
            print(f"  ⚠️  Adiology error: {data}")
            return {"status": "failed", "error": str(data)}
    except Exception as e:
        print(f"  ⚠️  Adiology unreachable: {e}")
        return {"status": "failed", "error": str(e)}


def adiology_template(number: str, title: str, greeting: str,
                       body: str, details: list,
                       closing: str = "",
                       project_header: str = "🏢 OrgMind",
                       project_footer: str = "— OrgMind HR Team") -> dict:
    """Send structured template message via Adiology."""
    if not number or not ADIOLOGY_KEY:
        print(f"  📋 Adiology template simulated → {number}")
        return {"status": "simulated"}

    clean = number.replace("whatsapp:", "").replace("+91","").replace("+","").strip()
    if len(clean) != 10:
        return {"status": "invalid_number"}

    try:
        resp = requests.post(
            f"{ADIOLOGY_URL}/api/send-template",
            headers=_headers(),
            json={
                "number":        clean,
                "projectName":   "OrgMind",
                "projectHeader": project_header,
                "projectFooter": project_footer,
                "templateData": {
                    "title":    title,
                    "greeting": greeting,
                    "body":     body,
                    "details":  details,
                    "closing":  closing,
                }
            },
            timeout=10,
        )
        data = resp.json()
        if resp.status_code == 200:
            print(f"  ✅ Adiology template sent → {clean}")
            return {"status": "sent", "data": data}
        else:
            print(f"  ⚠️  Adiology error: {data}")
            return {"status": "failed", "error": str(data)}
    except Exception as e:
        print(f"  ⚠️  Adiology unreachable: {e}")
        return {"status": "failed", "error": str(e)}


def adiology_status() -> dict:
    """Check if Adiology notifier is running."""
    try:
        resp = requests.get(f"{ADIOLOGY_URL}/api/status",
                            headers=_headers(), timeout=5)
        return {"online": True, "data": resp.json()}
    except:
        return {"online": False}