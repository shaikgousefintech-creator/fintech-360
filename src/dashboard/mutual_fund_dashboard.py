
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = (
    BASE_DIR
    / "data"
    / "warehouse"
    / "database"
    / "fintech360.db"
)

st.set_page_config(
    page_title="FINTECH 360 | Mutual Funds",
    page_icon="📊",
    layout="wide"
)


# ==================================================
# 2. DATA LOADING
# ==================================================

@st.cache_data
def load_data():

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    with sqlite3.connect(DB_PATH) as conn:

        transactions = pd.read_sql_query(
            """
            SELECT
                t.*,
                i.investor_name,
                i.investor_segment,
                i.city,
                s.scheme_name,
                s.fund_house,
                s.fund_category,
                s.risk_level,
                s.expense_ratio

            FROM mf_transactions t

            LEFT JOIN mf_investors i
                ON t.investor_id = i.investor_id

            LEFT JOIN mf_schemes s
                ON t.scheme_id = s.scheme_id
            """,
            conn
        )

    transactions["transaction_date"] = pd.to_datetime(
        transactions["transaction_date"],
        errors="coerce"
    )

    numeric_columns = [
        "amount",
        "nav",
        "units",
        "expense_ratio"
    ]

    for column in numeric_columns:
        transactions[column] = pd.to_numeric(
            transactions[column],
            errors="coerce"
        )

    return transactions


try:
    transactions = load_data()

except Exception as error:
    st.error(f"Unable to load dashboard data: {error}")
    st.stop()


# ==================================================
# 3. DASHBOARD HEADER
# ==================================================

st.title("FINTECH 360°")

st.header("Mutual Funds Analytics Dashboard")

st.caption(
    "End-to-End Financial Data Engineering, "
    "Analytics and Business Intelligence Platform"
)

st.divider()


# ==================================================
# 4. SIDEBAR FILTERS
# ==================================================

st.sidebar.header("Dashboard Filters")

valid_dates = transactions[
    "transaction_date"
].dropna()

if valid_dates.empty:
    st.error("No valid transaction dates found.")
    st.stop()

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

st.sidebar.subheader("Transaction Date Range")

start_date = st.sidebar.date_input(
    "Start Date",
    value=min_date,
    min_value=min_date,
    max_value=max_date,
    key="mf_start_date"
)

end_date = st.sidebar.date_input(
    "End Date",
    value=max_date,
    min_value=min_date,
    max_value=max_date,
    key="mf_end_date"
)

if start_date > end_date:
    st.sidebar.error(
        "Start Date cannot be after End Date."
    )
    st.stop()

st.sidebar.divider()

segments = sorted(
    transactions["investor_segment"].dropna().unique()
)

selected_segments = st.sidebar.multiselect(
    "Investor Segment",
    segments,
    default=segments
)

categories = sorted(
    transactions["fund_category"].dropna().unique()
)

selected_categories = st.sidebar.multiselect(
    "Fund Category",
    categories,
    default=categories
)

schemes = sorted(
    transactions["scheme_name"].dropna().unique()
)

selected_schemes = st.sidebar.multiselect(
    "Mutual Fund Schemes",
    schemes,
    default=schemes
)

modes = sorted(
    transactions["investment_mode"].dropna().unique()
)

selected_modes = st.sidebar.multiselect(
    "Investment Mode",
    modes,
    default=modes
)

st.sidebar.divider()

st.sidebar.caption(
    "FINTECH 360° | Mutual Funds Module"
)


# ==================================================
# 5. APPLY FILTERS
# ==================================================

start_timestamp = pd.Timestamp(start_date)

end_timestamp = (
    pd.Timestamp(end_date)
    + pd.Timedelta(days=1)
)

filtered = transactions[
    (transactions["transaction_date"] >= start_timestamp)
    & (transactions["transaction_date"] < end_timestamp)
    & (transactions["investor_segment"].isin(selected_segments))
    & (transactions["fund_category"].isin(selected_categories))
    & (transactions["scheme_name"].isin(selected_schemes))
    & (transactions["investment_mode"].isin(selected_modes))
].copy()

st.write(
    f"Showing transactions from "
    f"{start_date.strftime('%d %b %Y')} to "
    f"{end_date.strftime('%d %b %Y')}"
)

st.write(f"Filtered Records: {len(filtered):,}")


# ==================================================
# 6. KEY PERFORMANCE INDICATORS
# ==================================================

st.header("Key Performance Indicators")

total_transactions = len(filtered)

total_investors = filtered[
    "investor_id"
].nunique()

successful = filtered[
    filtered["transaction_status"] == "SUCCESS"
]

failed = filtered[
    filtered["transaction_status"] == "FAILED"
]

purchase = successful[
    successful["transaction_type"] == "PURCHASE"
]

redemption = successful[
    successful["transaction_type"] == "REDEMPTION"
]

total_purchase = purchase["amount"].sum()

total_redemption = redemption["amount"].sum()

net_investment = (
    total_purchase - total_redemption
)

success_rate = (
    len(successful) / total_transactions * 100
    if total_transactions > 0 else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Investors",
    f"{total_investors:,}"
)

col2.metric(
    "Total Transactions",
    f"{total_transactions:,}"
)

col3.metric(
    "Purchase Amount",
    f"₹{total_purchase:,.2f}"
)

col4.metric(
    "Redemption Amount",
    f"₹{total_redemption:,.2f}"
)

col5, col6, col7, col8 = st.columns(4)

col5.metric(
    "Net Investment",
    f"₹{net_investment:,.2f}"
)

col6.metric(
    "Successful Transactions",
    f"{len(successful):,}"
)

col7.metric(
    "Failed Transactions",
    f"{len(failed):,}"
)

col8.metric(
    "Success Rate",
    f"{success_rate:.2f}%"
)

st.divider()


# ==================================================
# 7. INVESTOR BEHAVIOUR ANALYSIS
# ==================================================

st.header("Investor Behaviour Analysis")

left, right = st.columns(2)

with left:

    st.subheader("Investor Segment Distribution")

    segment_data = (
        filtered.groupby("investor_segment")
        .agg(
            total_investors=("investor_id", "nunique")
        )
        .reset_index()
    )

    if not segment_data.empty:

        fig = px.pie(
            segment_data,
            names="investor_segment",
            values="total_investors",
            hole=0.45,
            title="Investors by Segment"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("No investor data available.")

with right:

    st.subheader("Top 10 Investors")

    investor_data = filtered.copy()

    investor_data["purchase_amount"] = (
        investor_data["amount"].where(
            (investor_data["transaction_status"] == "SUCCESS")
            & (investor_data["transaction_type"] == "PURCHASE"),
            0
        )
    )

    investor_data["redemption_amount"] = (
        investor_data["amount"].where(
            (investor_data["transaction_status"] == "SUCCESS")
            & (investor_data["transaction_type"] == "REDEMPTION"),
            0
        )
    )

    investor_data = (
        investor_data.groupby(
            ["investor_id", "investor_name", "investor_segment"],
            as_index=False
        )
        .agg(
            total_purchase_amount=("purchase_amount", "sum"),
            total_redemption_amount=("redemption_amount", "sum")
        )
    )

    investor_data["net_investment_amount"] = (
        investor_data["total_purchase_amount"]
        - investor_data["total_redemption_amount"]
    )

    top_investors = investor_data.nlargest(
        10,
        "net_investment_amount"
    )

    if not top_investors.empty:

        fig = px.bar(
            top_investors.sort_values(
                "net_investment_amount",
                ascending=True
            ),
            x="net_investment_amount",
            y="investor_name",
            color="investor_segment",
            orientation="h",
            title="Top Investors by Net Investment",
            labels={
                "net_investment_amount": "Net Investment (₹)",
                "investor_name": "Investor"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("No investor data available.")


# ==================================================
# 8. MUTUAL FUND SCHEME PERFORMANCE
# ==================================================

st.divider()

st.header("Mutual Fund Scheme Performance")

scheme_data = filtered.copy()

scheme_data["purchase_amount"] = (
    scheme_data["amount"].where(
        (scheme_data["transaction_status"] == "SUCCESS")
        & (scheme_data["transaction_type"] == "PURCHASE"),
        0
    )
)

scheme_data["redemption_amount"] = (
    scheme_data["amount"].where(
        (scheme_data["transaction_status"] == "SUCCESS")
        & (scheme_data["transaction_type"] == "REDEMPTION"),
        0
    )
)

scheme_data["is_successful"] = (
    scheme_data["transaction_status"] == "SUCCESS"
).astype(int)

scheme_data = (
    scheme_data.groupby(
        ["scheme_name", "fund_house", "fund_category"],
        as_index=False
    )
    .agg(
        total_transactions=("investment_id", "count"),
        successful_transactions=("is_successful", "sum"),
        total_purchase_amount=("purchase_amount", "sum"),
        total_redemption_amount=("redemption_amount", "sum")
    )
)

scheme_data["net_investment_amount"] = (
    scheme_data["total_purchase_amount"]
    - scheme_data["total_redemption_amount"]
)

scheme_data["success_rate_percentage"] = (
    scheme_data["successful_transactions"]
    / scheme_data["total_transactions"].replace(0, pd.NA)
    * 100
).fillna(0)

if not scheme_data.empty:

    left, right = st.columns(2)

    with left:

        st.subheader("Scheme-wise Purchase Amount")

        purchase_chart = scheme_data.sort_values(
            "total_purchase_amount",
            ascending=True
        )

        fig = px.bar(
            purchase_chart,
            x="total_purchase_amount",
            y="scheme_name",
            color="fund_category",
            orientation="h",
            title="Scheme-wise Purchase Amount",
            labels={
                "total_purchase_amount": "Purchase Amount (₹)",
                "scheme_name": "Mutual Fund Scheme",
                "fund_category": "Fund Category"
            },
            height=650
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        st.subheader("Scheme-wise Net Investment")

        net_chart = scheme_data.sort_values(
            "net_investment_amount",
            ascending=True
        )

        fig = px.bar(
            net_chart,
            x="net_investment_amount",
            y="scheme_name",
            color="fund_category",
            orientation="h",
            title="Scheme-wise Net Investment",
            labels={
                "net_investment_amount": "Net Investment (₹)",
                "scheme_name": "Mutual Fund Scheme",
                "fund_category": "Fund Category"
            },
            height=650
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader("Scheme Performance Table")

    st.dataframe(
        scheme_data.sort_values(
            "net_investment_amount",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No scheme data available.")


# ==================================================
# 9. FUND CATEGORY ANALYSIS
# ==================================================

st.divider()

st.header("Fund Category Analysis")

category_data = filtered.copy()

category_data["purchase_amount"] = (
    category_data["amount"].where(
        (category_data["transaction_status"] == "SUCCESS")
        & (category_data["transaction_type"] == "PURCHASE"),
        0
    )
)

category_data["redemption_amount"] = (
    category_data["amount"].where(
        (category_data["transaction_status"] == "SUCCESS")
        & (category_data["transaction_type"] == "REDEMPTION"),
        0
    )
)

category_data = (
    category_data.groupby(
        "fund_category",
        as_index=False
    )
    .agg(
        total_transactions=("investment_id", "count"),
        total_purchase_amount=("purchase_amount", "sum"),
        total_redemption_amount=("redemption_amount", "sum")
    )
)

category_data["net_investment_amount"] = (
    category_data["total_purchase_amount"]
    - category_data["total_redemption_amount"]
)

if not category_data.empty:

    fig = px.bar(
        category_data,
        x="fund_category",
        y="net_investment_amount",
        color="fund_category",
        title="Net Investment by Fund Category",
        labels={
            "fund_category": "Fund Category",
            "net_investment_amount": "Net Investment (₹)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        category_data,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No category data available.")


# ==================================================
# 10. INVESTMENT MODE ANALYSIS
# ==================================================

st.divider()

st.header("Investment Mode Analysis")

mode_data = filtered.copy()

mode_data["mode_label"] = (
    mode_data["investment_mode"].replace({
        "NOT_APPLICABLE": "Redemption"
    })
)

mode_data["successful_amount"] = (
    mode_data["amount"].where(
        mode_data["transaction_status"] == "SUCCESS",
        0
    )
)

mode_data["is_successful"] = (
    mode_data["transaction_status"] == "SUCCESS"
).astype(int)

mode_data["is_failed"] = (
    mode_data["transaction_status"] == "FAILED"
).astype(int)

mode_data = (
    mode_data.groupby(
        "mode_label",
        as_index=False
    )
    .agg(
        total_transactions=("investment_id", "count"),
        successful_transactions=("is_successful", "sum"),
        failed_transactions=("is_failed", "sum"),
        successful_transaction_amount=("successful_amount", "sum")
    )
)

mode_data["success_rate_percentage"] = (
    mode_data["successful_transactions"]
    / mode_data["total_transactions"].replace(0, pd.NA)
    * 100
).fillna(0)

if not mode_data.empty:

    left, right = st.columns(2)

    with left:

        fig = px.bar(
            mode_data,
            x="mode_label",
            y="total_transactions",
            color="mode_label",
            title="Transactions by Investment Mode",
            labels={
                "mode_label": "Transaction Category",
                "total_transactions": "Transactions"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        fig = px.bar(
            mode_data,
            x="mode_label",
            y="successful_transaction_amount",
            color="mode_label",
            title="Successful Transaction Amount by Category",
            labels={
                "mode_label": "Transaction Category",
                "successful_transaction_amount": "Amount (₹)"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.dataframe(
        mode_data,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No investment mode data available.")


# ==================================================
# 11. MONTHLY INVESTMENT TRENDS
# ==================================================

st.divider()

st.header("Monthly Investment Trends")

if not filtered.empty:

    monthly_data = filtered.copy()

    monthly_data = monthly_data[
        monthly_data["transaction_status"] == "SUCCESS"
    ].copy()

    monthly_data["transaction_month"] = (
        monthly_data["transaction_date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_data = (
        monthly_data.groupby(
            ["transaction_month", "transaction_type"],
            as_index=False
        )
        .agg(
            transaction_amount=("amount", "sum")
        )
    )

    if not monthly_data.empty:

        selected_end = pd.Timestamp(end_date)

        month_end = (
            selected_end
            + pd.offsets.MonthEnd(0)
        )

        is_partial_month = (
            end_date == max_date
            and max_date < month_end.date()
        )

        monthly_title = (
            "Monthly Purchase and Redemption Amount"
        )

        if is_partial_month:
            monthly_title += " (Latest Month - Partial Data)"

        fig = px.line(
            monthly_data,
            x="transaction_month",
            y="transaction_amount",
            color="transaction_type",
            markers=True,
            title=monthly_title,
            labels={
                "transaction_month": "Month",
                "transaction_amount": "Amount (₹)",
                "transaction_type": "Transaction Type"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        if is_partial_month:
            st.caption(
                f"Note: The latest month is incomplete. "
                f"Available transaction data ends on "
                f"{max_date.strftime('%d %b %Y')}. "
                "Do not compare it directly with completed months."
            )

    else:
        st.info("No successful transactions available.")

else:
    st.info("No transactions available for the selected filters.")


# ==================================================
# 12. TRANSACTION DATA EXPLORER
# ==================================================

st.divider()

st.header("Transaction Data Explorer")

if not filtered.empty:

    display_columns = [
        "investment_id",
        "investor_id",
        "investor_name",
        "scheme_name",
        "fund_category",
        "transaction_date",
        "transaction_type",
        "investment_mode",
        "amount",
        "nav",
        "units",
        "transaction_status",
        "failure_reason"
    ]

    explorer = filtered[
        display_columns
    ].sort_values(
        "transaction_date",
        ascending=False
    )

    st.dataframe(
        explorer,
        use_container_width=True,
        hide_index=True
    )

    csv_data = explorer.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Filtered Transactions",
        data=csv_data,
        file_name="mutual_fund_filtered_transactions.csv",
        mime="text/csv"
    )

else:
    st.info(
        "No transactions match the selected filters."
    )


# ==================================================
# 13. FOOTER
# ==================================================

st.divider()

st.caption(
    "FINTECH 360° | Mutual Funds Analytics | "
    "Built with Python, SQLite, Pandas, Streamlit and Plotly"
)

st.caption(
    "Note: This dashboard analyses synthetic transaction activity. "
    "Net investment is not investment return or actual AUM."
)
