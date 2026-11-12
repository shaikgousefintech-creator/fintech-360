
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px


# ==========================================================
# 1. CONFIGURATION
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = (
    PROJECT_ROOT
    / "data"
    / "warehouse"
    / "database"
    / "fintech360.db"
)

st.set_page_config(
    page_title="FINTECH 360 | UPI Analytics",
    page_icon="💳",
    layout="wide"
)


# ==========================================================
# 2. DATABASE CONNECTION
# ==========================================================

@st.cache_data
def load_data():

    with sqlite3.connect(DB_PATH) as db:

        transactions = pd.read_sql_query(
            "SELECT * FROM upi_transactions",
            db
        )

        daily = pd.read_sql_query(
            "SELECT * FROM mart_upi_daily_performance",
            db
        )

        banks = pd.read_sql_query(
            "SELECT * FROM mart_upi_bank_performance",
            db
        )

        apps = pd.read_sql_query(
            "SELECT * FROM mart_upi_payment_app_performance",
            db
        )

    return transactions, daily, banks, apps


transactions, daily, banks, apps = load_data()


# ==========================================================
# 3. PREPARE TRANSACTION DATA
# ==========================================================

if transactions.empty:
    st.error("No UPI transaction data available in the database.")
    st.stop()

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"],
    errors="coerce"
)

transactions["amount"] = pd.to_numeric(
    transactions["amount"],
    errors="coerce"
).fillna(0)

transactions = transactions.dropna(
    subset=["transaction_date"]
).copy()

if transactions.empty:
    st.error("No valid transaction dates found.")
    st.stop()

transactions["transaction_day"] = (
    transactions["transaction_date"].dt.normalize()
)

start_date = transactions["transaction_day"].min().date()
end_date = transactions["transaction_day"].max().date()


# ==========================================================
# 4. FINTECH 360° THEME
# ==========================================================

st.markdown(
    """
<style>

/* ------------------------------------------
   FINTECH 360° BRAND COLOURS
------------------------------------------ */

:root {
    --fintech-navy: #10243a;
    --fintech-blue: #183e5c;
    --fintech-teal: #176b75;
    --fintech-accent: #9edce0;
    --fintech-text: #e3edf5;
    --fintech-muted: #c2d4e1;
}

/* ------------------------------------------
   MAIN APPLICATION
   Matching Portfolio Overview dark theme
------------------------------------------ */

.stApp {
    background-color: #1e1e1e;
    color: #e3edf5;
}

[data-testid="stHeader"] {
    background-color: #1e1e1e;
}

[data-testid="stSidebar"] {
    background-color: #1e1e1e;
    border-right: 1px solid #344354;
}

/* ------------------------------------------
   HERO HEADER
------------------------------------------ */

.fintech-hero {
    box-sizing: border-box;
    width: 100%;
    padding: 2.2rem 2rem;
    border-radius: 18px;

    background: linear-gradient(
        120deg,
        #10243a 0%,
        #183e5c 55%,
        #176b75 100%
    );

    border: 1px solid rgba(158, 220, 224, 0.16);
    color: #ffffff;
    margin: 0 0 1.5rem 0;
}

.fintech-hero-kicker {
    color: #9edce0;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0 0 0.6rem 0;
}

.fintech-hero h1 {
    color: #ffffff !important;
    font-size: 2.65rem;
    font-weight: 700;
    margin: 0;
    padding: 0;
    line-height: 1.2;
}

.fintech-hero-subtitle {
    color: #d9e8f1;
    font-size: 1.12rem;
    margin: 0.8rem 0 0.4rem 0;
}

.fintech-hero-description {
    color: #c2d4e1;
    font-size: 0.96rem;
    max-width: 850px;
    line-height: 1.65;
    margin: 0;
}

/* ------------------------------------------
   DATE RANGE FILTERS
   Target the actual BaseWeb input wrapper
------------------------------------------ */

[data-testid="stSidebar"] [data-testid="stDateInput"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-testid="stDateInput"] [data-baseweb="input"] > div {
    background-color: #10243a !important;
    border: 1px solid #176b75 !important;
    border-radius: 8px !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] [data-testid="stDateInput"] input {
    background-color: #10243a !important;
    color: #e3edf5 !important;
    -webkit-text-fill-color: #e3edf5 !important;
    border: none !important;
    color-scheme: dark !important;
}

[data-testid="stSidebar"] [data-testid="stDateInput"] button {
    color: #9edce0 !important;
}

[data-testid="stSidebar"] [data-testid="stDateInput"] button svg {
    fill: #9edce0 !important;
}

[data-testid="stSidebar"] [data-testid="stDateInput"] label {
    color: #d9e8f1 !important;
}

[data-testid="stSidebar"] [data-testid="stDateInput"] [data-baseweb="input"]:focus-within,
[data-testid="stSidebar"] [data-testid="stDateInput"] [data-baseweb="input"] > div:focus-within {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 1px #38bdf8 !important;
}

/* ------------------------------------------
   BANK AND PAYMENT APP MULTISELECT FILTERS
------------------------------------------ */

[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
    background-color: #10243a !important;
    border: 1px solid #176b75 !important;
    border-radius: 8px !important;
}

/* Selected chips */

[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background-color: #176b75 !important;
    border: 1px solid #38bdf8 !important;
    color: #ffffff !important;
}

/* Chip text and remove icon */

[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="tag"] * {
    color: #ffffff !important;
    fill: #ffffff !important;
}

/* ------------------------------------------
   SIDEBAR LABELS AND HEADINGS
------------------------------------------ */

[data-testid="stSidebar"] label {
    color: #d9e8f1 !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #e3edf5 !important;
}

/* ------------------------------------------
   KPI CARDS
------------------------------------------ */

[data-testid="stMetric"] {
    background: linear-gradient(
        135deg,
        #172b40,
        #1b3d50
    );

    border: 1px solid #31566b;
    padding: 18px;
    border-radius: 12px;
}

[data-testid="stMetricLabel"] {
    color: #c2d4e1 !important;
}

[data-testid="stMetricValue"] {
    color: #e3edf5 !important;
}

/* ------------------------------------------
   HEADINGS AND CAPTIONS
------------------------------------------ */

h1, h2, h3, h4 {
    color: #e3edf5 !important;
}

[data-testid="stCaptionContainer"] {
    color: #aabac9 !important;
}

/* ------------------------------------------
   DATAFRAMES
------------------------------------------ */

[data-testid="stDataFrame"] {
    border: 1px solid #344b60;
    border-radius: 10px;
}

/* ------------------------------------------
   DOWNLOAD BUTTON
------------------------------------------ */

.stDownloadButton button {
    background: linear-gradient(
        120deg,
        #183e5c,
        #176b75
    );

    color: #ffffff !important;
    border: 1px solid #38bdf8;
    border-radius: 8px;
}

.stDownloadButton button:hover {
    background: #176b75;
    color: #ffffff !important;
    border-color: #9edce0;
}

/* ------------------------------------------
   DIVIDERS
------------------------------------------ */

hr {
    border-color: #344354 !important;
}

</style>
""",
    unsafe_allow_html=True
)


# ==========================================================
# 5. DASHBOARD HEADER
# Important: HTML lines start at the beginning of the string.
# This prevents Streamlit from displaying them as code.
# ==========================================================

st.markdown(
    """<div class="fintech-hero">
<div class="fintech-hero-kicker">FINANCIAL DATA PLATFORM · BUSINESS ANALYTICS</div>
<h1>FINTECH 360°</h1>
<div class="fintech-hero-subtitle">UPI Payments Analytics Dashboard</div>
<div class="fintech-hero-description">End-to-End Financial Data Engineering, Analytics &amp; Business Intelligence Platform</div>
</div>""",
    unsafe_allow_html=True
)

st.divider()


# ==========================================================
# 6. SIDEBAR FILTERS
# ==========================================================

st.sidebar.header("Dashboard Filters")

st.sidebar.subheader("Transaction Date Range")

selected_start_date = st.sidebar.date_input(
    "Start Date",
    value=start_date,
    min_value=start_date,
    max_value=end_date,
    key="upi_start_date"
)

selected_end_date = st.sidebar.date_input(
    "End Date",
    value=end_date,
    min_value=start_date,
    max_value=end_date,
    key="upi_end_date"
)

if selected_start_date > selected_end_date:

    st.sidebar.error(
        "Start Date cannot be greater than End Date."
    )

    st.stop()

st.sidebar.divider()

available_banks = sorted(
    transactions["payer_bank"].dropna().unique().tolist()
)

selected_banks = st.sidebar.multiselect(
    "Select Banks",
    options=available_banks,
    default=available_banks,
    key="upi_bank_filter"
)

available_apps = sorted(
    transactions["payment_app"].dropna().unique().tolist()
)

selected_apps = st.sidebar.multiselect(
    "Select Payment Apps",
    options=available_apps,
    default=available_apps,
    key="upi_app_filter"
)


# ==========================================================
# 7. FILTER TRANSACTIONS
# ==========================================================

start_timestamp = pd.Timestamp(selected_start_date)

end_timestamp = (
    pd.Timestamp(selected_end_date)
    + pd.Timedelta(days=1)
)

filtered = transactions[
    (transactions["transaction_date"] >= start_timestamp)
    & (transactions["transaction_date"] < end_timestamp)
    & (transactions["payer_bank"].isin(selected_banks))
    & (transactions["payment_app"].isin(selected_apps))
].copy()

st.caption(
    f"Showing transactions from "
    f"{selected_start_date.strftime('%d %b %Y')} "
    f"to {selected_end_date.strftime('%d %b %Y')}"
)

st.caption(
    f"Filtered Records: {len(filtered):,}"
)


# ==========================================================
# 8. CALCULATE KPIs
# ==========================================================

total_transactions = len(filtered)

successful = (
    filtered["status"] == "SUCCESS"
).sum()

failed = (
    filtered["status"] == "FAILED"
).sum()

pending = (
    filtered["status"] == "PENDING"
).sum()

total_value = filtered["amount"].sum()

successful_value = filtered.loc[
    filtered["status"] == "SUCCESS",
    "amount"
].sum()

success_rate = (
    successful / total_transactions * 100
    if total_transactions > 0
    else 0
)


# ==========================================================
# 9. KPI CARDS
# ==========================================================

st.header("Key Performance Indicators")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Transactions",
    f"{total_transactions:,}"
)

c2.metric(
    "Total Transaction Value",
    f"₹{total_value:,.2f}"
)

c3.metric(
    "Successful Transactions",
    f"{successful:,}"
)

c4.metric(
    "Success Rate",
    f"{success_rate:.2f}%"
)

c5, c6, c7 = st.columns(3)

c5.metric(
    "Failed Transactions",
    f"{failed:,}"
)

c6.metric(
    "Pending Transactions",
    f"{pending:,}"
)

c7.metric(
    "Successful Transaction Value",
    f"₹{successful_value:,.2f}"
)

st.divider()


# ==========================================================
# 10. DAILY TRANSACTION TRENDS
# ==========================================================

st.header("Daily Transaction Trends")

if not filtered.empty:

    daily_trend = (
        filtered
        .groupby("transaction_day")
        .agg(
            total_transactions=("transaction_id", "count"),
            transaction_value=("amount", "sum")
        )
        .reset_index()
        .sort_values("transaction_day")
    )

    fig = px.bar(
        daily_trend,
        x="transaction_day",
        y="total_transactions",
        title="Daily Transaction Volume",
        text="total_transactions",
        labels={
            "transaction_day": "Date",
            "total_transactions": "Total Transactions"
        }
    )

    fig.update_xaxes(
        type="date",
        tickformat="%d %b %Y"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig = px.line(
        daily_trend,
        x="transaction_day",
        y="transaction_value",
        title="Daily Transaction Value",
        markers=True,
        labels={
            "transaction_day": "Date",
            "transaction_value": "Transaction Value (₹)"
        }
    )

    fig.update_xaxes(
        type="date",
        tickformat="%d %b %Y"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info("No transactions available for selected filters.")


# ==========================================================
# 11. TRANSACTION STATUS ANALYSIS
# ==========================================================

st.header("Transaction Status Analysis")

status_data = pd.DataFrame({
    "Status": ["SUCCESS", "FAILED", "PENDING"],
    "Transactions": [successful, failed, pending]
})

col1, col2 = st.columns(2)

with col1:

    fig = px.pie(
        status_data,
        names="Status",
        values="Transactions",
        title="Transaction Status Distribution",
        hole=0.45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.bar(
        status_data,
        x="Status",
        y="Transactions",
        title="Transaction Status Count",
        text_auto=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==========================================================
# 12. BANK PERFORMANCE
# ==========================================================

st.header("Bank Performance Analysis")

if not filtered.empty:

    bank_data = (
        filtered.groupby("payer_bank")
        .agg(
            total_transactions=("transaction_id", "count"),
            transaction_value=("amount", "sum"),
            successful_transactions=("is_successful", "sum")
        )
        .reset_index()
    )

    bank_data["success_rate"] = (
        bank_data["successful_transactions"]
        / bank_data["total_transactions"] * 100
    )

    fig = px.bar(
        bank_data.sort_values(
            "total_transactions",
            ascending=False
        ),
        x="payer_bank",
        y="total_transactions",
        color="success_rate",
        title="Bank-wise Transaction Volume",
        text_auto=True,
        labels={
            "payer_bank": "Bank",
            "total_transactions": "Total Transactions",
            "success_rate": "Success Rate (%)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig = px.bar(
        bank_data,
        x="payer_bank",
        y="success_rate",
        title="Bank-wise Success Rate",
        text_auto=".2f",
        labels={
            "payer_bank": "Bank",
            "success_rate": "Success Rate (%)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info("No bank performance data available.")


# ==========================================================
# 13. PAYMENT APP PERFORMANCE
# ==========================================================

st.header("Payment App Performance")

if not filtered.empty:

    app_data = (
        filtered.groupby("payment_app")
        .agg(
            total_transactions=("transaction_id", "count"),
            transaction_value=("amount", "sum"),
            successful_transactions=("is_successful", "sum")
        )
        .reset_index()
    )

    app_data["success_rate"] = (
        app_data["successful_transactions"]
        / app_data["total_transactions"] * 100
    )

    fig = px.bar(
        app_data.sort_values(
            "total_transactions",
            ascending=False
        ),
        x="payment_app",
        y="total_transactions",
        color="success_rate",
        title="Payment App Transaction Comparison",
        text_auto=True,
        labels={
            "payment_app": "Payment App",
            "total_transactions": "Total Transactions",
            "success_rate": "Success Rate (%)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig = px.bar(
        app_data,
        x="payment_app",
        y="success_rate",
        title="Payment App Success Rate",
        text_auto=".2f",
        labels={
            "payment_app": "Payment App",
            "success_rate": "Success Rate (%)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info("No payment app performance data available.")


# ==========================================================
# 14. UPI FAILURE ANALYSIS
# ==========================================================

st.divider()

st.header("UPI Failure Analysis")

failed_data = filtered[
    filtered["status"] == "FAILED"
].copy()

if not failed_data.empty:

    # ----------------------------------------------
    # 14.1 FAILURE REASON ANALYSIS
    # ----------------------------------------------

    st.subheader("Failure Reason Analysis")

    failed_data["failure_reason"] = (
        failed_data["failure_reason"]
        .fillna("UNKNOWN")
        .replace("", "UNKNOWN")
    )

    failure_reason_data = (
        failed_data.groupby("failure_reason")
        .agg(
            failed_transactions=("transaction_id", "count"),
            failed_transaction_value=("amount", "sum")
        )
        .reset_index()
        .sort_values(
            "failed_transactions",
            ascending=False
        )
    )

    failure_reason_data["failure_percentage"] = (
        failure_reason_data["failed_transactions"]
        / len(failed_data) * 100
    ).round(2)

    fig = px.bar(
        failure_reason_data,
        x="failure_reason",
        y="failed_transactions",
        color="failure_percentage",
        title="Failed Transactions by Reason",
        text="failed_transactions",
        labels={
            "failure_reason": "Failure Reason",
            "failed_transactions": "Failed Transactions",
            "failure_percentage": "Failure (%)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        failure_reason_data,
        use_container_width=True,
        hide_index=True
    )

    # ----------------------------------------------
    # 14.2 BANK FAILURE ANALYSIS
    # ----------------------------------------------

    st.subheader("Bank Failure Analysis")

    bank_failure_data = (
        filtered.groupby("payer_bank")
        .agg(
            total_transactions=("transaction_id", "count"),
            failed_transactions=(
                "status",
                lambda x: (x == "FAILED").sum()
            )
        )
        .reset_index()
    )

    bank_failure_data["failure_rate_percentage"] = (
        bank_failure_data["failed_transactions"]
        / bank_failure_data["total_transactions"] * 100
    ).round(2)

    bank_failure_data = bank_failure_data.sort_values(
        "failure_rate_percentage",
        ascending=False
    )

    fig = px.bar(
        bank_failure_data,
        x="payer_bank",
        y="failure_rate_percentage",
        title="Bank-wise Failure Rate",
        text="failure_rate_percentage",
        labels={
            "payer_bank": "Payer Bank",
            "failure_rate_percentage": "Failure Rate (%)"
        }
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        bank_failure_data,
        use_container_width=True,
        hide_index=True
    )

    # ----------------------------------------------
    # 14.3 PAYMENT APP FAILURE ANALYSIS
    # ----------------------------------------------

    st.subheader("Payment App Failure Analysis")

    app_failure_data = (
        filtered.groupby("payment_app")
        .agg(
            total_transactions=("transaction_id", "count"),
            failed_transactions=(
                "status",
                lambda x: (x == "FAILED").sum()
            )
        )
        .reset_index()
    )

    app_failure_data["failure_rate_percentage"] = (
        app_failure_data["failed_transactions"]
        / app_failure_data["total_transactions"] * 100
    ).round(2)

    app_failure_data = app_failure_data.sort_values(
        "failure_rate_percentage",
        ascending=False
    )

    fig = px.bar(
        app_failure_data,
        x="payment_app",
        y="failure_rate_percentage",
        title="Payment App-wise Failure Rate",
        text="failure_rate_percentage",
        labels={
            "payment_app": "Payment App",
            "failure_rate_percentage": "Failure Rate (%)"
        }
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        app_failure_data,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No failed transactions found for the selected filters.")


# ==========================================================
# 15. UPI TRANSACTION TIME ANALYSIS
# ==========================================================

st.divider()

st.header("UPI Transaction Time Analysis")

if not filtered.empty:

    # ----------------------------------------------
    # 15.1 HOURLY TRANSACTION ANALYSIS
    # ----------------------------------------------

    st.subheader("Hourly Transaction Analysis")

    hourly_data = (
        filtered.groupby("transaction_hour")
        .agg(
            total_transactions=("transaction_id", "count"),
            successful_transactions=(
                "status",
                lambda x: (x == "SUCCESS").sum()
            ),
            failed_transactions=(
                "status",
                lambda x: (x == "FAILED").sum()
            ),
            pending_transactions=(
                "status",
                lambda x: (x == "PENDING").sum()
            ),
            total_transaction_value=("amount", "sum")
        )
        .reset_index()
        .sort_values("transaction_hour")
    )

    hourly_data["failure_rate_percentage"] = (
        hourly_data["failed_transactions"]
        / hourly_data["total_transactions"] * 100
    ).round(2)

    fig = px.bar(
        hourly_data,
        x="transaction_hour",
        y="total_transactions",
        title="Hourly Transaction Volume",
        labels={
            "transaction_hour": "Hour of Day",
            "total_transactions": "Total Transactions"
        }
    )

    fig.update_xaxes(
        tickmode="linear",
        dtick=1
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig = px.line(
        hourly_data,
        x="transaction_hour",
        y="failure_rate_percentage",
        markers=True,
        title="Hourly Transaction Failure Rate",
        labels={
            "transaction_hour": "Hour of Day",
            "failure_rate_percentage": "Failure Rate (%)"
        }
    )

    fig.update_xaxes(
        range=[-0.5, 23.5],
        tickmode="linear",
        dtick=1
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        hourly_data,
        use_container_width=True,
        hide_index=True
    )

    # ----------------------------------------------
    # 15.2 WEEKDAY TRANSACTION ANALYSIS
    # ----------------------------------------------

    st.subheader("Day-of-Week Transaction Analysis")

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    weekday_data = (
        filtered.groupby("transaction_day_of_week")
        .agg(
            total_transactions=("transaction_id", "count"),
            successful_transactions=(
                "status",
                lambda x: (x == "SUCCESS").sum()
            ),
            failed_transactions=(
                "status",
                lambda x: (x == "FAILED").sum()
            ),
            pending_transactions=(
                "status",
                lambda x: (x == "PENDING").sum()
            ),
            total_transaction_value=("amount", "sum")
        )
        .reset_index()
    )

    weekday_data["failure_rate_percentage"] = (
        weekday_data["failed_transactions"]
        / weekday_data["total_transactions"] * 100
    ).round(2)

    weekday_data["transaction_day_of_week"] = pd.Categorical(
        weekday_data["transaction_day_of_week"],
        categories=weekday_order,
        ordered=True
    )

    weekday_data = weekday_data.sort_values(
        "transaction_day_of_week"
    )

    fig = px.bar(
        weekday_data,
        x="transaction_day_of_week",
        y="total_transactions",
        title="Weekday Transaction Volume",
        text="total_transactions",
        labels={
            "transaction_day_of_week": "Day of Week",
            "total_transactions": "Total Transactions"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig = px.bar(
        weekday_data,
        x="transaction_day_of_week",
        y="failure_rate_percentage",
        title="Weekday Transaction Failure Rate",
        text="failure_rate_percentage",
        labels={
            "transaction_day_of_week": "Day of Week",
            "failure_rate_percentage": "Failure Rate (%)"
        }
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        weekday_data,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No transactions available for time analysis.")


# ==========================================================
# 16. TRANSACTION DATA EXPLORER
# ==========================================================

st.header("Transaction Data Explorer")

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True
)

csv_data = filtered.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Filtered Transactions",
    data=csv_data,
    file_name="upi_filtered_transactions.csv",
    mime="text/csv"
)


# ==========================================================
# 17. FOOTER
# ==========================================================

st.divider()

st.sidebar.divider()

st.sidebar.caption(
    "FINTECH 360° | UPI Payments Module"
)

st.caption(
    "FINTECH 360° | UPI Analytics | "
    "Built with Python, SQLite, Streamlit and Plotly"
)
