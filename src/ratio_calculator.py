import pandas as pd

financials = pd.read_csv("data/processed/apple_financials.csv")

financials["net_profit_margin"] = (
    financials["net_income"] / financials["revenue"]
)

financials["return_on_assets"] = (
    financials["net_income"] / financials["total_assets"]
)

financials["debt_to_equity"] = (
    financials["total_liabilities"] / financials["shareholders_equity"]
)

financials["current_ratio"] = (
    financials["current_assets"] / financials["current_liabilities"]
)

results = financials[
    [
        "company",
        "year",
        "net_profit_margin",
        "return_on_assets",
        "debt_to_equity",
        "current_ratio",
    ]
].copy()

results["net_profit_margin"] = results["net_profit_margin"].map("{:.2%}".format)
results["return_on_assets"] = results["return_on_assets"].map("{:.2%}".format)
results["debt_to_equity"] = results["debt_to_equity"].map("{:.2f}".format)
results["current_ratio"] = results["current_ratio"].map("{:.2f}".format)

print("\nApple financial-ratio analysis\n")
print(results.to_string(index=False))