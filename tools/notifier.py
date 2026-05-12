from dotenv import load_dotenv
from datetime import datetime
import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()


# ══════════════════════════════════════════════════════════
#  CORE SEND FUNCTIONS
# ══════════════════════════════════════════════════════════

def send_whatsapp(to_number: str, message: str) -> dict:
    """
    Send WhatsApp — tries Adiology first, falls back to Twilio, then simulates.
    """
    # clean number for display
    display = to_number.replace("whatsapp:","")
    print(f"\n  📱 WhatsApp → {display}")
    print(f"     {message[:80]}...")

    # Try Adiology first (your custom notifier)
    adiology_key = os.getenv("ADIOLOGY_API_KEY","")
    if adiology_key:
        try:
            from tools.adiology_notifier import adiology_send
            result = adiology_send(to_number, message)
            if result.get("status") == "sent":
                return result
        except Exception as e:
            print(f"     Adiology failed: {e} — trying Twilio")

    # Try Twilio
    sid   = os.getenv("TWILIO_SID","")
    token = os.getenv("TWILIO_TOKEN","")
    from_ = os.getenv("TWILIO_WHATSAPP_FROM","whatsapp:+14155238886")

    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"

    if sid and token:
        try:
            from twilio.rest import Client
            msg = Client(sid, token).messages.create(
                from_=from_, to=to_number, body=message)
            print(f"     ✅ Twilio sent | SID: {msg.sid}")
            return {"status":"sent", "sid":msg.sid, "via":"twilio"}
        except Exception as e:
            print(f"     ⚠️  Twilio failed: {str(e)[:80]}")

    # Simulate
    print(f"\n  ┌─────────────────────────────────────")
    print(f"  │ 📱 WhatsApp (Simulated)")
    print(f"  │ To: {display}")
    for line in message.split('\n'):
        print(f"  │ {line}")
    print(f"  └─────────────────────────────────────")
    return {"status":"simulated", "to":display}

def send_email(to_email: str, subject: str, body: str,
               html_body: str = "") -> dict:
    """Send email via Gmail SMTP."""
    gmail_user = os.getenv("GMAIL_USER","")
    gmail_pass = os.getenv("GMAIL_APP_PASSWORD","")

    print(f"\n  📧 Email → {to_email}")
    print(f"     Subject: {subject}")

    if gmail_user and gmail_pass:
        try:
            msg            = MIMEMultipart("alternative")
            msg["Subject"] = f"[OrgMind] {subject}"
            msg["From"]    = f"OrgMind Technologies <{gmail_user}>"
            msg["To"]      = to_email
            msg.attach(MIMEText(body, "plain"))
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
                s.login(gmail_user, gmail_pass)
                s.sendmail(gmail_user, to_email, msg.as_string())

            print(f"     ✅ Sent")
            return {"status":"sent", "to":to_email, "subject":subject}
        except Exception as e:
            print(f"     ⚠️  Failed: {e}")
            return {"status":"failed", "error":str(e)}
    else:
        print(f"\n  ┌─────────────────────────────────────────")
        print(f"  │ 📧 Email (Simulated)")
        print(f"  │ To      : {to_email}")
        print(f"  │ Subject : [OrgMind] {subject}")
        print(f"  │ Time    : {datetime.now().strftime('%d %b %Y %I:%M %p')}")
        print(f"  ├─────────────────────────────────────────")
        for line in body.split('\n')[:8]:
            print(f"  │ {line}")
        print(f"  └─────────────────────────────────────────")
        return {"status":"simulated", "to":to_email, "subject":subject}


# ══════════════════════════════════════════════════════════
#  CEO NOTIFICATIONS
# ══════════════════════════════════════════════════════════

def notify_ceo(message: str, priority: str = "normal") -> dict:
    """Notify CEO via WhatsApp + Email."""
    ceo_wa    = os.getenv("YOUR_WHATSAPP_NUMBER","")
    ceo_email = os.getenv("CEO_EMAIL","")
    prefix    = "🚨 URGENT ACTION REQUIRED" if priority=="critical" else "📋 OrgMind Update"
    results   = {}

    full_msg = f"{prefix}\n\n{message}\n\n⏰ {datetime.now().strftime('%d %b %Y %I:%M %p')}"

    if ceo_wa:
        results["whatsapp"] = send_whatsapp(ceo_wa, full_msg)
    if ceo_email:
        results["email"] = send_email(
            ceo_email,
            f"{prefix} — {message[:50]}",
            full_msg
        )
    if not ceo_wa and not ceo_email:
        print(f"  📋 CEO notification simulated: {message[:60]}")
        results["status"] = "simulated"

    return results


# ══════════════════════════════════════════════════════════
#  CANDIDATE NOTIFICATIONS
# ══════════════════════════════════════════════════════════

def notify_candidate_shortlisted(candidate: dict,
                                  project_name: str,
                                  interview_schedule: dict = None) -> dict:
    """Notify selected candidate via WhatsApp + Email."""
    name     = candidate.get("name","Candidate")
    email    = candidate.get("email","")
    phone    = candidate.get("phone","")
    role     = candidate.get("role", candidate.get("role_applied","the role"))
    score    = candidate.get("score", 0)

    schedule_text = ""
    if interview_schedule:
        schedule_text = (
            f"\n\n📅 Interview Details:\n"
            f"Date : {interview_schedule.get('date','TBD')}\n"
            f"Time : {interview_schedule.get('time','TBD')}\n"
            f"Mode : {interview_schedule.get('mode','Google Meet')}\n"
            f"Duration: {interview_schedule.get('duration','45 min')}"
        )

    wa_msg = (
        f"🎉 Congratulations {name}!\n\n"
        f"You have been shortlisted for *{role}* at "
        f"*OrgMind Technologies Pvt Ltd*.\n\n"
        f"Project : {project_name}\n"
        f"Your Score: {score}/100"
        f"{schedule_text}\n\n"
        f"Our HR team will be in touch shortly.\n"
        f"— OrgMind HR Team"
    )

    email_body = (
        f"Dear {name},\n\n"
        f"We are pleased to inform you that you have been shortlisted "
        f"for the position of {role} at OrgMind Technologies Pvt Ltd.\n\n"
        f"Project     : {project_name}\n"
        f"Your Score  : {score}/100\n"
        f"Role        : {role}"
        f"{schedule_text.replace(chr(10), chr(10))}\n\n"
        f"Our HR team will reach out to confirm next steps.\n\n"
        f"Best regards,\n"
        f"HR Team\nOrgMind Technologies Pvt Ltd\n"
        f"contact@OrgMind.in | +91-9876543210"
    )

    results = {}
    if phone:
        results["whatsapp"] = send_whatsapp(phone, wa_msg)
    if email:
        results["email"] = send_email(
            email,
            f"Shortlisted for {role} — {project_name}",
            email_body
        )

    print(f"  ✅ Candidate notified: {name}")
    return results


# ══════════════════════════════════════════════════════════
#  CLIENT NOTIFICATIONS
# ══════════════════════════════════════════════════════════

def notify_client_project_started(client_name: str, client_email: str,
                                   client_phone: str, project: dict) -> dict:
    """Notify client that their project has been approved and started."""
    project_name = project.get("name", project.get("project_name",""))
    value        = project.get("value", 0)

    wa_msg = (
        f"🚀 *Project Started — OrgMind Technologies*\n\n"
        f"Dear {client_name},\n\n"
        f"Your project *{project_name}* has been approved "
        f"and our team has started working on it.\n\n"
        f"Project Value : ₹{int(value):,}\n"
        f"Started       : {datetime.now().strftime('%d %b %Y')}\n\n"
        f"Our project manager will contact you within 24 hours "
        f"to schedule a kickoff meeting.\n\n"
        f"— OrgMind Technologies\n"
        f"📞 +91-9876543210"
    )

    email_body = (
        f"Dear {client_name},\n\n"
        f"We are pleased to inform you that your project "
        f"'{project_name}' has been officially approved and initiated.\n\n"
        f"Project Details:\n"
        f"  Name  : {project_name}\n"
        f"  Value : ₹{int(value):,}\n"
        f"  Start : {datetime.now().strftime('%d %B %Y')}\n\n"
        f"Our dedicated project team will reach out within 24 hours "
        f"to schedule the kickoff meeting and share the project timeline.\n\n"
        f"Thank you for choosing OrgMind Technologies.\n\n"
        f"Best regards,\n"
        f"Project Management Team\n"
        f"OrgMind Technologies Pvt Ltd\n"
        f"contact@OrgMind.in | +91-9876543210"
    )

    results = {}
    if client_phone:
        results["whatsapp"] = send_whatsapp(client_phone, wa_msg)
    if client_email:
        results["email"] = send_email(
            client_email,
            f"Project Started — {project_name}",
            email_body
        )

    print(f"  ✅ Client notified: {client_name}")
    return results


# ══════════════════════════════════════════════════════════
#  INVESTOR NOTIFICATIONS
# ══════════════════════════════════════════════════════════

def notify_investor_selected(investor: dict, project: dict) -> dict:
    """Notify selected investor that CEO has chosen them."""
    name         = investor.get("contact_name", investor.get("name",""))
    email        = investor.get("email","")
    phone        = investor.get("phone","")
    company      = investor.get("company","")
    amount       = investor.get("budget_inr", 0)
    project_name = project.get("name", project.get("project_name",""))

    wa_msg = (
        f"🤝 *Investment Opportunity — OrgMind Technologies*\n\n"
        f"Dear {name},\n\n"
        f"We are pleased to inform you that your investment interest "
        f"in *OrgMind Technologies* has been reviewed and selected "
        f"by our CEO.\n\n"
        f"Project    : {project_name}\n"
        f"Amount     : ₹{int(amount):,}\n"
        f"Your Company: {company}\n\n"
        f"Our team will contact you within 48 hours to discuss "
        f"terms, equity/debt structure, and next steps.\n\n"
        f"— CEO Office\nOrgMind Technologies Pvt Ltd\n"
        f"📞 +91-9876543210"
    )

    email_body = (
        f"Dear {name},\n\n"
        f"We are delighted to inform you that following a thorough "
        f"evaluation of all investor applications, OrgMind Technologies "
        f"has selected {company} as our preferred investment partner "
        f"for the project '{project_name}'.\n\n"
        f"Investment Details:\n"
        f"  Company    : {company}\n"
        f"  Amount     : ₹{int(amount):,}\n"
        f"  Project    : {project_name}\n"
        f"  Selected on: {datetime.now().strftime('%d %B %Y')}\n\n"
        f"Our legal and finance team will reach out within 48 hours "
        f"to initiate due diligence, share the term sheet, "
        f"and schedule a meeting with our CEO.\n\n"
        f"Thank you for your confidence in OrgMind Technologies.\n\n"
        f"Warm regards,\n"
        f"CEO Office\n"
        f"OrgMind Technologies Pvt Ltd\n"
        f"contact@OrgMind.in | +91-9876543210"
    )

    results = {}
    if phone:
        results["whatsapp"] = send_whatsapp(phone, wa_msg)
    if email:
        results["email"] = send_email(
            email,
            f"Investment Selected — {project_name} — OrgMind Technologies",
            email_body
        )

    print(f"  ✅ Investor notified: {name} ({company})")
    return results


# ══════════════════════════════════════════════════════════
#  MARKETING BROADCAST (existing customers/users)
# ══════════════════════════════════════════════════════════

def marketing_broadcast_whatsapp(numbers: list,
                                  message: str,
                                  campaign_name: str = "") -> dict:
    """
    Send marketing WhatsApp to a list of numbers.
    Use for product updates, campaigns, announcements.
    """
    print(f"\n📣 Marketing Broadcast — {campaign_name}")
    print(f"   Recipients: {len(numbers)}")
    print(f"   Message   : {message[:80]}...")

    results  = []
    sent     = 0
    failed   = 0
    simulated = 0

    for number in numbers:
        result = send_whatsapp(number, message)
        results.append(result)
        if result["status"] == "sent":
            sent += 1
        elif result["status"] == "failed":
            failed += 1
        else:
            simulated += 1

    print(f"\n  ✅ Sent: {sent} | ❌ Failed: {failed} | 📋 Simulated: {simulated}")

    return {
        "campaign":  campaign_name,
        "total":     len(numbers),
        "sent":      sent,
        "failed":    failed,
        "simulated": simulated,
        "results":   results,
        "timestamp": datetime.now().isoformat(),
    }


def marketing_broadcast_email(emails: list,
                               subject: str,
                               body: str,
                               campaign_name: str = "") -> dict:
    """Send marketing email to a list."""
    print(f"\n📧 Email Broadcast — {campaign_name}")
    print(f"   Recipients: {len(emails)}")

    results  = []
    sent     = 0
    failed   = 0
    simulated = 0

    for email in emails:
        result = send_email(email, subject, body)
        results.append(result)
        if result["status"] == "sent":
            sent += 1
        elif result["status"] == "failed":
            failed += 1
        else:
            simulated += 1

    print(f"  ✅ Sent: {sent} | ❌ Failed: {failed} | 📋 Simulated: {simulated}")

    return {
        "campaign":  campaign_name,
        "total":     len(emails),
        "sent":      sent,
        "failed":    failed,
        "simulated": simulated,
        "timestamp": datetime.now().isoformat(),
    }