
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

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


# --------------------------------------------------
# 2. DATABASE CONNECTION
# --------------------------------------------------

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


# --------------------------------------------------
# 3. PREPARE TRANSACTION DATA
# --------------------------------------------------

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

# Normalize dates for date-based filtering
transactions["transaction_day"] = (
    transactions["transaction_date"].dt.normalize()
)

start_date = transactions["transaction_day"].min().date()
end_date = transactions["transaction_day"].max().date()


# --------------------------------------------------
# 4. DASHBOARD HEADER
# --------------------------------------------------

st.title("FINTECH 360°")

st.subheader("UPI Payments Analytics Dashboard")

st.caption(
    "End-to-End Financial Data Engineering, "
    "Analytics & Business Intelligence Platform"
)

st.divider()


# --------------------------------------------------
# 5. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

st.sidebar.subheader("Transaction Date Range")

# Separate Start Date and End Date pickers
# This avoids incomplete tuple selection issues.

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

# Validate selected date range

if selected_start_date > selected_end_date:

    st.sidebar.error(
        "Start Date cannot be greater than End Date."
    )

    st.stop()

st.sidebar.divider()

# Bank filter

available_banks = sorted(
    transactions["payer_bank"].dropna().unique().tolist()
)

selected_banks = st.sidebar.multiselect(
    "Select Banks",
    options=available_banks,
    default=available_banks,
    key="upi_bank_filter"
)

# Payment App filter

available_apps = sorted(
    transactions["payment_app"].dropna().unique().tolist()
)

selected_apps = st.sidebar.multiselect(
    "Select Payment Apps",
    options=available_apps,
    default=available_apps,
    key="upi_app_filter"
)


# --------------------------------------------------
# 6. FILTER TRANSACTIONS
# --------------------------------------------------

# Convert selected dates into timestamps.
# End date is exclusive, so the entire end date is included.

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

# Display selected filter information

st.caption(
    f"Showing transactions from "
    f"{selected_start_date.strftime('%d %b %Y')} "
    f"to {selected_end_date.strftime('%d %b %Y')}"
)

st.caption(
    f"Filtered Records: {len(filtered):,}"
)


# --------------------------------------------------
# 7. CALCULATE KPIs
# --------------------------------------------------

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


# --------------------------------------------------
# 8. KPI CARDS
# --------------------------------------------------

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


# --------------------------------------------------
# 9. DAILY TRANSACTION TRENDS
# --------------------------------------------------

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

    # Daily Transaction Volume

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

    # Daily Transaction Value

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


# --------------------------------------------------
# 10. TRANSACTION STATUS ANALYSIS
# --------------------------------------------------

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


# --------------------------------------------------
# 11. BANK PERFORMANCE
# --------------------------------------------------

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

    # Bank-wise Transaction Volume

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

    # Bank-wise Success Rate

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


# --------------------------------------------------
# 12. PAYMENT APP PERFORMANCE
# --------------------------------------------------

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

    # Payment App Transaction Comparison

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

    # Payment App Success Rate

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


# --------------------------------------------------
# 13. TRANSACTION DATA EXPLORER
# --------------------------------------------------

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


# --------------------------------------------------
# 14. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "FINTECH 360° | UPI Analytics | "
    "Built with Python, SQLite, Streamlit and Plotly"
)
