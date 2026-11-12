import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "warehouse" / "database" / "fintech360.db"
ANALYTICS_DIR = BASE_DIR / "data" / "warehouse" / "cash_loans"
INSIGHTS_DIR = ANALYTICS_DIR / "business_insights"

st.set_page_config(
    page_title="FINTECH 360 | Cash Loans",
    page_icon="💰",
    layout="wide",
)


# ==================================================
# 2. DATA LOADING
# ==================================================

@st.cache_data
def load_data():

    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        applications = pd.read_sql_query(
            """
            SELECT
                a.*,
                c.customer_name,
                c.customer_segment,
                c.city,
                c.age,
                c.gender,
                p.product_name,
                p.loan_type,
                p.annual_interest_rate,
                p.processing_fee_percentage
            FROM cl_loan_applications a
            LEFT JOIN cl_customers c
                ON a.customer_id = c.customer_id
            LEFT JOIN cl_loan_products p
                ON a.product_id = p.product_id
            """,
            conn,
        )

        disbursements = pd.read_sql_query(
            """
            SELECT
                d.*,
                a.customer_id,
                a.product_id,
                a.application_date,
                a.employment_type,
                a.application_status,
                c.customer_name,
                c.customer_segment,
                c.city,
                p.product_name,
                p.loan_type
            FROM cl_loan_disbursements d
            LEFT JOIN cl_loan_applications a
                ON d.application_id = a.application_id
            LEFT JOIN cl_customers c
                ON a.customer_id = c.customer_id
            LEFT JOIN cl_loan_products p
                ON a.product_id = p.product_id
            """,
            conn,
        )

        repayments = pd.read_sql_query(
            """
            SELECT
                r.*,
                d.application_id,
                d.disbursement_date,
                a.customer_id,
                a.product_id,
                a.employment_type,
                c.customer_name,
                c.customer_segment,
                c.city,
                p.product_name,
                p.loan_type
            FROM cl_loan_repayments r
            LEFT JOIN cl_loan_disbursements d
                ON r.disbursement_id = d.disbursement_id
            LEFT JOIN cl_loan_applications a
                ON d.application_id = a.application_id
            LEFT JOIN cl_customers c
                ON a.customer_id = c.customer_id
            LEFT JOIN cl_loan_products p
                ON a.product_id = p.product_id
            """,
            conn,
        )

    for frame, column in [
        (applications, "application_date"),
        (disbursements, "disbursement_date"),
        (disbursements, "application_date"),
        (repayments, "due_date"),
        (repayments, "payment_date"),
        (repayments, "disbursement_date"),
    ]:
        frame[column] = pd.to_datetime(frame[column], errors="coerce")

    for frame, columns in [
        (
            applications,
            ["requested_amount", "approved_amount", "credit_score", "monthly_income"],
        ),
        (disbursements, ["disbursed_amount"]),
        (
            repayments,
            [
                "principal_amount",
                "interest_amount",
                "total_due_amount",
                "amount_paid",
                "late_days",
            ],
        ),
    ]:
        for column in columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")

    analytics_files = {
        "segments": "cl_customer_segment_analysis.csv",
        "products": "cl_loan_product_performance.csv",
        "daily_applications": "cl_daily_application_trends.csv",
        "daily_disbursements": "cl_daily_disbursement_trends.csv",
        "repayment_performance": "cl_repayment_performance.csv",
        "employment": "cl_employment_type_analysis.csv",
    }

    insights_files = {
        "top_customers": "cl_top_customers.csv",
        "segment_insights": "cl_customer_segment_insights.csv",
        "product_insights": "cl_loan_product_insights.csv",
        "employment_insights": "cl_employment_type_insights.csv",
        "repayment_risk": "cl_repayment_risk_insights.csv",
        "monthly_flows": "cl_monthly_loan_flows.csv",
    }

    analytics = {}
    insights = {}

    for key, filename in analytics_files.items():
        path = ANALYTICS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {path}. Run cash_loan_analytics.py first."
            )
        analytics[key] = pd.read_csv(path)

    for key, filename in insights_files.items():
        path = INSIGHTS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {path}. Run cash_loan_business_insights.py first."
            )
        insights[key] = pd.read_csv(path)

    for frame, column in [
        (analytics["daily_applications"], "application_date"),
        (analytics["daily_disbursements"], "disbursement_date"),
        (analytics["repayment_performance"], "due_date"),
        (insights["repayment_risk"], "due_date"),
    ]:
        frame[column] = pd.to_datetime(frame[column], errors="coerce")

    insights["monthly_flows"]["activity_month"] = pd.to_datetime(
        insights["monthly_flows"]["activity_month"] + "-01",
        errors="coerce",
    )

    return applications, disbursements, repayments, analytics, insights


try:
    applications, disbursements, repayments, analytics, insights = load_data()
except Exception as error:
    st.error(f"Unable to load Cash Loans dashboard data: {error}")
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

    .fintech-hero {
        box-sizing: border-box;
        width: 100%;
        padding: 2.2rem 2rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #10243a 0%, #183e5c 55%, #176b75 100%);
        border: 1px solid rgba(158, 220, 224, 0.16);
        margin: 0 0 1.5rem 0;
    }

    .fintech-hero-kicker {
        color: #9edce0;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }

    .fintech-hero h1 {
        color: #ffffff !important;
        font-size: 2.65rem;
        font-weight: 700;
        margin: 0;
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

    [data-testid="stSidebar"] [data-testid="stDateInput"] [data-baseweb="input"],
    [data-testid="stSidebar"] [data-testid="stDateInput"] [data-baseweb="input"] > div,
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
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

    [data-testid="stSidebar"] [data-testid="stDateInput"] button,
    [data-testid="stSidebar"] [data-testid="stDateInput"] button svg {
        color: #9edce0 !important;
        fill: #9edce0 !important;
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #d9e8f1 !important;
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

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #172b40, #1b3d50);
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

    h1, h2, h3, h4 {
        color: #e3edf5 !important;
    }

    [data-testid="stCaptionContainer"] {
        color: #aabac9 !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #344b60;
        border-radius: 10px;
    }

    .stDownloadButton button {
        background: linear-gradient(120deg, #183e5c, #176b75);
        color: #ffffff !important;
        border: 1px solid #38bdf8;
        border-radius: 8px;
    }

    .stDownloadButton button:hover {
        background: #176b75;
        color: #ffffff !important;
        border-color: #9edce0;
    }

    hr {
        border-color: #344354 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
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
            Cash Loans Analytics Dashboard
        </div>
        <div class="fintech-hero-description">
            End-to-End Financial Data Engineering, Analytics
            &amp; Business Intelligence Platform
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()


# ==================================================
# 5. SIDEBAR FILTERS
# ==================================================

st.sidebar.header("Dashboard Filters")

valid_dates = applications["application_date"].dropna()

if valid_dates.empty:
    st.error("No valid application dates found.")
    st.stop()

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

st.sidebar.subheader("Application Date Range")

start_date = st.sidebar.date_input(
    "Start Date",
    value=min_date,
    min_value=min_date,
    max_value=max_date,
    key="cl_start_date",
)

end_date = st.sidebar.date_input(
    "End Date",
    value=max_date,
    min_value=min_date,
    max_value=max_date,
    key="cl_end_date",
)

if start_date > end_date:
    st.sidebar.error("Start Date cannot be after End Date.")
    st.stop()

st.sidebar.divider()

segments = sorted(applications["customer_segment"].dropna().unique())
selected_segments = st.sidebar.multiselect(
    "Customer Segment", segments, default=segments
)

cities = sorted(applications["city"].dropna().unique())
selected_cities = st.sidebar.multiselect(
    "Customer City", cities, default=cities
)

loan_types = sorted(applications["loan_type"].dropna().unique())
selected_loan_types = st.sidebar.multiselect(
    "Loan Type", loan_types, default=loan_types
)

employment_types = sorted(applications["employment_type"].dropna().unique())
selected_employment_types = st.sidebar.multiselect(
    "Employment Type", employment_types, default=employment_types
)

statuses = sorted(applications["application_status"].dropna().unique())
selected_statuses = st.sidebar.multiselect(
    "Application Status", statuses, default=statuses
)

st.sidebar.divider()
st.sidebar.caption("FINTECH 360° | Cash Loans Module")


# ==================================================
# 6. APPLY FILTERS AND BUILD APPLICATION COHORT
# ==================================================

start_timestamp = pd.Timestamp(start_date)
end_timestamp = pd.Timestamp(end_date) + pd.Timedelta(days=1)

filtered_applications = applications[
    (applications["application_date"] >= start_timestamp)
    & (applications["application_date"] < end_timestamp)
    & (applications["customer_segment"].isin(selected_segments))
    & (applications["city"].isin(selected_cities))
    & (applications["loan_type"].isin(selected_loan_types))
    & (applications["employment_type"].isin(selected_employment_types))
    & (applications["application_status"].isin(selected_statuses))
].copy()

application_ids = set(filtered_applications["application_id"])

filtered_disbursements = disbursements[
    disbursements["application_id"].isin(application_ids)
].copy()

disbursement_ids = set(filtered_disbursements["disbursement_id"])

filtered_repayments = repayments[
    repayments["disbursement_id"].isin(disbursement_ids)
].copy()

st.write(
    f"Showing applications from {start_date.strftime('%d %b %Y')} "
    f"to {end_date.strftime('%d %b %Y')}"
)
st.write(
    f"Filtered Applications: {len(filtered_applications):,} "
    f"| Related Disbursements: {len(filtered_disbursements):,} "
    f"| Related Installments: {len(filtered_repayments):,}"
)
st.caption(
    "The date filter is based on application date. Disbursement and repayment "
    "metrics include all records linked to applications in the selected cohort, "
    "including installments due after the selected application date range."
)


# ==================================================
# 7. KEY PERFORMANCE INDICATORS
# ==================================================

st.header("Key Performance Indicators")

total_customers = filtered_applications["customer_id"].nunique()
total_applications = len(filtered_applications)

approved_applications = filtered_applications[
    filtered_applications["application_status"] == "APPROVED"
]
rejected_applications = filtered_applications[
    filtered_applications["application_status"] == "REJECTED"
]

approval_rate = (
    len(approved_applications) / total_applications * 100
    if total_applications else 0
)

successful_disbursements = filtered_disbursements[
    filtered_disbursements["disbursement_status"] == "SUCCESS"
]
failed_disbursements = filtered_disbursements[
    filtered_disbursements["disbursement_status"] == "FAILED"
]
pending_disbursements = filtered_disbursements[
    filtered_disbursements["disbursement_status"] == "PENDING"
]

total_disbursed = successful_disbursements["disbursed_amount"].sum()
total_due = filtered_repayments["total_due_amount"].sum()
total_collected = filtered_repayments["amount_paid"].sum()
total_outstanding = (
    filtered_repayments["total_due_amount"]
    - filtered_repayments["amount_paid"]
).sum()

overdue = filtered_repayments[
    filtered_repayments["repayment_status"] == "OVERDUE"
]
overdue_outstanding = (
    overdue["total_due_amount"] - overdue["amount_paid"]
).sum()

collection_rate = total_collected / total_due * 100 if total_due else 0
disbursement_success_rate = (
    len(successful_disbursements) / len(filtered_disbursements) * 100
    if len(filtered_disbursements) else 0
)


def format_inr_crore(amount):
    return f"₹{amount / 10_000_000:,.2f} Cr"


col1, col2, col3, col4 = st.columns(4)
col1.metric("Customers", f"{total_customers:,}")
col2.metric("Loan Applications", f"{total_applications:,}")
col3.metric("Approval Rate", f"{approval_rate:.2f}%")
col4.metric("Successful Disbursements", f"{len(successful_disbursements):,}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Disbursed", format_inr_crore(total_disbursed))
col2.metric("Amount Collected", format_inr_crore(total_collected))
col3.metric("Total Outstanding", format_inr_crore(total_outstanding))
col4.metric("Overdue Outstanding", format_inr_crore(overdue_outstanding))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Rejected Applications", f"{len(rejected_applications):,}")
col2.metric("Failed Disbursements", f"{len(failed_disbursements):,}")
col3.metric("Pending Disbursements", f"{len(pending_disbursements):,}")
col4.metric("Repayment Collection Rate", f"{collection_rate:.2f}%")

st.caption(f"Disbursement success rate: {disbursement_success_rate:.2f}%.")
st.divider()


# ==================================================
# 8. CUSTOMER BEHAVIOUR ANALYSIS
# ==================================================

st.header("Customer Behaviour Analysis")
left, right = st.columns(2)

with left:
    st.subheader("Customer Segment Distribution")
    if not filtered_applications.empty:
        segment_data = (
            filtered_applications.groupby("customer_segment", as_index=False)
            .agg(total_customers=("customer_id", "nunique"))
        )
        fig = px.pie(
            segment_data,
            names="customer_segment",
            values="total_customers",
            hole=0.45,
            title="Customers by Segment",
        )
        fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No customer data available.")

with right:
    st.subheader("Top 10 Customers by Disbursed Amount")
    customer_data = filtered_applications[
        ["customer_id", "customer_name", "customer_segment"]
    ].drop_duplicates()

    if not customer_data.empty:
        customer_disbursed = (
            successful_disbursements.groupby("customer_id", as_index=False)
            .agg(total_disbursed_amount=("disbursed_amount", "sum"))
        )
        customer_data = customer_data.merge(
            customer_disbursed, on="customer_id", how="left"
        )
        customer_data["total_disbursed_amount"] = (
            customer_data["total_disbursed_amount"].fillna(0)
        )
        top_customers = customer_data.nlargest(10, "total_disbursed_amount")

        fig = px.bar(
            top_customers.sort_values("total_disbursed_amount"),
            x="total_disbursed_amount",
            y="customer_name",
            color="customer_segment",
            orientation="h",
            title="Top Customers by Successful Disbursement",
            labels={
                "total_disbursed_amount": "Disbursed Amount (₹)",
                "customer_name": "Customer",
            },
        )
        fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No customer data available.")

st.divider()


# ==================================================
# 9. LOAN APPLICATION ANALYSIS
# ==================================================

st.header("Loan Application Analysis")
left, right = st.columns(2)

with left:
    st.subheader("Application Status Distribution")
    if not filtered_applications.empty:
        status_data = (
            filtered_applications.groupby("application_status", as_index=False)
            .size()
            .rename(columns={"size": "total_applications"})
        )
        fig = px.pie(
            status_data,
            names="application_status",
            values="total_applications",
            hole=0.45,
            title="Applications by Status",
        )
        fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No application data available.")

with right:
    st.subheader("Applications by Employment Type")
    if not filtered_applications.empty:
        employment_data = (
            filtered_applications.groupby("employment_type", as_index=False)
            .size()
            .rename(columns={"size": "total_applications"})
        )
        fig = px.bar(
            employment_data.sort_values("total_applications"),
            x="total_applications",
            y="employment_type",
            color="employment_type",
            orientation="h",
            title="Applications by Employment Type",
            labels={
                "total_applications": "Applications",
                "employment_type": "Employment Type",
            },
        )
        fig.update_layout(height=460, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No employment data available.")

if not filtered_applications.empty:
    amount_data = (
        filtered_applications.groupby("application_status", as_index=False)
        .agg(
            requested_amount=("requested_amount", "sum"),
            approved_amount=("approved_amount", "sum"),
        )
    )
    amount_chart = amount_data.melt(
        id_vars="application_status",
        value_vars=["requested_amount", "approved_amount"],
        var_name="amount_type",
        value_name="amount",
    )
    amount_chart["amount_type"] = amount_chart["amount_type"].replace(
        {
            "requested_amount": "Requested Amount",
            "approved_amount": "Approved Amount",
        }
    )
    fig = px.bar(
        amount_chart,
        x="application_status",
        y="amount",
        color="amount_type",
        barmode="group",
        title="Requested and Approved Amount by Application Status",
        labels={"amount": "Amount (₹)", "application_status": "Status"},
    )
    fig.update_layout(height=460)
    st.plotly_chart(fig, use_container_width=True)

st.divider()


# ==================================================
# 10. LOAN PRODUCT PERFORMANCE
# ==================================================

st.header("Loan Product Performance")

if not filtered_applications.empty:
    product_data = (
        filtered_applications.groupby(
            ["product_name", "loan_type"], as_index=False
        )
        .agg(
            total_applications=("application_id", "count"),
            approved_applications=(
                "application_status",
                lambda values: (values == "APPROVED").sum(),
            ),
            total_requested_amount=("requested_amount", "sum"),
            total_approved_amount=("approved_amount", "sum"),
        )
    )
    product_data["approval_rate_percentage"] = (
        product_data["approved_applications"]
        / product_data["total_applications"].replace(0, pd.NA)
        * 100
    ).fillna(0)

    left, right = st.columns(2)
    with left:
        fig = px.bar(
            product_data.sort_values("total_applications"),
            x="total_applications",
            y="product_name",
            color="loan_type",
            orientation="h",
            title="Applications by Loan Product",
        )
        fig.update_layout(height=520)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.bar(
            product_data.sort_values("approval_rate_percentage"),
            x="approval_rate_percentage",
            y="product_name",
            color="loan_type",
            orientation="h",
            title="Approval Rate by Loan Product",
            labels={"approval_rate_percentage": "Approval Rate (%)"},
        )
        fig.update_layout(height=520)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Loan Product Performance Table")
    st.dataframe(
        product_data.sort_values("total_requested_amount", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No loan product data available.")

st.divider()


# ==================================================
# 11. DISBURSEMENT ANALYSIS
# ==================================================

st.header("Disbursement Analysis")

if not filtered_disbursements.empty:
    status_data = (
        filtered_disbursements.groupby("disbursement_status", as_index=False)
        .size()
        .rename(columns={"size": "total_disbursements"})
    )
    product_disbursement = (
        successful_disbursements.groupby("product_name", as_index=False)
        .agg(total_disbursed_amount=("disbursed_amount", "sum"))
    )

    left, right = st.columns(2)
    with left:
        fig = px.pie(
            status_data,
            names="disbursement_status",
            values="total_disbursements",
            hole=0.45,
            title="Disbursement Status Distribution",
        )
        fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.bar(
            product_disbursement.sort_values("total_disbursed_amount"),
            x="total_disbursed_amount",
            y="product_name",
            orientation="h",
            title="Successful Disbursed Amount by Product",
            labels={"total_disbursed_amount": "Disbursed Amount (₹)"},
        )
        fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Disbursement Records")
    st.dataframe(
        filtered_disbursements.sort_values(
            "disbursement_date", ascending=False, na_position="last"
        ),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No disbursement records for the selected applications.")

st.divider()


# ==================================================
# 12. REPAYMENT AND CREDIT RISK ANALYSIS
# ==================================================

st.header("Repayment and Credit Risk Analysis")

if not filtered_repayments.empty:
    repayment_status = (
        filtered_repayments.groupby("repayment_status", as_index=False)
        .size()
        .rename(columns={"size": "total_installments"})
    )

    repayment_amounts = (
        filtered_repayments.groupby("repayment_status", as_index=False)
        .agg(
            total_due=("total_due_amount", "sum"),
            total_collected=("amount_paid", "sum"),
        )
    )
    repayment_amounts["outstanding"] = (
        repayment_amounts["total_due"] - repayment_amounts["total_collected"]
    )

    left, right = st.columns(2)
    with left:
        fig = px.pie(
            repayment_status,
            names="repayment_status",
            values="total_installments",
            hole=0.45,
            title="Installments by Repayment Status",
        )
        fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        chart_data = repayment_amounts.melt(
            id_vars="repayment_status",
            value_vars=["total_due", "total_collected", "outstanding"],
            var_name="amount_type",
            value_name="amount",
        )
        chart_data["amount_type"] = chart_data["amount_type"].replace(
            {
                "total_due": "Total Due",
                "total_collected": "Collected",
                "outstanding": "Outstanding",
            }
        )
        fig = px.bar(
            chart_data,
            x="repayment_status",
            y="amount",
            color="amount_type",
            barmode="group",
            title="Due, Collected and Outstanding by Status",
            labels={"amount": "Amount (₹)", "repayment_status": "Status"},
        )
        fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)

    overdue_rows = filtered_repayments[
        filtered_repayments["repayment_status"] == "OVERDUE"
    ].copy()

    if not overdue_rows.empty:
        overdue_rows["overdue_outstanding"] = (
            overdue_rows["total_due_amount"] - overdue_rows["amount_paid"]
        )
        overdue_by_date = (
            overdue_rows.groupby("due_date", as_index=False)
            .agg(
                overdue_installments=("repayment_id", "count"),
                overdue_outstanding=("overdue_outstanding", "sum"),
            )
        )
        fig = px.line(
            overdue_by_date,
            x="due_date",
            y="overdue_outstanding",
            markers=True,
            title="Overdue Outstanding by Installment Due Date",
            labels={
                "due_date": "Due Date",
                "overdue_outstanding": "Overdue Outstanding (₹)",
            },
        )
        fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Repayment Performance Table")
    repayment_table = (
        filtered_repayments.groupby("repayment_status", as_index=False)
        .agg(
            total_installments=("repayment_id", "count"),
            total_due_amount=("total_due_amount", "sum"),
            total_amount_collected=("amount_paid", "sum"),
        )
    )
    repayment_table["outstanding_amount"] = (
        repayment_table["total_due_amount"]
        - repayment_table["total_amount_collected"]
    )
    st.dataframe(repayment_table, use_container_width=True, hide_index=True)
else:
    st.info("No repayment installments for the selected applications.")

st.divider()


# ==================================================
# 13. MONTHLY LOAN FLOW TRENDS
# ==================================================

st.header("Monthly Loan Flow Trends")

monthly_data = insights["monthly_flows"].copy()
monthly_start = start_timestamp.to_period("M").to_timestamp()
monthly_end = end_timestamp.to_period("M").to_timestamp()

monthly_filtered = monthly_data[
    (monthly_data["activity_month"] >= monthly_start)
    & (monthly_data["activity_month"] <= monthly_end)
].copy()

if not monthly_filtered.empty:
    count_chart = monthly_filtered.melt(
        id_vars="activity_month",
        value_vars=[
            "total_applications",
            "successful_disbursements",
            "total_installments",
        ],
        var_name="activity_type",
        value_name="record_count",
    )
    count_chart["activity_type"] = count_chart["activity_type"].replace(
        {
            "total_applications": "Applications",
            "successful_disbursements": "Successful Disbursements",
            "total_installments": "Repayment Installments",
        }
    )
    fig = px.line(
        count_chart,
        x="activity_month",
        y="record_count",
        color="activity_type",
        markers=True,
        title="Monthly Applications, Disbursements and Installments",
        labels={"activity_month": "Month", "record_count": "Records"},
    )
    fig.update_layout(height=460)
    st.plotly_chart(fig, use_container_width=True)

    amount_chart = monthly_filtered.melt(
        id_vars="activity_month",
        value_vars=[
            "total_disbursed_amount",
            "total_amount_collected",
            "total_outstanding_amount",
        ],
        var_name="amount_type",
        value_name="amount",
    )
    amount_chart["amount_type"] = amount_chart["amount_type"].replace(
        {
            "total_disbursed_amount": "Disbursed",
            "total_amount_collected": "Collected",
            "total_outstanding_amount": "Outstanding",
        }
    )
    fig = px.line(
        amount_chart,
        x="activity_month",
        y="amount",
        color="amount_type",
        markers=True,
        title="Monthly Disbursement and Repayment Amounts",
        labels={"activity_month": "Month", "amount": "Amount (₹)"},
    )
    fig.update_layout(height=460)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Loan Flow Dataset")
    st.dataframe(
        monthly_filtered.sort_values("activity_month", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No monthly loan flow data for the selected date range.")

st.divider()


# ==================================================
# 14. LOAN DATA EXPLORER
# ==================================================

st.header("Loan Data Explorer")
explorer_tabs = st.tabs(
    ["Applications", "Disbursements", "Repayments", "Business Insights"]
)

with explorer_tabs[0]:
    application_columns = [
        "application_id",
        "customer_id",
        "customer_name",
        "customer_segment",
        "city",
        "product_name",
        "loan_type",
        "application_date",
        "requested_amount",
        "approved_amount",
        "credit_score",
        "employment_type",
        "monthly_income",
        "application_status",
        "rejection_reason",
    ]
    application_explorer = filtered_applications[application_columns].sort_values(
        "application_date", ascending=False
    )
    st.dataframe(
        application_explorer, use_container_width=True, hide_index=True
    )
    st.download_button(
        "Download Filtered Applications",
        application_explorer.to_csv(index=False).encode("utf-8"),
        "cash_loan_filtered_applications.csv",
        "text/csv",
    )

with explorer_tabs[1]:
    st.dataframe(
        filtered_disbursements.sort_values(
            "disbursement_date", ascending=False, na_position="last"
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Download Related Disbursements",
        filtered_disbursements.to_csv(index=False).encode("utf-8"),
        "cash_loan_filtered_disbursements.csv",
        "text/csv",
    )

with explorer_tabs[2]:
    st.dataframe(
        filtered_repayments.sort_values("due_date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Download Related Repayments",
        filtered_repayments.to_csv(index=False).encode("utf-8"),
        "cash_loan_filtered_repayments.csv",
        "text/csv",
    )

with explorer_tabs[3]:
    insight_tabs = st.tabs(
        ["Top Customers", "Segments", "Products", "Employment", "Repayment Risk"]
    )
    insight_keys = [
        "top_customers",
        "segment_insights",
        "product_insights",
        "employment_insights",
        "repayment_risk",
    ]
    insight_files = [
        "cash_loan_top_customers.csv",
        "cash_loan_customer_segments.csv",
        "cash_loan_product_insights.csv",
        "cash_loan_employment_insights.csv",
        "cash_loan_repayment_risk.csv",
    ]

    for tab, key, filename in zip(insight_tabs, insight_keys, insight_files):
        with tab:
            insight_df = insights[key]
            st.dataframe(insight_df, use_container_width=True, hide_index=True)
            st.download_button(
                f"Download {key.replace('_', ' ').title()}",
                insight_df.to_csv(index=False).encode("utf-8"),
                filename,
                "text/csv",
                key=f"download_{key}",
            )


# ==================================================
# 15. FOOTER
# ==================================================

st.divider()
st.caption(
    "FINTECH 360° | Cash Loans Analytics | "
    "Built with Python, SQLite, Pandas, Streamlit and Plotly"
)
st.caption(
    "Note: This dashboard analyses synthetic loan activity. "
    "Disbursed amounts include successful disbursements only. "
    "Outstanding amounts represent unpaid installment amounts. "
    "Overdue outstanding includes installments classified as OVERDUE. "
    "These metrics do not represent lender profitability or a complete "
    "credit-risk assessment."
)