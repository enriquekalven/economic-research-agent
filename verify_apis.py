#  Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
"""ERA API Verification Script. Connectivity & Key Validation."""

import os
import requests
from fredapi import Fred
from dotenv import load_dotenv

load_dotenv()

def verify_fred():
    print("\n--- [1] FRED (St. Louis Fed) ---")
    key = os.getenv("FRED_API_KEY")
    try:
        fred = Fred(api_key=key)
        data = fred.get_series('UNRATE')
        print(f"✅ SUCCESS: Fetched Unemployment Rate (Latest: {data.iloc[-1]}%)")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")

def verify_bea():
    print("\n--- [2] BEA (Bureau of Economic Analysis) ---")
    key = os.getenv("BEA_API_KEY")
    url = f"https://apps.bea.gov/api/data?UserID={key}&method=GetDataSetList&ResultFormat=JSON"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ SUCCESS: BEA Dataset List accessible.")
        else:
            print(f"❌ FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")

def verify_census():
    print("\n--- [3] Census Bureau ---")
    key = os.getenv("CENSUS_API_KEY")
    url = f"https://api.census.gov/data/2021/acs/acs5?get=NAME&for=state:01&key={key}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ SUCCESS: Census ACS Connectivity confirmed.")
        else:
            print(f"❌ FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")

def verify_eia():
    print("\n--- [4] EIA (Energy Information Admin) ---")
    key = os.getenv("EIA_API_KEY")
    url = f"https://api.eia.gov/v2/electricity/retail-sales/data/?api_key={key}&data[0]=price&length=1"
    try:
        response = requests.get(url, timeout=12)
        if response.status_code == 200:
            print(f"✅ SUCCESS: EIA Electricity Data accessible.")
        else:
            print(f"❌ FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")

def verify_newsapi():
    print("\n--- [5] NewsAPI (Sentiment) ---")
    key = os.getenv("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize=1&apiKey={key}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ SUCCESS: NewsAPI Connectivity confirmed.")
        else:
            print(f"❌ FAILED: Status {response.status_code}")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")

if __name__ == "__main__":
    print("🛰️ ERA CONNECTOR VALIDATION...")
    verify_fred()
    verify_bea()
    verify_census()
    verify_eia()
    verify_newsapi()
    print("\n🚀 VALIDATION COMPLETE.")
