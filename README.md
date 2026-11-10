# FINTECH 360°

### End-to-End Financial Data Engineering, Analytics & Business Intelligence Platform

FINTECH 360° is an end-to-end data engineering and analytics portfolio project demonstrating how financial transaction data can be ingested, validated, transformed, stored, analyzed, and presented through interactive dashboards.

The platform covers four fintech domains:

- Mutual Funds
- Digital Gold
- UPI Payments
- Cash Loans

The project uses synthetic financial data to demonstrate practical data engineering workflows without exposing real customer information.

---

## Project Objectives

- Build an end-to-end financial data pipeline.
- Implement data ingestion and validation.
- Apply data cleaning and transformation techniques.
- Store structured data in a centralized analytical database.
- Develop SQL-based analytical models and business insights.
- Build interactive dashboards for business users.
- Demonstrate data quality, reconciliation, and pipeline orchestration.

## Technology Stack

| Area | Technologies |
|---|---|
| Programming | Python |
| Data Processing | Pandas |
| Database | SQLite |
| Query Language | SQL |
| Visualization | Streamlit, Plotly |
| Version Control | Git, GitHub |

## Project Architecture

The platform follows this general workflow:

```text
Synthetic Financial Data
          |
          v
     Data Ingestion
          |
          v
   Data Quality Checks
          |
          v
   Data Transformation
          |
          v
   SQLite Data Warehouse
          |
          v
   SQL Analytics & Marts
          |
          v
Business Insights & Dashboards
```
## Documentation

Detailed documentation for the implemented UPI module is available below:

| Document | Description |
|---|---|
| [UPI Architecture](docs/UPI_ARCHITECTURE.md) | UPI pipeline architecture and component overview |
| [UPI Data Quality](docs/UPI_DATA_QUALITY.md) | Data validation rules and quality results |
| [UPI Pipeline Execution](docs/UPI_PIPELINE_EXECUTION.md) | Pipeline stages and execution instructions |
| [UPI Analytics & Business Insights](docs/UPI_ANALYTICS_AND_BUSINESS_INSIGHTS.md) | Business insights, transaction failure analysis, and time-based analysis |

## Project Modules

### 1. UPI Payments

**Status: Core pipeline and analytics implemented**

The UPI module demonstrates an end-to-end financial transaction data pipeline.

**Implemented components:**

- Synthetic UPI transaction data generation.
- CSV-based data ingestion.
- Data validation and rejected-record handling.
- Data standardization and transformation.
- Analytical column creation.
- SQLite data loading.
- SQL-based data validation.
- Analytical data marts.
- Data quality and reconciliation checks.
- Pipeline orchestration.
- Interactive Streamlit dashboard.
- Business insights, transaction failure analysis, and time-based analysis scripts.

**Current dataset:** 10,000 synthetic UPI transactions.

**Validation results:**

- 10,000 records processed.
- 0 rejected records.
- 10 data quality checks passed.
- 24 analytical mart reconciliation checks passed.

### 2. Mutual Funds

**Status: Planned**

Planned scope:

- Investment transaction data.
- Mutual fund scheme performance.
- Investor portfolio analysis.
- SIP and lump-sum investment analytics.

### 3. Digital Gold

**Status: Planned**

Planned scope:

- Digital gold purchase and sell transactions.
- Gold holdings and portfolio valuation.
- Price movement analysis.
- Customer investment behavior.

### 4. Cash Loans

**Status: Planned**

Planned scope:

- Loan application and disbursement data.
- Repayment tracking.
- Outstanding loan analysis.
- Delinquency and repayment performance.

## Repository Structure

```text
fintech-360/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── curated/
│   └── warehouse/
│
├── docs/
├── logs/
├── notebooks/
│
├── sql/
│   ├── ddl/
│   ├── transformations/
│   └── marts/
│
├── src/
│   ├── ingestion/
│   ├── transformation/
│   ├── quality/
│   ├── common/
│   ├── analytics/
│   └── dashboard/
│
├── tests/
├── config/
│
├── README.md
└── .gitignore
```

## Running the UPI Pipeline

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd fintech-360
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install pandas streamlit plotly
```

### 5. Run the UPI pipeline

```bash
python src/common/run_upi_pipeline.py
```

### 6. Launch the UPI dashboard

```bash
python -m streamlit run src/dashboard/upi_dashboard.py
```

## UPI Dashboard

The UPI dashboard provides interactive analysis of:

- Total transactions and transaction value.
- Successful, failed, and pending transactions.
- Transaction success rate.
- Daily transaction trends.
- Bank-wise performance.
- Payment application performance.
- Filtered transaction exploration.
- CSV export of filtered records.

## Data Quality and Reliability

The UPI pipeline includes validation at multiple stages:

- Required field validation.
- Duplicate transaction ID detection.
- Positive transaction amount validation.
- Timestamp validation.
- Transaction status validation.
- Failure reason validation.
- Merchant information validation.
- SQL-based data validation.
- Analytical mart reconciliation.

## Future Enhancements

- Complete Mutual Funds, Digital Gold, and Cash Loans modules.
- Integrate all financial domains into a unified analytical warehouse.
- Add automated testing and stronger pipeline monitoring.
- Expand business intelligence dashboards.
- Improve deployment and documentation.

## Disclaimer

This project uses synthetic data for educational and portfolio demonstration purposes. It does not contain real customer or financial transaction records.

## Author

**FINTECH 360°** — A practical portfolio project demonstrating end-to-end financial data engineering, analytics, and business intelligence.