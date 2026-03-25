import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
HUD_API_KEY = os.getenv("HUD_API_KEY")
county_code = "48453" # Travis County

headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
url = f"https://www.huduser.gov/portal/datasets/fmr/fmr2024/api/data/{county_code}"

print(f"Testing HUD API with key: {HUD_API_KEY[:10] if HUD_API_KEY else 'None'}...")
try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
