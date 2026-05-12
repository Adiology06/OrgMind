import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_adiology():
    url = f"{os.getenv('ADIOLOGY_URL')}/api/send"

    payload = {
        "number": "9876542100",
        "projectName": "OrgMind",
        "projectHeader": "🏢 OrgMind Recruitment Division",
        "projectFooter": "— OrgMind HR Team",
        "message": "OrgMind integration test successful"
    }

    headers = {
        "x-api-key": os.getenv("ADIOLOGY_API_KEY"),
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

test_adiology()