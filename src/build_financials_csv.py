import argparse
import json
from pathlib import Path

import pandas as pd


parser = argparse.ArgumentParser(
    description="Create a clean financial CSV from SEC company facts."
)

parser.add_argument(
    "--input",
    required=True,
    help="Path to a raw SEC company-facts JSON file.",
)

parser.add_argument(
    "--output",
    required=True,
    help="Path for the cleaned financial CSV file.",
)

args = parser.parse_args()

RAW_DATA_PATH = Path(args.input)
OUTPUT_PATH = Path(args.output)

FACT_TAGS = {
    "revenue": "RevenueFromContractWithCustomerExcludingAssessedTax",
    "net_income": "NetIncomeLoss",
    "total_assets": "Assets",
    "total_liabilities": "Liabilities",
    "shareholders_equity": "StockholdersEquity",
    "current_assets": "AssetsCurrent",
    "current_liabilities": "LiabilitiesCurrent",
}


def get_recent_annual_end_dates(facts, number_of_years=2):
    """Find the two most recent annual 10-K reporting dates."""
    revenue_entries = facts[
        "RevenueFromContractWithCustomerExcludingAssessedTax"
    ]["units"]["USD"]

    annual_entries = []

    for entry in revenue_entries:
        if (
            entry.get("form") == "10-K"
            and entry.get("fp") == "FY"
            and "start" in entry
        ):
            duration_days = (
                pd.Timestamp(entry["end"]) - pd.Timestamp(entry["start"])
            ).days

            if 330 <= duration_days <= 380:
                annual_entries.append(entry)

    unique_end_dates = {entry["end"] for entry in annual_entries}

    return sorted(unique_end_dates, reverse=True)[:number_of_years]


def get_fact_value(facts, tag, end_date):
    """Return one annual 10-K value for a given XBRL tag and period end date."""
    fact_entries = facts[tag]["units"]["USD"]

    matches = [
        entry
        for entry in fact_entries
        if entry.get("form") == "10-K" and entry.get("end") == end_date
    ]

    if not matches:
        raise ValueError(f"No 10-K value found for {tag} ending {end_date}")

    latest_filed_match = max(matches, key=lambda entry: entry["filed"])
    return latest_filed_match["val"]


with RAW_DATA_PATH.open(encoding="utf-8") as file:
    sec_data = json.load(file)

us_gaap_facts = sec_data["facts"]["us-gaap"]
recent_end_dates = get_recent_annual_end_dates(us_gaap_facts)

print(f"Company: {sec_data['entityName']}")
print("Detected fiscal year ends:", ", ".join(recent_end_dates))

rows = []

for end_date in recent_end_dates:
    row = {
        "company": sec_data["entityName"].title(),
        "year": int(end_date[:4]),
        "fiscal_year_end": end_date,
    }

    for column_name, xbrl_tag in FACT_TAGS.items():
        value_in_dollars = get_fact_value(
            us_gaap_facts,
            xbrl_tag,
            end_date,
        )

        row[column_name] = value_in_dollars / 1_000_000

    rows.append(row)

financials = pd.DataFrame(rows).sort_values("year", ascending=False)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
financials.to_csv(OUTPUT_PATH, index=False)

print(f"Created: {OUTPUT_PATH}")
print(financials.to_string(index=False))