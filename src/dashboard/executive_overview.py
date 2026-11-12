
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# 1. CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "warehouse" / "database" / "fintech360.db"

st.set_page_config(
    page_title="FINTECH 360° | Overview",
    page_icon="📊",
    layout="wide",
)


# =========================================================
# 2. DATA ACCESS
# =========================================================

@st.cache_data(ttl=60)
def read_sql(query):
    """Read data from the central SQLite warehouse."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query(query, connection)


@st.cache_data(ttl=60)
def load_portfolio_data():

    # ---------------- UPI ----------------

    upi_summary = read_sql("""
        SELECT
            COUNT(*) AS total_transactions,
            SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END)
                AS successful_transactions,
            SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END)
                AS failed_transactions,
            SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END)
                AS pending_transactions,
            SUM(CASE WHEN status = 'SUCCESS' THEN amount ELSE 0 END)
                AS successful_amount
        FROM upi_transactions
    """)

    upi_status = read_sql("""
        SELECT status, COUNT(*) AS transaction_count,
               SUM(amount) AS transaction_amount
        FROM upi_transactions
        GROUP BY status
        ORDER BY status
    """)

    upi_monthly = read_sql("""
        SELECT
            substr(transaction_date, 1, 7) AS activity_month,
            COUNT(*) AS total_transactions,
            SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END)
                AS successful_transactions,
            SUM(CASE WHEN status = 'SUCCESS' THEN amount ELSE 0 END)
                AS successful_amount
        FROM upi_transactions
        GROUP BY substr(transaction_date, 1, 7)
        ORDER BY activity_month
    """)

    # ---------------- MUTUAL FUNDS ----------------

    mf_summary = read_sql("""
        SELECT
            (SELECT COUNT(*) FROM mf_investors) AS total_investors,
            (SELECT COUNT(*) FROM mf_schemes) AS total_schemes,
            (SELECT COUNT(*) FROM mf_nav_history) AS total_nav_records,
            COUNT(*) AS total_transactions,
            SUM(CASE
                WHEN transaction_status = 'SUCCESS'
                THEN 1 ELSE 0
            END) AS successful_transactions,
            SUM(CASE
                WHEN transaction_status = 'SUCCESS'
                     AND transaction_type = 'PURCHASE'
                THEN amount ELSE 0
            END) AS successful_purchases,
            SUM(CASE
                WHEN transaction_status = 'SUCCESS'
                     AND transaction_type = 'REDEMPTION'
                THEN amount ELSE 0
            END) AS successful_redemptions
        FROM mf_transactions
    """)

    mf_status = read_sql("""
        SELECT
            transaction_status,
            transaction_type,
            COUNT(*) AS transaction_count,
            SUM(amount) AS transaction_amount
        FROM mf_transactions
        GROUP BY transaction_status, transaction_type
        ORDER BY transaction_status, transaction_type
    """)

    mf_monthly = read_sql("""
        SELECT
            substr(transaction_date, 1, 7) AS activity_month,
            COUNT(*) AS total_transactions,
            SUM(CASE
                WHEN transaction_status = 'SUCCESS'
                     AND transaction_type = 'PURCHASE'
                THEN amount ELSE 0
            END) AS purchase_amount,
            SUM(CASE
                WHEN transaction_status = 'SUCCESS'
                     AND transaction_type = 'REDEMPTION'
                THEN amount ELSE 0
            END) AS redemption_amount
        FROM mf_transactions
        GROUP BY substr(transaction_date, 1, 7)
        ORDER BY activity_month
    """)

    # ---------------- DIGITAL GOLD ----------------

    dg_summary = read_sql("""
        SELECT
            (SELECT COUNT(*) FROM dg_customers) AS total_customers,
            (SELECT COUNT(*) FROM dg_wallet_ledger) AS total_ledger_entries,
            (SELECT COUNT(*) FROM dg_price_history) AS total_price_records,
            COUNT(*) AS total_transactions,
            SUM(CASE
                WHEN transaction_status = 'SUCCESS'
                THEN 1 ELSE 0
            END) AS successful_transactions,
            SUM(CASE
                WHEN transaction_status = 'SUCCESS'
                     AND transaction_type = 'BUY'
                THEN amount ELSE 0
            END) AS successful_buy_amount,
            SUM(CASE
                WHEN transaction_status = 'SUCCESS'
                     AND transaction_type = 'SELL'
                THEN amount ELSE 0
            END) AS successful_sell_amount,
            SUM(CASE
                WHEN transaction_status = 'SUCCESS'
                     AND transaction_type = 'BUY'
                THEN gold_quantity_grams ELSE 0
            END) AS successful_buy_grams,
            SUM(CASE
                WHEN transaction_status = 'SUCCESS'
                     AND transaction_type = 'SELL'
                THEN gold_quantity_grams ELSE 0
            END) AS successful_sell_grams
        FROM dg_transactions
    """)

    dg_status = read_sql("""
        SELECT
            transaction_status,
            transaction_type,
            COUNT(*) AS transaction_count,
            SUM(amount) AS transaction_amount,
            SUM(gold_quantity_grams) AS gold_quantity
        FROM dg_transactions
        GROUP BY transaction_status, transaction_type
        ORDER BY transaction_status, transaction_type
    """)

    dg_monthly = read_sql("""
        SELECT
            substr(transaction_date, 1, 7) AS activity_month,
            COUNT(*) AS total_transactions,
            SUM(CASE
                WHEN transaction_status = 'SUCCESS'
                     AND transaction_type = 'BUY'
                THEN gold_quantity_grams ELSE 0
            END) AS buy_grams,
            SUM(CASE
                WHEN transaction_status = 'SUCCESS'
                     AND transaction_type = 'SELL'
                THEN gold_quantity_grams ELSE 0
            END) AS sell_grams,
            SUM(CASE
                WHEN transaction_status = 'SUCCESS'
                THEN amount ELSE 0
            END) AS successful_amount
        FROM dg_transactions
        GROUP BY substr(transaction_date, 1, 7)
        ORDER BY activity_month
    """)

    # ---------------- CASH LOANS ----------------

    cl_summary = read_sql("""
        SELECT
            (SELECT COUNT(*) FROM cl_customers) AS total_customers,
            COUNT(*) AS total_applications,
            SUM(CASE
                WHEN application_status = 'APPROVED'
                THEN 1 ELSE 0
            END) AS approved_applications,
            SUM(CASE
                WHEN application_status = 'REJECTED'
                THEN 1 ELSE 0
            END) AS rejected_applications,
            SUM(requested_amount) AS total_requested_amount,
            SUM(CASE
                WHEN application_status = 'APPROVED'
                THEN approved_amount ELSE 0
            END) AS total_approved_amount
        FROM cl_loan_applications
    """)

    cl_disbursement = read_sql("""
        SELECT
            COUNT(*) AS total_disbursements,
            SUM(CASE
                WHEN disbursement_status = 'SUCCESS'
                THEN 1 ELSE 0
            END) AS successful_disbursements,
            SUM(CASE
                WHEN disbursement_status = 'FAILED'
                THEN 1 ELSE 0
            END) AS failed_disbursements,
            SUM(CASE
                WHEN disbursement_status = 'PENDING'
                THEN 1 ELSE 0
            END) AS pending_disbursements,
            SUM(CASE
                WHEN disbursement_status = 'SUCCESS'
                THEN disbursed_amount ELSE 0
            END) AS successful_disbursed_amount
        FROM cl_loan_disbursements
    """)

    cl_repayment = read_sql("""
        SELECT
            COUNT(*) AS total_installments,
            SUM(total_due_amount) AS total_due,
            SUM(amount_paid) AS total_collected,
            SUM(CASE
                WHEN repayment_status = 'OVERDUE'
                THEN total_due_amount - amount_paid
                ELSE 0
            END) AS overdue_outstanding,
            SUM(CASE
                WHEN repayment_status = 'PAID'
                THEN 1 ELSE 0
            END) AS paid_installments,
            SUM(CASE
                WHEN repayment_status = 'OVERDUE'
                THEN 1 ELSE 0
            END) AS overdue_installments
        FROM cl_loan_repayments
    """)

    cl_monthly = read_sql("""
        SELECT
            substr(application_date, 1, 7) AS activity_month,
            COUNT(*) AS total_applications,
            SUM(CASE
                WHEN application_status = 'APPROVED'
                THEN 1 ELSE 0
            END) AS approved_applications,
            SUM(CASE
                WHEN application_status = 'REJECTED'
                THEN 1 ELSE 0
            END) AS rejected_applications
        FROM cl_loan_applications
        GROUP BY substr(application_date, 1, 7)
        ORDER BY activity_month
    """)

    cl_application_status = read_sql("""
        SELECT application_status, COUNT(*) AS application_count
        FROM cl_loan_applications
        GROUP BY application_status
        ORDER BY application_status
    """)

    return {
        "upi_summary": upi_summary,
        "upi_status": upi_status,
        "upi_monthly": upi_monthly,
        "mf_summary": mf_summary,
        "mf_status": mf_status,
        "mf_monthly": mf_monthly,
        "dg_summary": dg_summary,
        "dg_status": dg_status,
        "dg_monthly": dg_monthly,
        "cl_summary": cl_summary,
        "cl_disbursement": cl_disbursement,
        "cl_repayment": cl_repayment,
        "cl_monthly": cl_monthly,
        "cl_application_status": cl_application_status,
    }


try:
    data = load_portfolio_data()
except Exception as error:
    st.error(f"Unable to load portfolio data: {error}")
    st.stop()


# =========================================================
# 3. SAFE VALUE HELPERS
# =========================================================

def number(frame, column):
    value = frame.iloc[0][column]
    return 0 if pd.isna(value) else value


def percentage(numerator, denominator):
    return numerator / denominator * 100 if denominator else 0


def inr_lakh(value):
    return f"₹{value / 100000:,.2f} L"


def inr_crore(value):
    return f"₹{value / 10000000:,.2f} Cr"


def fmt_number(value):
    return f"{value:,.0f}"


def chart_theme(fig, height=380):
    fig.update_layout(
        height=height,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#d9e8f1"),
        margin=dict(l=20, r=20, t=65, b=25),
        legend_title_text="",
    )
    return fig


# =========================================================
# 4. THEME
# =========================================================

st.markdown(
    """
    <style>
    .stApp, [data-testid="stHeader"] {
        background-color: #1e1e1e;
        color: #e3edf5;
    }

    [data-testid="stAppViewContainer"] .main .block-container {
        max-width: 100%;
        padding: 1.5rem 2rem 2rem 2rem;
    }

    [data-testid="stSidebar"] {
        background-color: #1e1e1e;
        border-right: 1px solid #344354;
    }

    .hero {
        padding: 2.2rem 2rem;
        border-radius: 18px;
        background: linear-gradient(
            120deg, #10243a 0%, #183e5c 55%, #176b75 100%
        );
        border: 1px solid rgba(158, 220, 224, 0.16);
        margin-bottom: 1.5rem;
    }

    .hero-kicker {
        color: #9edce0;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }

    .hero h1 {
        color: #ffffff !important;
        font-size: 2.65rem;
        margin: 0;
        line-height: 1.2;
    }

    .hero-subtitle {
        color: #d9e8f1;
        font-size: 1.12rem;
        margin-top: 0.8rem;
    }

    .hero-description {
        color: #c2d4e1;
        font-size: 0.96rem;
        max-width: 900px;
        line-height: 1.65;
    }

    .domain-card {
        border: 1px solid #344b60;
        border-radius: 13px;
        padding: 1rem;
        min-height: 185px;
        background: rgba(16, 36, 58, 0.35);
    }

    .domain-card h3 {
        color: #e3edf5 !important;
        margin: 0.4rem 0;
        font-size: 1.1rem;
    }

    .domain-card p {
        color: #c2d4e1;
        font-size: 0.88rem;
        line-height: 1.5;
    }

    .domain-tag {
        color: #9edce0;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .section-intro {
        color: #aab4c5;
        margin-top: -0.4rem;
        margin-bottom: 1rem;
    }

    .capability-card {
        border-left: 3px solid #1596a3;
        padding: 0.35rem 0.8rem;
        margin-bottom: 0.8rem;
    }

    .muted {
        color: #aab4c5;
        font-size: 0.85rem;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #172b40, #1b3d50);
        border: 1px solid #31566b;
        padding: 16px;
        border-radius: 12px;
        min-height: 108px;
    }

    [data-testid="stMetricLabel"] {
        color: #c2d4e1 !important;
    }

    [data-testid="stMetricValue"] {
        color: #e3edf5 !important;
    }

    h1, h2, h3, h4 {
        color: #e3edf5 !important;
    }

    [data-testid="stCaptionContainer"] {
        color: #aab4c5 !important;
    }

    hr {
        border-color: #344354 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 5. EXTRACT DOMAIN METRICS
# =========================================================

upi = data["upi_summary"]
mf = data["mf_summary"]
dg = data["dg_summary"]
cl = data["cl_summary"]
cld = data["cl_disbursement"]
clr = data["cl_repayment"]

upi_total = number(upi, "total_transactions")
upi_success = number(upi, "successful_transactions")
upi_failed = number(upi, "failed_transactions")
upi_pending = number(upi, "pending_transactions")
upi_amount = number(upi, "successful_amount")
upi_success_rate = percentage(upi_success, upi_total)

mf_investors = number(mf, "total_investors")
mf_schemes = number(mf, "total_schemes")
mf_nav = number(mf, "total_nav_records")
mf_total = number(mf, "total_transactions")
mf_success = number(mf, "successful_transactions")
mf_purchase = number(mf, "successful_purchases")
mf_redemption = number(mf, "successful_redemptions")
mf_net_investment = mf_purchase - mf_redemption
mf_success_rate = percentage(mf_success, mf_total)

dg_customers = number(dg, "total_customers")
dg_ledger = number(dg, "total_ledger_entries")
dg_price_records = number(dg, "total_price_records")
dg_total = number(dg, "total_transactions")
dg_success = number(dg, "successful_transactions")
dg_buy_amount = number(dg, "successful_buy_amount")
dg_sell_amount = number(dg, "successful_sell_amount")
dg_buy_grams = number(dg, "successful_buy_grams")
dg_sell_grams = number(dg, "successful_sell_grams")
dg_net_grams = dg_buy_grams - dg_sell_grams
dg_success_rate = percentage(dg_success, dg_total)

cl_customers = number(cl, "total_customers")
cl_applications = number(cl, "total_applications")
cl_approved = number(cl, "approved_applications")
cl_rejected = number(cl, "rejected_applications")
cl_approval_rate = percentage(cl_approved, cl_applications)

cl_success_disbursements = number(cld, "successful_disbursements")
cl_disbursed_amount = number(cld, "successful_disbursed_amount")
cl_total_due = number(clr, "total_due")
cl_collected = number(clr, "total_collected")
cl_overdue = number(clr, "overdue_outstanding")
cl_overdue_count = number(clr, "overdue_installments")
cl_collection_rate = percentage(cl_collected, cl_total_due)


# =========================================================
# 6. HERO
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">
            FINANCIAL DATA PLATFORM · PORTFOLIO OVERVIEW
        </div>
        <h1>FINTECH 360°</h1>
        <div class="hero-subtitle">
            End-to-End Financial Data Engineering, Analytics
            &amp; Business Intelligence Platform
        </div>
        <div class="hero-description">
            A unified analytical platform covering UPI Payments,
            Mutual Funds, Digital Gold and Cash Loans.
            Transforming synthetic financial data into trusted
            datasets and actionable business insights.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    FINTECH 360° demonstrates the complete data lifecycle:
    synthetic data generation, ingestion, data quality,
    transformation, warehouse loading, SQL analytical modelling,
    Python business analytics and interactive dashboards.
    """
)


# =========================================================
# 7. PORTFOLIO SNAPSHOT
# =========================================================

st.divider()
st.header("Portfolio at a Glance")

st.markdown(
    '<p class="section-intro">Four implemented fintech domains in one analytical platform.</p>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Financial Domains", "4")
col2.metric("UPI Transactions", fmt_number(upi_total))
col3.metric("Mutual Fund Transactions", fmt_number(mf_total))
col4.metric("Digital Gold Transactions", fmt_number(dg_total))

col1, col2, col3, col4 = st.columns(4)

col1.metric("Cash Loan Applications", fmt_number(cl_applications))
col2.metric("MF Investors", fmt_number(mf_investors))
col3.metric("Digital Gold Customers", fmt_number(dg_customers))
col4.metric("Cash Loan Customers", fmt_number(cl_customers))

st.caption(
    "Domain counts represent different business entities and activities. "
    "They should not be interpreted as one common transaction measure."
)


# =========================================================
# 8. FOUR DOMAIN CARDS
# =========================================================

st.divider()
st.header("Four Financial Business Domains")

domain_cols = st.columns(4)

domains = [
    {
        "icon": "💳",
        "name": "UPI Payments",
        "description": (
            "Digital payment transactions, payment success, "
            "bank performance and failure analysis."
        ),
        "detail": f"{upi_total:,.0f} transactions",
    },
    {
        "icon": "📈",
        "name": "Mutual Funds",
        "description": (
            "Investor behaviour, scheme performance, "
            "purchase and redemption analytics."
        ),
        "detail": f"{mf_investors:,.0f} investors · {mf_schemes} schemes",
    },
    {
        "icon": "🪙",
        "name": "Digital Gold",
        "description": (
            "Gold purchases, sales, wallet ledger, "
            "customer activity and gold quantities."
        ),
        "detail": f"{dg_customers:,.0f} customers",
    },
    {
        "icon": "💰",
        "name": "Cash Loans",
        "description": (
            "Loan applications, approval, disbursement, "
            "repayment and overdue analysis."
        ),
        "detail": f"{cl_applications:,.0f} applications",
    },
]

for col, domain in zip(domain_cols, domains):
    with col:
        st.markdown(
            f"""
            <div class="domain-card">
                <div style="font-size:1.8rem">{domain["icon"]}</div>
                <div class="domain-tag">IMPLEMENTED</div>
                <h3>{domain["name"]}</h3>
                <p>{domain["description"]}</p>
                <div class="muted">{domain["detail"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# 9. DOMAIN PERFORMANCE
# =========================================================

st.divider()
st.header("Domain Performance Overview")

st.subheader("UPI Payments")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Transactions", fmt_number(upi_total))
col2.metric("Successful", fmt_number(upi_success))
col3.metric("Success Rate", f"{upi_success_rate:.2f}%")
col4.metric("Successful Payment Value", inr_lakh(upi_amount))

st.subheader("Mutual Funds")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Investors", fmt_number(mf_investors))
col2.metric("Schemes", fmt_number(mf_schemes))
col3.metric("Successful Purchases", inr_crore(mf_purchase))
col4.metric("Successful Redemptions", inr_crore(mf_redemption))

st.metric("Net Successful Investment Flow", inr_crore(mf_net_investment))
st.caption(
    "Net investment flow = successful purchase amount minus successful "
    "redemption amount. It is not NAV-based investment return or AUM."
)

st.subheader("Digital Gold")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Customers", fmt_number(dg_customers))
col2.metric("Transactions", fmt_number(dg_total))
col3.metric("Success Rate", f"{dg_success_rate:.2f}%")
col4.metric("Wallet Ledger Entries", fmt_number(dg_ledger))

col1, col2, col3 = st.columns(3)
col1.metric("Successful Buy Quantity", f"{dg_buy_grams:,.2f} g")
col2.metric("Successful Sell Quantity", f"{dg_sell_grams:,.2f} g")
col3.metric("Net Gold Quantity", f"{dg_net_grams:,.2f} g")

st.caption(
    "Net gold quantity = successful BUY quantity minus successful SELL "
    "quantity. It is not portfolio valuation or investment return."
)

st.subheader("Cash Loans")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Applications", fmt_number(cl_applications))
col2.metric("Approved Applications", fmt_number(cl_approved))
col3.metric("Approval Rate", f"{cl_approval_rate:.2f}%")
col4.metric("Successful Disbursements", fmt_number(cl_success_disbursements))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Successfully Disbursed", inr_crore(cl_disbursed_amount))
col2.metric("Amount Collected", inr_crore(cl_collected))
col3.metric("Collection Rate", f"{cl_collection_rate:.2f}%")
col4.metric("Overdue Outstanding", inr_lakh(cl_overdue))

st.caption(
    "Disbursed amount includes successful disbursements only. "
    "Collection rate = amount paid divided by total repayment due. "
    "Overdue outstanding includes installments classified as OVERDUE."
)


# =========================================================
# 10. TRANSACTION STATUS COMPARISON
# =========================================================

st.divider()
st.header("Transaction and Application Status")

left, right = st.columns(2)

with left:
    st.subheader("UPI Transaction Status")
    upi_status = data["upi_status"]

    fig = px.pie(
        upi_status,
        names="status",
        values="transaction_count",
        hole=0.5,
        title="UPI Transactions by Status",
    )
    st.plotly_chart(chart_theme(fig), use_container_width=True)

with right:
    st.subheader("Mutual Fund Transaction Status")
    mf_status = data["mf_status"]

    mf_status_chart = (
        mf_status.groupby("transaction_status", as_index=False)
        ["transaction_count"].sum()
    )

    fig = px.pie(
        mf_status_chart,
        names="transaction_status",
        values="transaction_count",
        hole=0.5,
        title="Mutual Fund Transactions by Status",
    )
    st.plotly_chart(chart_theme(fig), use_container_width=True)

left, right = st.columns(2)

with left:
    st.subheader("Digital Gold Transaction Status")
    dg_status = data["dg_status"]

    dg_status_chart = (
        dg_status.groupby("transaction_status", as_index=False)
        ["transaction_count"].sum()
    )

    fig = px.pie(
        dg_status_chart,
        names="transaction_status",
        values="transaction_count",
        hole=0.5,
        title="Digital Gold Transactions by Status",
    )
    st.plotly_chart(chart_theme(fig), use_container_width=True)

with right:
    st.subheader("Cash Loan Application Status")
    cl_status = data["cl_application_status"]

    fig = px.bar(
        cl_status.sort_values("application_count"),
        x="application_count",
        y="application_status",
        orientation="h",
        color="application_status",
        title="Loan Applications by Status",
        labels={
            "application_count": "Applications",
            "application_status": "Application Status",
        },
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(chart_theme(fig), use_container_width=True)


# =========================================================
# 11. FINANCIAL ACTIVITY COMPARISON
# =========================================================

st.divider()
st.header("Financial Activity by Domain")

activity = pd.DataFrame([
    {
        "Domain": "UPI Payments",
        "Activity": "Successful payment value",
        "Amount": upi_amount,
    },
    {
        "Domain": "Mutual Funds",
        "Activity": "Successful purchase amount",
        "Amount": mf_purchase,
    },
    {
        "Domain": "Digital Gold",
        "Activity": "Successful BUY amount",
        "Amount": dg_buy_amount,
    },
    {
        "Domain": "Cash Loans",
        "Activity": "Successful disbursement amount",
        "Amount": cl_disbursed_amount,
    },
])

fig = px.bar(
    activity,
    x="Domain",
    y="Amount",
    color="Domain",
    text=activity["Amount"].apply(inr_crore),
    title="Successful Financial Activity by Domain",
    labels={"Amount": "Amount (₹)", "Domain": "Business Domain"},
)
fig.update_traces(textposition="outside")
fig.update_layout(showlegend=False)
st.plotly_chart(chart_theme(fig, 440), use_container_width=True)

st.caption(
    "This chart compares different types of successful financial activity. "
    "It does not represent consolidated revenue, profit, AUM or portfolio value."
)


# =========================================================
# 12. MONTHLY ACTIVITY TRENDS
# =========================================================

st.divider()
st.header("Monthly Business Activity Trends")

monthly_data = {
    "UPI Payments": data["upi_monthly"],
    "Mutual Funds": data["mf_monthly"],
    "Digital Gold": data["dg_monthly"],
    "Cash Loans": data["cl_monthly"],
}

for name, frame in monthly_data.items():
    if "activity_month" in frame.columns:
        frame["activity_month"] = pd.to_datetime(
            frame["activity_month"], errors="coerce"
        )

left, right = st.columns(2)

with left:
    st.subheader("UPI Payment Activity")

    upi_monthly = data["upi_monthly"].dropna(
        subset=["activity_month"]
    )

    if not upi_monthly.empty:
        fig = px.line(
            upi_monthly,
            x="activity_month",
            y="total_transactions",
            markers=True,
            title="Monthly UPI Transaction Volume",
            labels={
                "activity_month": "Month",
                "total_transactions": "Transactions",
            },
        )
        st.plotly_chart(chart_theme(fig), use_container_width=True)
    else:
        st.info("No UPI monthly data available.")

with right:
    st.subheader("Mutual Fund Investment Activity")

    mf_monthly = data["mf_monthly"].dropna(
        subset=["activity_month"]
    )

    if not mf_monthly.empty:
        mf_flow = mf_monthly.melt(
            id_vars="activity_month",
            value_vars=["purchase_amount", "redemption_amount"],
            var_name="flow_type",
            value_name="amount",
        )

        mf_flow["flow_type"] = mf_flow["flow_type"].replace({
            "purchase_amount": "Successful Purchases",
            "redemption_amount": "Successful Redemptions",
        })

        fig = px.line(
            mf_flow,
            x="activity_month",
            y="amount",
            color="flow_type",
            markers=True,
            title="Monthly Mutual Fund Flows",
            labels={
                "activity_month": "Month",
                "amount": "Amount (₹)",
                "flow_type": "Activity",
            },
        )
        st.plotly_chart(chart_theme(fig), use_container_width=True)
    else:
        st.info("No Mutual Fund monthly data available.")

left, right = st.columns(2)

with left:
    st.subheader("Digital Gold Activity")

    dg_monthly = data["dg_monthly"].dropna(
        subset=["activity_month"]
    )

    if not dg_monthly.empty:
        fig = px.line(
            dg_monthly,
            x="activity_month",
            y="total_transactions",
            markers=True,
            title="Monthly Digital Gold Transactions",
            labels={
                "activity_month": "Month",
                "total_transactions": "Transactions",
            },
        )
        st.plotly_chart(chart_theme(fig), use_container_width=True)
    else:
        st.info("No Digital Gold monthly data available.")

with right:
    st.subheader("Cash Loan Application Activity")

    cl_monthly = data["cl_monthly"].dropna(
        subset=["activity_month"]
    )

    if not cl_monthly.empty:
        cl_flow = cl_monthly.melt(
            id_vars="activity_month",
            value_vars=["total_applications", "approved_applications"],
            var_name="application_type",
            value_name="application_count",
        )

        cl_flow["application_type"] = cl_flow["application_type"].replace({
            "total_applications": "Total Applications",
            "approved_applications": "Approved Applications",
        })

        fig = px.line(
            cl_flow,
            x="activity_month",
            y="application_count",
            color="application_type",
            markers=True,
            title="Monthly Cash Loan Applications",
            labels={
                "activity_month": "Month",
                "application_count": "Applications",
                "application_type": "Application Type",
            },
        )
        st.plotly_chart(chart_theme(fig), use_container_width=True)
    else:
        st.info("No Cash Loan monthly data available.")


# =========================================================
# 13. BUSINESS HIGHLIGHTS
# =========================================================

st.divider()
st.header("Business Highlights")

highlight_cols = st.columns(2)

with highlight_cols[0]:
    st.subheader("UPI Payments")
    st.markdown(
        f"""
        - **{upi_success_rate:.2f}%** transaction success rate.
        - **{upi_success:,.0f}** successful payments.
        - **{inr_lakh(upi_amount)}** successful payment value.
        - **{upi_failed:,.0f}** failed and **{upi_pending:,.0f}**
          pending transactions.
        """
    )

    st.subheader("Mutual Funds")
    st.markdown(
        f"""
        - **{mf_investors:,.0f}** investors across **{mf_schemes}** schemes.
        - **{inr_crore(mf_purchase)}** successful purchase amount.
        - **{inr_crore(mf_redemption)}** successful redemption amount.
        - **{inr_crore(mf_net_investment)}** net successful investment flow.
        """
    )

with highlight_cols[1]:
    st.subheader("Digital Gold")
    st.markdown(
        f"""
        - **{dg_customers:,.0f}** customers.
        - **{dg_success:,.0f}** successful transactions.
        - **{dg_buy_grams:,.2f} g** successful BUY quantity.
        - **{dg_net_grams:,.2f} g** net successful gold quantity.
        """
    )

    st.subheader("Cash Loans")
    st.markdown(
        f"""
        - **{cl_applications:,.0f}** loan applications.
        - **{cl_approval_rate:.2f}%** application approval rate.
        - **{inr_crore(cl_disbursed_amount)}** successful disbursements.
        - **{inr_lakh(cl_overdue)}** overdue outstanding across
          **{cl_overdue_count:,.0f}** overdue installments.
        """
    )


# =========================================================
# 14. ENGINEERING ARCHITECTURE
# =========================================================

st.divider()
st.header("End-to-End Data Engineering Architecture")

st.markdown(
    '<p class="section-intro">A common engineering workflow powering all four financial domains.</p>',
    unsafe_allow_html=True,
)

architecture = [
    ("01", "Synthetic Data", "Financial source datasets"),
    ("02", "Ingestion", "CSV and Python pipelines"),
    ("03", "Data Quality", "Validation and reconciliation"),
    ("04", "Transformation", "Cleaning and standardization"),
    ("05", "Data Warehouse", "Centralized SQLite storage"),
    ("06", "SQL Analytics", "Analytical models and marts"),
    ("07", "Business Insights", "Python and Pandas analysis"),
    ("08", "Business Intelligence", "Streamlit and Plotly"),
]

for start in range(0, len(architecture), 4):
    cols = st.columns(4)

    for col, (number_value, name, detail) in zip(
        cols, architecture[start:start + 4]
    ):
        with col:
            st.markdown(
                f"""
                <div class="domain-card" style="min-height:112px;text-align:center">
                    <div class="domain-tag">{number_value}</div>
                    <h3>{name}</h3>
                    <div class="muted">{detail}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if start == 0:
        st.markdown(
            '<div style="text-align:center;color:#9edce0;padding:0.4rem">↓</div>',
            unsafe_allow_html=True,
        )


# =========================================================
# 15. ENGINEERING CAPABILITIES
# =========================================================

st.divider()
st.header("Data Engineering Capabilities Demonstrated")

capability_cols = st.columns(2)

with capability_cols[0]:
    capabilities = [
        (
            "Data Generation and Ingestion",
            "Synthetic datasets, CSV ingestion and source loading.",
        ),
        (
            "Data Quality Engineering",
            "Validation, rejected-record handling and reconciliation.",
        ),
        (
            "Data Transformation",
            "Cleaning, standardization and curated datasets.",
        ),
        (
            "Data Modelling",
            "Relational tables and analytical data marts.",
        ),
    ]

    for title, description in capabilities:
        st.markdown(
            f"""
            <div class="capability-card">
                <strong>{title}</strong><br>
                <span class="muted">{description}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

with capability_cols[1]:
    capabilities = [
        (
            "SQL Analytics",
            "Analytical queries, aggregations and reusable marts.",
        ),
        (
            "Python Analytics",
            "Pandas-based metrics and business insights.",
        ),
        (
            "Automated Testing",
            "Pytest and domain-level data quality checks.",
        ),
        (
            "Business Intelligence",
            "Interactive Streamlit dashboards and Plotly charts.",
        ),
    ]

    for title, description in capabilities:
        st.markdown(
            f"""
            <div class="capability-card">
                <strong>{title}</strong><br>
                <span class="muted">{description}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# 16. TECHNOLOGY STACK
# =========================================================

st.divider()
st.header("Technology Stack")

technology = [
    ("Programming", "Python"),
    ("Data Processing", "Pandas"),
    ("Database", "SQLite"),
    ("Query Language", "SQL"),
    ("Visualization", "Streamlit and Plotly"),
    ("Testing", "Pytest"),
    ("Version Control", "Git and GitHub"),
]

tech_cols = st.columns(4)

for index, (area, tools) in enumerate(technology):
    with tech_cols[index % 4]:
        st.markdown(f"**{area}**")
        st.caption(tools)


# =========================================================
# 17. NAVIGATION
# =========================================================

st.divider()
st.header("Explore the Four Business Platforms")

st.markdown(
    """
    All four domain dashboards are integrated into the unified
    FINTECH 360° application. Use the **Business Platforms** section
    in the sidebar to explore:

    - **UPI Payments:** Transaction performance and payment analytics.
    - **Mutual Funds:** Investor, scheme and investment analytics.
    - **Digital Gold:** Customer, gold transaction and wallet analytics.
    - **Cash Loans:** Applications, disbursements and repayment analytics.
    """
)


# =========================================================
# 18. DISCLAIMER AND FOOTER
# =========================================================

st.divider()

st.info(
    "All datasets used in FINTECH 360° are synthetic and created "
    "for educational and portfolio demonstration purposes. "
    "They do not represent real customers or financial transactions."
)

st.caption(
    "Financial amounts are domain-specific and should not be added "
    "together as consolidated revenue, profit, AUM or portfolio value."
)

st.caption(
    "FINTECH 360° | End-to-End Financial Data Engineering, Analytics & BI"
)
