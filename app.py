import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Financial Dashboard", layout="wide")

financials = pd.read_csv(
    "data/processed/peer_financials.csv",
    parse_dates=["fiscal_year_end"],
)

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

companies = sorted(financials["company"].unique())

st.title("Financial Statement Insights Dashboard")
st.caption("Source: SEC company facts. Amounts are shown in USD millions.")
st.subheader("Latest Reported Peer Comparison")

latest_by_company = (
    financials.sort_values("fiscal_year_end", ascending=False)
    .groupby("company")
    .head(1)
    .sort_values("company")
    .copy()
)

peer_comparison = latest_by_company[
    [
        "company",
        "fiscal_year_end",
        "revenue",
        "net_income",
        "net_profit_margin",
        "return_on_assets",
        "debt_to_equity",
        "current_ratio",
    ]
].copy()

peer_comparison["fiscal_year_end"] = peer_comparison[
    "fiscal_year_end"
].dt.strftime("%b %d, %Y")

peer_comparison["revenue"] = peer_comparison["revenue"].map(
    lambda value: f"${value / 1000:.1f}B"
)

peer_comparison["net_income"] = peer_comparison["net_income"].map(
    lambda value: f"${value / 1000:.1f}B"
)

peer_comparison["net_profit_margin"] = peer_comparison[
    "net_profit_margin"
].map("{:.2%}".format)

peer_comparison["return_on_assets"] = peer_comparison[
    "return_on_assets"
].map("{:.2%}".format)

peer_comparison["debt_to_equity"] = peer_comparison[
    "debt_to_equity"
].map("{:.2f}".format)

peer_comparison["current_ratio"] = peer_comparison[
    "current_ratio"
].map("{:.2f}".format)

peer_comparison = peer_comparison.rename(
    columns={
        "company": "Company",
        "fiscal_year_end": "Fiscal Year End",
        "revenue": "Revenue",
        "net_income": "Net Income",
        "net_profit_margin": "Net Profit Margin",
        "return_on_assets": "Return on Assets",
        "debt_to_equity": "Debt-to-Equity",
        "current_ratio": "Current Ratio",
    }
)

st.dataframe(peer_comparison, use_container_width=True, hide_index=True)

st.caption(
    "Fiscal year-end dates differ by company; compare the dates before "
    "drawing conclusions from the latest reported values."
    
)
st.subheader("Peer Ratio Comparison")

ratio_options = {
    "Net Profit Margin": "net_profit_margin",
    "Return on Assets": "return_on_assets",
    "Debt-to-Equity": "debt_to_equity",
    "Current Ratio": "current_ratio",
}

selected_ratio_label = st.selectbox(
    "Choose a ratio to compare",
    list(ratio_options.keys()),
)

selected_ratio_column = ratio_options[selected_ratio_label]

peer_chart_data = latest_by_company.copy()

if selected_ratio_column in ["net_profit_margin", "return_on_assets"]:
    peer_chart_data["display_value"] = peer_chart_data[
        selected_ratio_column
    ].map("{:.2%}".format)
else:
    peer_chart_data["display_value"] = peer_chart_data[
        selected_ratio_column
    ].map("{:.2f}".format)

peer_fig = px.bar(
    peer_chart_data,
    x="company",
    y=selected_ratio_column,
    color="company",
    text="display_value",
    title=f"Latest Reported {selected_ratio_label}",
    labels={
        "company": "Company",
        selected_ratio_column: selected_ratio_label,
    },
)

peer_fig.update_layout(showlegend=False)
peer_fig.update_traces(textposition="outside")

if selected_ratio_column in ["net_profit_margin", "return_on_assets"]:
    peer_fig.update_yaxes(tickformat=".0%")

st.plotly_chart(peer_fig, use_container_width=True)

selected_company = st.selectbox(
    "Choose a company",
    companies,
)

company_financials = financials[
    financials["company"] == selected_company
].sort_values("fiscal_year_end", ascending=False)

latest = company_financials.iloc[0]
previous = company_financials.iloc[1]

st.subheader(
    f"{selected_company}: Fiscal Year Ended "
    f"{latest['fiscal_year_end'].strftime('%B %d, %Y')}"
)

st.subheader("Key Ratios")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Net Profit Margin",
    f"{latest['net_profit_margin']:.2%}",
    f"{latest['net_profit_margin'] - previous['net_profit_margin']:+.2%} pts",
)

col2.metric(
    "Return on Assets",
    f"{latest['return_on_assets']:.2%}",
    f"{latest['return_on_assets'] - previous['return_on_assets']:+.2%} pts",
)

col3.metric(
    "Debt-to-Equity",
    f"{latest['debt_to_equity']:.2f}",
    f"{latest['debt_to_equity'] - previous['debt_to_equity']:+.2f}",
    delta_color="inverse",
)

col4.metric(
    "Current Ratio",
    f"{latest['current_ratio']:.2f}",
    f"{latest['current_ratio'] - previous['current_ratio']:+.2f}",
)

revenue_growth = latest["revenue"] / previous["revenue"] - 1
net_income_growth = latest["net_income"] / previous["net_income"] - 1
margin_change = latest["net_profit_margin"] - previous["net_profit_margin"]

st.subheader("Key Takeaways")

st.write(
    f"""
- **Revenue growth:** Revenue increased from
  ${previous["revenue"] / 1000:.1f}B to
  ${latest["revenue"] / 1000:.1f}B, representing
  **{revenue_growth:.1%} growth**.

- **Earnings growth:** Net income changed by
  **{net_income_growth:.1%}**. Net profit margin changed by
  **{margin_change:.2%} percentage points**.

- **Leverage:** Debt-to-equity changed from
  **{previous["debt_to_equity"]:.2f}** to
  **{latest["debt_to_equity"]:.2f}**.

- **Liquidity:** The current ratio is
  **{latest["current_ratio"]:.2f}**.
"""
)

st.subheader("Financial Summary")

display_data = company_financials[
    [
        "year",
        "fiscal_year_end",
        "revenue",
        "net_income",
        "net_profit_margin",
        "return_on_assets",
        "debt_to_equity",
        "current_ratio",
    ]
].copy()

display_data["fiscal_year_end"] = display_data["fiscal_year_end"].dt.strftime(
    "%b %d, %Y"
)

display_data["revenue"] = display_data["revenue"].map(
    lambda value: f"${value / 1000:.1f}B"
)

display_data["net_income"] = display_data["net_income"].map(
    lambda value: f"${value / 1000:.1f}B"
)

display_data["net_profit_margin"] = display_data["net_profit_margin"].map(
    "{:.2%}".format
)

display_data["return_on_assets"] = display_data["return_on_assets"].map(
    "{:.2%}".format
)

display_data["debt_to_equity"] = display_data["debt_to_equity"].map(
    "{:.2f}".format
)

display_data["current_ratio"] = display_data["current_ratio"].map(
    "{:.2f}".format
)

display_data = display_data.rename(
    columns={
        "year": "Fiscal Year",
        "fiscal_year_end": "Fiscal Year End",
        "revenue": "Revenue",
        "net_income": "Net Income",
        "net_profit_margin": "Net Profit Margin",
        "return_on_assets": "Return on Assets",
        "debt_to_equity": "Debt-to-Equity",
        "current_ratio": "Current Ratio",
    }
)

st.dataframe(display_data, use_container_width=True, hide_index=True)

chart_data = company_financials.melt(
    id_vars=["company", "year"],
    value_vars=["revenue", "net_income"],
    var_name="metric",
    value_name="amount",
)

chart_data["metric"] = chart_data["metric"].replace(
    {
        "revenue": "Revenue",
        "net_income": "Net Income",
    }
)

fig = px.bar(
    chart_data,
    x="year",
    y="amount",
    color="metric",
    barmode="group",
    title=f"{selected_company}: Revenue and Net Income",
    labels={
        "year": "Fiscal Year",
        "amount": "USD millions",
        "metric": "Metric",
    },
)

st.plotly_chart(fig, use_container_width=True)