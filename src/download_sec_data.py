from pathlib import Path

import requests

CIK = "0000320193"  # Apple Inc.

url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"

headers = {
    "User-Agent": "Gregory Christenson gtchrist@gmail.com",
    "Accept-Encoding": "gzip, deflate",
}

response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()

data = response.json()

output_path = Path("data/raw/apple_companyfacts.json")
output_path.write_text(response.text, encoding="utf-8")

print(f"Saved raw SEC data to: {output_path}")
print(f"Company: {data['entityName']}")
print(f"CIK: {data['cik']}")
print(f"GAAP concepts available: {len(data['facts']['us-gaap'])}")