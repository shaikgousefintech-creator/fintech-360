
import streamlit as st


# ---------------------------------------------------------
# PAGE CONTENT
# Page configuration is managed centrally in app.py.
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    .hero {
        padding: 2.2rem 2rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #10243a 0%, #183e5c 55%, #176b75 100%);
        color: white;
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
        color: white;
        font-size: 2.65rem;
        margin: 0;
        line-height: 1.15;
    }
    .hero-subtitle {
        color: #d9e8f1;
        font-size: 1.12rem;
        margin-top: 0.8rem;
        margin-bottom: 0.4rem;
    }
    .hero-description {
        color: #c2d4e1;
        font-size: 0.96rem;
        max-width: 850px;
        line-height: 1.65;
    }
    .section-intro {
        color: #64748b;
        margin-top: -0.45rem;
        margin-bottom: 1.1rem;
    }
    .domain-card {
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 13px;
        padding: 1.1rem;
        min-height: 190px;
        background: rgba(128, 128, 128, 0.035);
    }
    .domain-card h3 {
        margin-top: 0.4rem;
        margin-bottom: 0.5rem;
        font-size: 1.12rem;
    }
    .domain-card p {
        font-size: 0.91rem;
        line-height: 1.5;
        margin-bottom: 0.8rem;
    }
    .status-live {
        color: #16865b;
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.7px;
    }
    .status-planned {
        color: #b7791f;
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.7px;
    }
    .architecture-step {
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 11px;
        padding: 0.9rem 0.55rem;
        min-height: 112px;
        text-align: center;
        background: rgba(128, 128, 128, 0.035);
    }
    .architecture-number {
        color: #1596a3;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 1px;
    }
    .architecture-name {
        font-weight: 700;
        font-size: 0.91rem;
        margin-top: 0.4rem;
    }
    .architecture-detail {
        color: #8492a6;
        font-size: 0.77rem;
        margin-top: 0.35rem;
    }
    .capability-card {
        border-left: 3px solid #1596a3;
        padding: 0.3rem 0.8rem;
        margin-bottom: 0.75rem;
    }
    .muted {
        color: #8492a6;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# HERO
# ---------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">Financial Data Platform · Portfolio Project</div>
        <h1>FINTECH 360°</h1>
        <div class="hero-subtitle">
            End-to-End Data Engineering, Analytics &amp; Business Intelligence Platform
        </div>
        <div class="hero-description">
            Transforming synthetic financial transaction data into trusted,
            analytics-ready datasets and actionable business insights through
            an end-to-end data engineering workflow.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    FINTECH 360° demonstrates how financial data moves through the complete
    data lifecycle — from generation and ingestion to validation,
    transformation, analytical modelling, business insights and interactive BI.
    """
)


# ---------------------------------------------------------
# PLATFORM SNAPSHOT
# ---------------------------------------------------------

st.subheader("Platform at a Glance")
st.markdown(
    '<p class="section-intro">A growing platform with two implemented fintech domains and two planned extensions.</p>',
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)

metrics = [
    ("4", "Fintech domains"),
    ("2", "Implemented platforms"),
    ("30,000", "Implemented transactions"),
    ("Python · SQL", "Core engineering"),
]

for col, (value, label) in zip(metric_cols, metrics):
    with col:
        st.metric(label=label, value=value)


# ---------------------------------------------------------
# BUSINESS DOMAINS
# ---------------------------------------------------------

st.divider()
st.header("Four Financial Domains")
st.markdown(
    '<p class="section-intro">A modular architecture designed to bring multiple financial products into one analytical platform.</p>',
    unsafe_allow_html=True,
)

domain_cols = st.columns(4)

domains = [
    {
        "icon": "💳",
        "name": "UPI Payments",
        "status": "IMPLEMENTED",
        "status_class": "status-live",
        "description": (
            "Transaction processing, payment performance, failure analysis, "
            "bank and payment-app insights."
        ),
        "detail": "10,000 synthetic transactions",
    },
    {
        "icon": "📈",
        "name": "Mutual Funds",
        "status": "IMPLEMENTED",
        "status_class": "status-live",
        "description": (
            "Investment transactions, investor behaviour, scheme analysis, "
            "investment modes and monthly flows."
        ),
        "detail": "20,000 synthetic transactions",
    },
    {
        "icon": "🪙",
        "name": "Digital Gold",
        "status": "PLANNED",
        "status_class": "status-planned",
        "description": (
            "Planned purchase and sell transactions, gold holdings, "
            "portfolio valuation and price movement analytics."
        ),
        "detail": "Future module",
    },
    {
        "icon": "🏦",
        "name": "Cash Loans",
        "status": "PLANNED",
        "status_class": "status-planned",
        "description": (
            "Planned loan applications, disbursements, repayments, "
            "outstanding balances and delinquency analytics."
        ),
        "detail": "Future module",
    },
]

for col, domain in zip(domain_cols, domains):
    with col:
        st.markdown(
            f"""
            <div class="domain-card">
                <div style="font-size:1.7rem">{domain["icon"]}</div>
                <div class="{domain["status_class"]}">{domain["status"]}</div>
                <h3>{domain["name"]}</h3>
                <p>{domain["description"]}</p>
                <div class="muted">{domain["detail"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------
# DATA ENGINEERING ARCHITECTURE
# ---------------------------------------------------------

st.divider()
st.header("End-to-End Data Engineering Architecture")
st.markdown(
    '<p class="section-intro">The engineering workflow that converts raw financial data into trusted business information.</p>',
    unsafe_allow_html=True,
)

architecture = [
    ("01", "Synthetic Data", "Financial source data"),
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
    for col, (number, name, detail) in zip(
        cols, architecture[start:start + 4]
    ):
        with col:
            st.markdown(
                f"""
                <div class="architecture-step">
                    <div class="architecture-number">{number}</div>
                    <div class="architecture-name">{name}</div>
                    <div class="architecture-detail">{detail}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    if start == 0:
        st.markdown(
            '<div style="text-align:center;color:#1596a3;padding:0.25rem">↓</div>',
            unsafe_allow_html=True,
        )

st.caption(
    "The architecture represents the overall platform workflow. "
    "Individual modules may implement different stages as development progresses."
)


# ---------------------------------------------------------
# IMPLEMENTED ENGINEERING WORK
# ---------------------------------------------------------

st.divider()
st.header("Engineering Work Completed")
st.markdown(
    '<p class="section-intro">Verified implementation highlights from the UPI and Mutual Funds modules.</p>',
    unsafe_allow_html=True,
)

left, right = st.columns(2)

with left:
    st.subheader("UPI Payments")
    st.markdown(
        """
        - Synthetic transaction data generation
        - CSV ingestion and rejected-record handling
        - Data validation and standardization
        - SQLite data loading
        - SQL validation and analytical data marts
        - Mart reconciliation checks
        - Pipeline orchestration and execution logging
        - Automated tests
        - Interactive dashboard and business insights
        """
    )
    st.metric("UPI transactions", "10,000")
    st.caption(
        "README validation results: 10,000 processed, 0 rejected, "
        "10 data quality checks passed, 24 mart reconciliation checks passed, "
        "35 automated tests passed."
    )

with right:
    st.subheader("Mutual Funds")
    st.markdown(
        """
        - Synthetic investor and investment transaction data
        - Scheme and NAV history datasets
        - Relational SQLite data model
        - Data quality and SQL validation
        - Four analytical data marts
        - Investor, scheme and category analytics
        - Investment mode and monthly flow insights
        - Interactive dashboard and transaction explorer
        """
    )
    st.metric("Mutual Fund transactions", "20,000")
    st.caption(
        "Completed validation suites: 36 mart checks, "
        "42 analytics checks and 33 business-insight checks passed."
    )


# ---------------------------------------------------------
# ANALYTICS AND BUSINESS INSIGHTS
# ---------------------------------------------------------

st.divider()
st.header("Analytics & Business Insights")

analytics_left, analytics_right = st.columns(2)

with analytics_left:
    st.subheader("UPI Payments Analytics")
    st.markdown(
        """
        - Transaction success, failure and pending analysis
        - Daily transaction trends
        - Bank-wise transaction performance
        - Payment application performance
        - Failure reason analysis
        - Time-based transaction patterns
        """
    )

with analytics_right:
    st.subheader("Mutual Funds Analytics")
    st.markdown(
        """
        - Investor segment analysis
        - Scheme and fund category performance
        - SIP and lump-sum investment analysis
        - Purchase and redemption flows
        - Monthly investment trends
        - Investor and scheme-level insights
        """
    )


# ---------------------------------------------------------
# DATA ENGINEERING CAPABILITIES
# ---------------------------------------------------------

st.divider()
st.header("Data Engineering Capabilities Demonstrated")

capability_cols = st.columns(2)

with capability_cols[0]:
    capabilities = [
        ("Data Generation & Ingestion", "Creating synthetic datasets and loading source data."),
        ("Data Quality Engineering", "Validating records, identifying issues and reconciling outputs."),
        ("Data Transformation", "Cleaning, standardizing and preparing analytical datasets."),
        ("Data Modelling", "Designing structured tables and analytical data marts."),
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
        ("SQL Analytics", "Building analytical queries and reusable data marts."),
        ("Python Analytics", "Using Python and Pandas to derive business insights."),
        ("Pipeline Orchestration", "Executing pipeline stages and recording run details."),
        ("Business Intelligence", "Presenting analytical results through interactive dashboards."),
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


# ---------------------------------------------------------
# TECHNOLOGY STACK
# ---------------------------------------------------------

st.divider()
st.header("Technology Stack")

technology = [
    ("Programming", "Python"),
    ("Data Processing", "Pandas"),
    ("Database", "SQLite"),
    ("Query Language", "SQL"),
    ("Visualization", "Streamlit · Plotly"),
    ("Testing", "Pytest"),
    ("Version Control", "Git · GitHub"),
]

tech_cols = st.columns(4)

for index, (area, tools) in enumerate(technology):
    with tech_cols[index % 4]:
        st.markdown(f"**{area}**")
        st.caption(tools)


# ---------------------------------------------------------
# NAVIGATION AND DISCLAIMER
# ---------------------------------------------------------

st.divider()
st.header("Explore the Implemented Platforms")
st.markdown(
    """
    The UPI Payments and Mutual Funds dashboards are available in the
    **Business Platforms** section of the sidebar. Select a platform to
    explore its data, analytics and interactive visualizations.
    """
)

st.info(
    "Development roadmap: Digital Gold and Cash Loans will be added as "
    "separate modules and integrated into the unified analytical platform."
)

st.caption(
    "Disclaimer: FINTECH 360° uses synthetic data for educational and "
    "portfolio demonstration purposes. It does not contain real customer "
    "or financial transaction records."
)

st.caption(
    "FINTECH 360° · End-to-End Financial Data Engineering, Analytics & BI"
)
