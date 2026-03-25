import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
h_key = os.getenv("HUD_API_KEY", "").strip().replace('"', '').replace("'", "")
entityid = "4845399999"

print(f"DEBUG: Key starts with: {h_key[:15]}...")

for year in ["2026", "2025", "2024"]:
    url = f"https://www.huduser.gov/hudapi/public/fmr/data/{entityid}?year={year}"
    headers = {"Authorization": f"Bearer {h_key}"}
    print(f"DEBUG: Trying {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"DEBUG: Status {response.status_code}")
        if response.status_code == 200:
            print(f"DEBUG: FOUND {year} DATA!")
            print(json.dumps(response.json(), indent=2)[:500])
        else:
            print(f"DEBUG: Error: {response.text}")
    except Exception as e:
        print(f"DEBUG: Exception: {e}")

# Also test Income Limits
print("\nDEBUG: Testing Income Limits...")
for year in ["2025", "2024"]:
    url = f"https://www.huduser.gov/hudapi/public/il/data/{entityid}?year={year}"
    headers = {"Authorization": f"Bearer {h_key}"}
    print(f"DEBUG: Trying {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"DEBUG: Status {response.status_code}")
        if response.status_code == 200:
            print(f"DEBUG: FOUND {year} IL DATA!")
            print(json.dumps(response.json(), indent=2)[:500])
        else:
            print(f"DEBUG: Error: {response.text}")
    except Exception as e:
        print(f"DEBUG: Exception: {e}")
