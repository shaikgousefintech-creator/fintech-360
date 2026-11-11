
import streamlit as st


st.set_page_config(
    page_title="FINTECH 360° | Data Engineering & Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = {
    "FINTECH 360°": [
        st.Page(
            "executive_overview.py",
            title="Portfolio Overview",
            icon="🏠",
            default=True,
        ),
    ],
    "Business Platforms": [
        st.Page(
            "upi_dashboard.py",
            title="UPI Payments",
            icon="💳",
        ),
        st.Page(
            "mutual_fund_dashboard.py",
            title="Mutual Funds",
            icon="📈",
        ),
    ],
}

navigation = st.navigation(pages, position="sidebar")
navigation.run()
