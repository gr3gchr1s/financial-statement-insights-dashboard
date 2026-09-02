import argparse
from pathlib import Path

import requests


parser = argparse.ArgumentParser(
    description="Download SEC company facts for a public company."
)

parser.add_argument(
    "--cik",
    required=True,
    help="Company CIK number, with or without leading zeros.",
)

parser.add_argument(
    "--slug",
    required=True,
    help="Short lowercase filename label, such as apple or microsoft.",
)

args = parser.parse_args()

cik = args.cik.zfill(10)

url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

headers = {
    "User-Agent": "Gregory Christenson your-email@example.com",
    "Accept-Encoding": "gzip, deflate",
}

response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()

data = response.json()

output_path = Path("data/raw") / f"{args.slug}_companyfacts.json"
output_path.write_text(response.text, encoding="utf-8")

print(f"Saved raw SEC data to: {output_path}")
print(f"Company: {data['entityName']}")
print(f"CIK: {data['cik']}")