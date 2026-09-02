from pathlib import Path

import pandas as pd

APPLE_PATH = Path("data/processed/apple_financials.csv")
MICROSOFT_PATH = Path("data/processed/microsoft_financials.csv")
OUTPUT_PATH = Path("data/processed/peer_financials.csv")

apple = pd.read_csv(APPLE_PATH)
microsoft = pd.read_csv(MICROSOFT_PATH)

peer_financials = pd.concat(
    [apple, microsoft],
    ignore_index=True,
)

peer_financials = peer_financials.sort_values(
    ["company", "fiscal_year_end"],
    ascending=[True, False],
)

peer_financials.to_csv(OUTPUT_PATH, index=False)

print(f"Created: {OUTPUT_PATH}")
print(peer_financials.to_string(index=False))