import csv, os, io
from dotenv import load_dotenv
load_dotenv()

# ── Column mapping: Google Form label → OrgMind CSV column name ──────
RESUME_COLUMN_MAP = {
    # exact Google Form headers (lowercase stripped)
    "timestamp":                                        "submitted_at",
    "full name":                                        "name",
    "email address":                                    "email",
    "phone number (whatsapp)":                          "phone",
    "phone number":                                     "phone",
    "position applied for :":                           "role_applied",
    "position applied for":                             "role_applied",
    "years of experience:":                             "experience_years",
    "years of experience":                              "experience_years",
    "education / college":                              "education",
    "education":                                        "education",
    "key skills (long answer — comma separated)":       "skills",
    "key skills":                                       "skills",
    "previous company (short answer) if any":          "previous_company",
    "previous company":                                 "previous_company",
    "current city (short answer)":                      "location",
    "current city":                                     "location",
    "expected salary per month in ₹ (short answer)":   "expected_salary",
    "expected salary per month in ₹":                  "expected_salary",
    "expected salary":                                  "expected_salary",
    "notice period in days (short answer)":             "notice_period",
    "notice period in days":                            "notice_period",
    "notice period":                                    "notice_period",
    "linkedin profile (short answer)":                  "linkedin",
    "linkedin profile":                                 "linkedin",
    "name":                                             "name",
    "email":                                            "email",
    "phone":                                            "phone",
    "skills":                                           "skills",
    "location":                                         "location",
}

LEADS_COLUMN_MAP = {
    "timestamp":                                        "submitted_at",
    "your name":                                        "contact_name",
    "name":                                             "contact_name",
    "designation":                                      "designation",
    "company name":                                     "company",
    "company":                                          "company",
    "company email":                                    "email",
    "email":                                            "email",
    "phone number":                                     "phone",
    "phone":                                            "phone",
    "industry (dropdown):":                             "industry",
    "industry":                                         "industry",
    "company size (multiple choice):":                  "company_size",
    "company size":                                     "company_size",
    "budget / investment range in ₹ (dropdown):":       "budget_inr",
    "budget / investment range in ₹":                   "budget_inr",
    "budget":                                           "budget_inr",
    "interest level (multiple choice):":                "interest_level",
    "interest level":                                   "interest_level",
    "your requirement (long answer)":                   "requirement",
    "your requirement":                                 "requirement",
    "requirement":                                      "requirement",
    "your city":                                        "city",
    "city":                                             "city",
    "how did you hear about us? (multiple choice):":    "source",
    "how did you hear about us?":                       "source",
    "source":                                           "source",
}

PROJECTS_COLUMN_MAP = {
    "project name":          "name",
    "name":                  "name",
    "client company":        "client",
    "client":                "client",
    "client contact name":   "contact_name",
    "client email":          "client_email",
    "project value in ₹":   "value",
    "value":                 "value",
    "project type":          "type",
    "type":                  "type",
    "roles required":        "roles",
    "roles":                 "roles",
    "project duration":      "duration",
    "duration":              "duration",
    "project description":   "description",
    "description":           "description",
    "special requirements":  "requirements",
    "priority":              "priority",
    "timestamp":             "submitted_at",
}

# Budget string → integer mapping
BUDGET_MAP = {
    "up to 5 lakhs":     400000,
    "5-20 lakhs":        1000000,
    "20-50 lakhs":       3500000,
    "50 lakhs+":         6000000,
}


def _normalize_row(row: dict, column_map: dict) -> dict:
    """
    Ultra-flexible normalizer.
    Strips all special chars, spaces, emojis before matching.
    """
    import re
    normalized = {}

    def clean(s):
        s = s.lower().strip()
        s = re.sub(r'[^\w\s]', ' ', s)  # remove special chars
        s = re.sub(r'\s+', ' ', s).strip()  # normalize spaces
        return s

    for key, value in row.items():
        ck = clean(key)
        mapped = None

        # direct match
        for map_key, map_val in column_map.items():
            if clean(map_key) == ck:
                mapped = map_val
                break

        # substring match
        if not mapped:
            for map_key, map_val in column_map.items():
                mk = clean(map_key)
                if mk in ck or ck in mk:
                    mapped = map_val
                    break

        # word match — any word overlap
        if not mapped:
            ck_words = set(ck.split())
            for map_key, map_val in column_map.items():
                mk_words = set(clean(map_key).split())
                if len(ck_words & mk_words) >= 2:
                    mapped = map_val
                    break

        if not mapped:
            mapped = ck.replace(' ', '_')

        val = value.strip() if isinstance(value, str) else value
        normalized[mapped] = val

    return normalized


def _fix_budget(val: str) -> str:
    """Convert budget range string to integer string."""
    if not val:
        return "500000"
    val_lower = val.lower().strip()
    for label, amount in BUDGET_MAP.items():
        if label in val_lower:
            return str(amount)
    # if already a number
    cleaned = ''.join(filter(str.isdigit, val))
    return cleaned if cleaned else "500000"


def _fix_experience(val: str) -> str:
    """Convert experience range to integer."""
    if not val:
        return "1"
    val_lower = val.lower()
    if "fresher" in val_lower or "0-1" in val_lower:
        return "1"
    if "1-3" in val_lower:
        return "2"
    if "3-5" in val_lower:
        return "4"
    if "5+" in val_lower or "5 +" in val_lower:
        return "6"
    cleaned = ''.join(filter(str.isdigit, val.split('-')[0]))
    return cleaned if cleaned else "1"


def _add_ids(rows: list, prefix: str) -> list:
    """Add ID column if missing."""
    for i, row in enumerate(rows):
        if not row.get("id"):
            row["id"] = f"{prefix}{str(i+1).zfill(3)}"
    return rows


def read_sheet_raw(sheet_id: str) -> list:
    """Download sheet and return as list of dicts."""
    try:
        import urllib.request
        url      = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        req      = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=10)
        content  = response.read().decode('utf-8')
        reader   = csv.DictReader(io.StringIO(content))
        rows     = [dict(row) for row in reader]
        return rows
    except Exception as e:
        print(f"  ⚠️  Sheet read failed: {e}")
        return []


def sync_resumes(sheet_id: str = "") -> dict:
    if not sheet_id:
        sheet_id = os.getenv("RESUMES_SHEET_ID", "")

    existing_path = os.path.join("data", "resumes.csv")

    if not sheet_id:
        count = _count_csv(existing_path)
        return {"status": "using_csv", "count": count, "source": "resumes.csv"}

    print(f"\n  🔄 Syncing resumes from sheet...")
    raw_rows = read_sheet_raw(sheet_id)

    if not raw_rows:
        count = _count_csv(existing_path)
        return {"status": "using_csv", "count": count,
                "source": "resumes.csv", "note": "Sheet empty"}
    
    def debug_sheet_headers(sheet_id: str) -> dict:
        """Show exact column headers from sheet — for debugging."""
        rows = read_sheet_raw(sheet_id)
        if not rows:
            return {"error": "Could not read sheet"}
        return {
            "first_row_keys": list(rows[0].keys()),
            "sample_row":     rows[0],
            "total_rows":     len(rows)
        }

    # normalize columns
    normalized = []
    for row in raw_rows:
        n = _normalize_row(row, RESUME_COLUMN_MAP)
        # fix data types
        n["experience_years"] = _fix_experience(n.get("experience_years","1"))
        n["expected_salary"]  = ''.join(filter(str.isdigit,
                                n.get("expected_salary","30000"))) or "30000"
        n["notice_period"]    = ''.join(filter(str.isdigit,
                                n.get("notice_period","30"))) or "30"
        if not n.get("name") or not n.get("email"):
            continue  # skip empty rows
        normalized.append(n)

    normalized = _add_ids(normalized, "R")

    # write to CSV
    if normalized:
        fieldnames = ["id","name","email","phone","role_applied","experience_years",
                      "education","skills","previous_company","location",
                      "expected_salary","notice_period","submitted_at"]
        _write_csv(existing_path, normalized, fieldnames)
        print(f"  ✅ {len(normalized)} resumes synced from sheet")
        return {"status": "synced", "count": len(normalized), "source": "google_sheet"}

    count = _count_csv(existing_path)
    return {"status": "using_csv", "count": count, "source": "resumes.csv"}


def sync_leads(sheet_id: str = "") -> dict:
    if not sheet_id:
        sheet_id = os.getenv("LEADS_SHEET_ID", "")

    existing_path = os.path.join("data", "leads.csv")

    if not sheet_id:
        count = _count_csv(existing_path)
        return {"status": "using_csv", "count": count, "source": "leads.csv"}

    print(f"\n  🔄 Syncing investors/leads from sheet...")
    raw_rows = read_sheet_raw(sheet_id)

    if not raw_rows:
        count = _count_csv(existing_path)
        return {"status": "using_csv", "count": count,
                "source": "leads.csv", "note": "Sheet empty"}

    normalized = []
    for row in raw_rows:
        n = _normalize_row(row, LEADS_COLUMN_MAP)
        n["budget_inr"]    = _fix_budget(n.get("budget_inr",""))
        n["interest_level"] = _normalize_interest(n.get("interest_level","medium"))
        n["company_size"]  = _normalize_size(n.get("company_size","SME"))
        n["status"]        = "qualified"
        n["last_contact"]  = n.get("submitted_at","2026-05-01")[:10] or "2026-05-01"
        if not n.get("company") or not n.get("contact_name"):
            continue
        normalized.append(n)

    normalized = _add_ids(normalized, "L")

    if normalized:
        fieldnames = ["id","company","contact_name","designation","email","phone",
                      "industry","company_size","budget_inr","interest_level",
                      "source","city","requirement","last_contact","status"]
        _write_csv(existing_path, normalized, fieldnames)
        print(f"  ✅ {len(normalized)} investors synced from sheet")
        return {"status": "synced", "count": len(normalized), "source": "google_sheet"}

    count = _count_csv(existing_path)
    return {"status": "using_csv", "count": count, "source": "leads.csv"}


def sync_projects(sheet_id: str = "") -> dict:
    if not sheet_id:
        sheet_id = os.getenv("PROJECTS_SHEET_ID", "")

    if not sheet_id:
        return {"status": "skipped", "reason": "No PROJECTS_SHEET_ID in .env"}

    print(f"\n  🔄 Syncing projects from sheet...")
    raw_rows = read_sheet_raw(sheet_id)

    if not raw_rows:
        return {"status": "skipped", "reason": "Sheet empty"}

    normalized = []
    for i, row in enumerate(raw_rows):
        n = _normalize_row(row, PROJECTS_COLUMN_MAP)
        n["value"]  = ''.join(filter(str.isdigit,
                      str(n.get("value","500000")))) or "500000"
        n["status"] = "available"
        if not n.get("name") or not n.get("client"):
            continue
        normalized.append(n)

    normalized = _add_ids(normalized, "P")

    if normalized:
        path       = os.path.join("data", "projects_live.csv")
        fieldnames = ["id","name","client","contact_name","client_email",
                      "value","type","roles","duration","description",
                      "requirements","priority","status","submitted_at"]
        _write_csv(path, normalized, fieldnames)
        print(f"  ✅ {len(normalized)} projects synced from sheet")
        return {"status": "synced", "count": len(normalized), "source": "google_sheet"}

    return {"status": "skipped", "reason": "No valid rows"}


# ── Helpers ────────────────────────────────────────────────────────
def _count_csv(path: str) -> int:
    try:
        with open(path, newline='', encoding='utf-8') as f:
            return sum(1 for _ in csv.reader(f)) - 1
    except:
        return 0


def _write_csv(path: str, rows: list, fieldnames: list):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    all_keys = set()
    for r in rows:
        all_keys.update(r.keys())
    final_fields = fieldnames + [k for k in all_keys if k not in fieldnames]

    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=final_fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def _normalize_interest(val: str) -> str:
    val = val.lower()
    if "high" in val or "ready" in val:
        return "high"
    if "low" in val or "enquir" in val:
        return "low"
    return "medium"


def _normalize_size(val: str) -> str:
    val = val.lower()
    if "enterprise" in val or "500" in val:
        return "Enterprise"
    if "mid" in val or "100" in val:
        return "Mid-market"
    return "SME"