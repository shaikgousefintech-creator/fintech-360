
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
    page_title="FINTECH 360 | Digital Gold",
    page_icon="🪙",
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
                c.customer_name,
                c.customer_segment,
                c.city,
                c.age,
                c.gender
            FROM dg_transactions t
            LEFT JOIN dg_customers c
                ON t.customer_id = c.customer_id
            """,
            conn
        )

        price_history = pd.read_sql_query(
            """
            SELECT *
            FROM dg_price_history
            ORDER BY price_date
            """,
            conn
        )

    transactions["transaction_date"] = pd.to_datetime(
        transactions["transaction_date"],
        errors="coerce"
    )

    price_history["price_date"] = pd.to_datetime(
        price_history["price_date"],
        errors="coerce"
    )

    numeric_columns = [
        "gold_quantity_grams",
        "gold_price_per_gram",
        "amount",
        "age"
    ]

    for column in numeric_columns:
        transactions[column] = pd.to_numeric(
            transactions[column],
            errors="coerce"
        )

    price_columns = [
        "gold_price_per_gram",
        "buy_price_per_gram",
        "sell_price_per_gram"
    ]

    for column in price_columns:
        price_history[column] = pd.to_numeric(
            price_history[column],
            errors="coerce"
        )

    return transactions, price_history


try:
    transactions, price_history = load_data()

except Exception as error:
    st.error(f"Unable to load dashboard data: {error}")
    st.stop()


# ==================================================
# 3. FINTECH 360° SHARED THEME
# ==================================================

st.markdown(
    """
    <style>

    :root {
        --fintech-navy: #10243a;
        --fintech-blue: #183e5c;
        --fintech-teal: #176b75;
        --fintech-accent: #9edce0;
        --fintech-text: #e3edf5;
        --fintech-muted: #c2d4e1;
    }

    /* MAIN APPLICATION */

    .stApp {
        background-color: #1e1e1e;
        color: #e3edf5;
    }

    [data-testid="stHeader"] {
        background-color: #1e1e1e;
    }

    /* MAIN CONTENT LAYOUT */

    [data-testid="stAppViewContainer"] .main .block-container {
        max-width: 100%;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* SIDEBAR */

    [data-testid="stSidebar"] {
        background-color: #1e1e1e;
        border-right: 1px solid #344354;
    }

    /* GRADIENT HERO HEADER */

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

    /* DATE FILTERS */

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

    /* MULTISELECT FILTERS */

    [data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background-color: #10243a !important;
        border: 1px solid #176b75 !important;
        border-radius: 8px !important;
    }

    [data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background-color: #176b75 !important;
        border: 1px solid #38bdf8 !important;
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="tag"] * {
        color: #ffffff !important;
        fill: #ffffff !important;
    }

    /* SIDEBAR TEXT */

    [data-testid="stSidebar"] label {
        color: #d9e8f1 !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #e3edf5 !important;
    }

    /* KPI CARDS */

    [data-testid="stMetric"] {
        background: linear-gradient(
            135deg,
            #172b40,
            #1b3d50
        );
        border: 1px solid #31566b;
        padding: 18px;
        border-radius: 12px;
        min-height: 112px;
    }

    [data-testid="stMetricLabel"] {
        color: #c2d4e1 !important;
    }

    [data-testid="stMetricValue"] {
        color: #e3edf5 !important;
        font-size: clamp(1.05rem, 1.65vw, 1.8rem);
        white-space: nowrap;
    }

    /* HEADINGS AND CAPTIONS */

    h1, h2, h3, h4 {
        color: #e3edf5 !important;
    }

    [data-testid="stCaptionContainer"] {
        color: #aabac9 !important;
    }

    /* DATA TABLES */

    [data-testid="stDataFrame"] {
        border: 1px solid #344b60;
        border-radius: 10px;
    }

    /* DOWNLOAD BUTTON */

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

    /* DIVIDERS */

    hr {
        border-color: #344354 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# 4. DASHBOARD HEADER
# ==================================================

st.markdown(
    """
    <div class="fintech-hero">
        <div class="fintech-hero-kicker">
            FINANCIAL DATA PLATFORM · BUSINESS ANALYTICS
        </div>
        <h1>FINTECH 360°</h1>
        <div class="fintech-hero-subtitle">
            Digital Gold Analytics Dashboard
        </div>
        <div class="fintech-hero-description">
            End-to-End Financial Data Engineering, Analytics
            &amp; Business Intelligence Platform
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# ==================================================
# 5. SIDEBAR FILTERS
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
    key="dg_start_date"
)

end_date = st.sidebar.date_input(
    "End Date",
    value=max_date,
    min_value=min_date,
    max_value=max_date,
    key="dg_end_date"
)

if start_date > end_date:
    st.sidebar.error(
        "Start Date cannot be after End Date."
    )
    st.stop()

st.sidebar.divider()

segments = sorted(
    transactions["customer_segment"].dropna().unique()
)

selected_segments = st.sidebar.multiselect(
    "Customer Segment",
    segments,
    default=segments
)

cities = sorted(
    transactions["city"].dropna().unique()
)

selected_cities = st.sidebar.multiselect(
    "Customer City",
    cities,
    default=cities
)

modes = sorted(
    transactions["investment_mode"].dropna().unique()
)

selected_modes = st.sidebar.multiselect(
    "Investment Mode",
    modes,
    default=modes
)

transaction_types = sorted(
    transactions["transaction_type"].dropna().unique()
)

selected_types = st.sidebar.multiselect(
    "Transaction Type",
    transaction_types,
    default=transaction_types
)

st.sidebar.divider()

st.sidebar.caption(
    "FINTECH 360° | Digital Gold Module"
)


# ==================================================
# 6. APPLY FILTERS
# ==================================================

start_timestamp = pd.Timestamp(start_date)

end_timestamp = (
    pd.Timestamp(end_date)
    + pd.Timedelta(days=1)
)

filtered = transactions[
    (transactions["transaction_date"] >= start_timestamp)
    & (transactions["transaction_date"] < end_timestamp)
    & (transactions["customer_segment"].isin(selected_segments))
    & (transactions["city"].isin(selected_cities))
    & (transactions["investment_mode"].isin(selected_modes))
    & (transactions["transaction_type"].isin(selected_types))
].copy()

st.write(
    f"Showing transactions from "
    f"{start_date.strftime('%d %b %Y')} to "
    f"{end_date.strftime('%d %b %Y')}"
)

st.write(f"Filtered Records: {len(filtered):,}")


# ==================================================
# 7. KEY PERFORMANCE INDICATORS
# ==================================================

st.header("Key Performance Indicators")

total_transactions = len(filtered)

total_customers = filtered[
    "customer_id"
].nunique()

successful = filtered[
    filtered["transaction_status"] == "SUCCESS"
]

failed = filtered[
    filtered["transaction_status"] == "FAILED"
]

pending = filtered[
    filtered["transaction_status"] == "PENDING"
]

buy = successful[
    successful["transaction_type"] == "BUY"
]

sell = successful[
    successful["transaction_type"] == "SELL"
]

total_buy_amount = buy["amount"].sum()
total_sell_amount = sell["amount"].sum()

net_transaction_amount = (
    total_buy_amount - total_sell_amount
)

total_gold_bought = buy[
    "gold_quantity_grams"
].sum()

total_gold_sold = sell[
    "gold_quantity_grams"
].sum()

net_gold_accumulated = (
    total_gold_bought - total_gold_sold
)

success_rate = (
    len(successful) / total_transactions * 100
    if total_transactions > 0 else 0
)


def format_inr_crore(amount):
    """Format INR values in crore for compact KPI display."""
    return f"₹{amount / 10_000_000:,.2f} Cr"


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Customers",
    f"{total_customers:,}"
)

col2.metric(
    "Total Transactions",
    f"{total_transactions:,}"
)

col3.metric(
    "Successful BUY Amount",
    format_inr_crore(total_buy_amount)
)

col4.metric(
    "Successful SELL Amount",
    format_inr_crore(total_sell_amount)
)

col5, col6, col7, col8 = st.columns(4)

col5.metric(
    "Net Transaction Amount",
    format_inr_crore(net_transaction_amount)
)

col6.metric(
    "Net Gold Accumulated",
    f"{net_gold_accumulated:,.2f} g"
)

col7.metric(
    "Successful Transactions",
    f"{len(successful):,}"
)

col8.metric(
    "Success Rate",
    f"{success_rate:.2f}%"
)

st.divider()


# ==================================================
# 8. CUSTOMER BEHAVIOUR ANALYSIS
# ==================================================

st.header("Customer Behaviour Analysis")

left, right = st.columns(2)

with left:

    st.subheader("Customer Segment Distribution")

    segment_data = (
        filtered.groupby("customer_segment")
        .agg(
            total_customers=("customer_id", "nunique")
        )
        .reset_index()
    )

    if not segment_data.empty:

        fig = px.pie(
            segment_data,
            names="customer_segment",
            values="total_customers",
            hole=0.45,
            title="Customers by Segment"
        )

        fig.update_layout(
            height=480,
            margin=dict(l=20, r=20, t=65, b=20)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("No customer data available.")

with right:

    st.subheader("Top 10 Customers")

    customer_data = filtered.copy()

    customer_data["buy_gold_grams"] = (
        customer_data["gold_quantity_grams"].where(
            (customer_data["transaction_status"] == "SUCCESS")
            & (customer_data["transaction_type"] == "BUY"),
            0
        )
    )

    customer_data["sell_gold_grams"] = (
        customer_data["gold_quantity_grams"].where(
            (customer_data["transaction_status"] == "SUCCESS")
            & (customer_data["transaction_type"] == "SELL"),
            0
        )
    )

    customer_data = (
        customer_data.groupby(
            ["customer_id", "customer_name", "customer_segment"],
            as_index=False
        )
        .agg(
            total_gold_bought=("buy_gold_grams", "sum"),
            total_gold_sold=("sell_gold_grams", "sum")
        )
    )

    customer_data["net_gold_accumulated"] = (
        customer_data["total_gold_bought"]
        - customer_data["total_gold_sold"]
    )

    top_customers = customer_data.nlargest(
        10,
        "net_gold_accumulated"
    )

    if not top_customers.empty:

        fig = px.bar(
            top_customers.sort_values(
                "net_gold_accumulated",
                ascending=True
            ),
            x="net_gold_accumulated",
            y="customer_name",
            color="customer_segment",
            orientation="h",
            title="Top Customers by Net Gold Accumulation",
            labels={
                "net_gold_accumulated": "Net Gold (grams)",
                "customer_name": "Customer"
            }
        )

        fig.update_layout(
            height=480,
            margin=dict(l=20, r=20, t=65, b=35),
            yaxis_title="Customer"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("No customer data available.")


# ==================================================
# 9. BUY AND SELL PERFORMANCE
# ==================================================

st.divider()

st.header("BUY and SELL Performance")

type_data = filtered.copy()

type_data["buy_amount"] = (
    type_data["amount"].where(
        (type_data["transaction_status"] == "SUCCESS")
        & (type_data["transaction_type"] == "BUY"),
        0
    )
)

type_data["sell_amount"] = (
    type_data["amount"].where(
        (type_data["transaction_status"] == "SUCCESS")
        & (type_data["transaction_type"] == "SELL"),
        0
    )
)

type_data["buy_gold_grams"] = (
    type_data["gold_quantity_grams"].where(
        (type_data["transaction_status"] == "SUCCESS")
        & (type_data["transaction_type"] == "BUY"),
        0
    )
)

type_data["sell_gold_grams"] = (
    type_data["gold_quantity_grams"].where(
        (type_data["transaction_status"] == "SUCCESS")
        & (type_data["transaction_type"] == "SELL"),
        0
    )
)

type_data["is_successful"] = (
    type_data["transaction_status"] == "SUCCESS"
).astype(int)

type_data = (
    type_data.groupby(
        "transaction_type",
        as_index=False
    )
    .agg(
        total_transactions=("transaction_id", "count"),
        successful_transactions=("is_successful", "sum"),
        total_buy_amount=("buy_amount", "sum"),
        total_sell_amount=("sell_amount", "sum"),
        total_buy_gold=("buy_gold_grams", "sum"),
        total_sell_gold=("sell_gold_grams", "sum")
    )
)

if not type_data.empty:

    left, right = st.columns(2)

    with left:

        st.subheader("Successful Transaction Amount")

        amount_data = type_data.melt(
            id_vars="transaction_type",
            value_vars=[
                "total_buy_amount",
                "total_sell_amount"
            ],
            var_name="amount_type",
            value_name="amount"
        )

        amount_data["amount_type"] = (
            amount_data["amount_type"].replace({
                "total_buy_amount": "BUY",
                "total_sell_amount": "SELL"
            })
        )

        fig = px.bar(
            amount_data,
            x="transaction_type",
            y="amount",
            color="amount_type",
            barmode="group",
            title="BUY and SELL Amount",
            labels={
                "transaction_type": "Transaction Type",
                "amount": "Amount (₹)",
                "amount_type": "Amount Category"
            }
        )

        fig.update_layout(
            height=480,
            margin=dict(l=20, r=20, t=65, b=35),
            yaxis_title="Amount (₹)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        st.subheader("Successful Gold Quantity")

        quantity_data = type_data.melt(
            id_vars="transaction_type",
            value_vars=[
                "total_buy_gold",
                "total_sell_gold"
            ],
            var_name="quantity_type",
            value_name="quantity"
        )

        quantity_data["quantity_type"] = (
            quantity_data["quantity_type"].replace({
                "total_buy_gold": "BUY",
                "total_sell_gold": "SELL"
            })
        )

        fig = px.bar(
            quantity_data,
            x="transaction_type",
            y="quantity",
            color="quantity_type",
            barmode="group",
            title="BUY and SELL Gold Quantity",
            labels={
                "transaction_type": "Transaction Type",
                "quantity": "Gold Quantity (grams)",
                "quantity_type": "Quantity Category"
            }
        )

        fig.update_layout(
            height=480,
            margin=dict(l=20, r=20, t=65, b=35),
            yaxis_title="Gold Quantity (grams)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader("Transaction Type Performance Table")

    st.dataframe(
        type_data,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No BUY or SELL data available.")


# ==================================================
# 10. INVESTMENT MODE ANALYSIS
# ==================================================

st.divider()

st.header("Investment Mode Analysis")

mode_data = filtered.copy()

mode_data["successful_amount"] = (
    mode_data["amount"].where(
        mode_data["transaction_status"] == "SUCCESS",
        0
    )
)

mode_data["successful_gold_quantity"] = (
    mode_data["gold_quantity_grams"].where(
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

mode_data["is_pending"] = (
    mode_data["transaction_status"] == "PENDING"
).astype(int)

mode_data = (
    mode_data.groupby(
        "investment_mode",
        as_index=False
    )
    .agg(
        total_transactions=("transaction_id", "count"),
        successful_transactions=("is_successful", "sum"),
        failed_transactions=("is_failed", "sum"),
        pending_transactions=("is_pending", "sum"),
        successful_transaction_amount=("successful_amount", "sum"),
        successful_gold_quantity=("successful_gold_quantity", "sum")
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
            x="investment_mode",
            y="total_transactions",
            color="investment_mode",
            title="Transactions by Investment Mode",
            labels={
                "investment_mode": "Investment Mode",
                "total_transactions": "Transactions"
            }
        )

        fig.update_layout(
            height=480,
            margin=dict(l=20, r=20, t=65, b=35),
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        fig = px.bar(
            mode_data,
            x="investment_mode",
            y="successful_transaction_amount",
            color="investment_mode",
            title="Successful Transaction Amount by Mode",
            labels={
                "investment_mode": "Investment Mode",
                "successful_transaction_amount": "Amount (₹)"
            }
        )

        fig.update_layout(
            height=480,
            margin=dict(l=20, r=20, t=65, b=35),
            showlegend=False
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
# 11. MONTHLY GOLD FLOW TRENDS
# ==================================================

st.divider()

st.header("Monthly Gold Flow Trends")

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

    monthly_data["buy_amount"] = (
        monthly_data["amount"].where(
            monthly_data["transaction_type"] == "BUY",
            0
        )
    )

    monthly_data["sell_amount"] = (
        monthly_data["amount"].where(
            monthly_data["transaction_type"] == "SELL",
            0
        )
    )

    monthly_data = (
        monthly_data.groupby(
            "transaction_month",
            as_index=False
        )
        .agg(
            buy_amount=("buy_amount", "sum"),
            sell_amount=("sell_amount", "sum")
        )
    )

    if not monthly_data.empty:

        month_end = (
            pd.Timestamp(end_date)
            + pd.offsets.MonthEnd(0)
        )

        is_partial_month = (
            end_date == max_date
            and max_date < month_end.date()
        )

        monthly_title = "Monthly BUY and SELL Amount"

        if is_partial_month:
            monthly_title += " (Latest Month - Partial Data)"

        monthly_chart = monthly_data.melt(
            id_vars="transaction_month",
            value_vars=[
                "buy_amount",
                "sell_amount"
            ],
            var_name="transaction_type",
            value_name="transaction_amount"
        )

        monthly_chart["transaction_type"] = (
            monthly_chart["transaction_type"].replace({
                "buy_amount": "BUY",
                "sell_amount": "SELL"
            })
        )

        fig = px.line(
            monthly_chart,
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

        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=65, b=35)
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
# 12. GOLD PRICE TRENDS
# ==================================================

st.divider()

st.header("Gold Price Trends")

if not price_history.empty:

    price_filtered = price_history[
        (price_history["price_date"] >= start_timestamp)
        & (price_history["price_date"] < end_timestamp)
    ].copy()

    if not price_filtered.empty:

        fig = px.line(
            price_filtered,
            x="price_date",
            y=[
                "gold_price_per_gram",
                "buy_price_per_gram",
                "sell_price_per_gram"
            ],
            markers=True,
            title="Gold Price Movement",
            labels={
                "price_date": "Date",
                "value": "Price per Gram (₹)",
                "variable": "Price Type"
            }
        )

        fig.update_layout(
            height=500,
            margin=dict(l=20, r=20, t=65, b=35),
            legend_title_text="Price Type"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            price_filtered.sort_values(
                "price_date",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "No gold price data available for the selected dates."
        )

else:
    st.info("No gold price history available.")


# ==================================================
# 13. TRANSACTION DATA EXPLORER
# ==================================================

st.divider()

st.header("Transaction Data Explorer")

if not filtered.empty:

    display_columns = [
        "transaction_id",
        "customer_id",
        "customer_name",
        "customer_segment",
        "city",
        "transaction_date",
        "transaction_type",
        "investment_mode",
        "gold_quantity_grams",
        "gold_price_per_gram",
        "amount",
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
        file_name="digital_gold_filtered_transactions.csv",
        mime="text/csv"
    )

else:
    st.info(
        "No transactions match the selected filters."
    )


# ==================================================
# 14. FOOTER
# ==================================================

st.divider()

st.caption(
    "FINTECH 360° | Digital Gold Analytics | "
    "Built with Python, SQLite, Pandas, Streamlit and Plotly"
)

st.caption(
    "Note: This dashboard analyses synthetic transaction activity. "
    "Net gold accumulated is successful BUY quantity minus "
    "successful SELL quantity. It is not investment return or "
    "market valuation."
)
