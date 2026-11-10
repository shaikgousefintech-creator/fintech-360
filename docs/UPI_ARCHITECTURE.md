# FINTECH 360° – UPI Module Architecture

## 1. Overview

The UPI module is an end-to-end data engineering pipeline that processes synthetic UPI transaction data and makes it available for analytics and business intelligence.

It demonstrates data ingestion, data quality validation, data transformation, data warehousing, SQL validation, analytical processing, and dashboard development.

## 2. Architecture

```text
Raw UPI Transaction CSV
          |
          v
     Data Ingestion
          |
          v
   Processed CSV Data
          |
          v
  Data Quality Validation
          |
          v
   Data Transformation
          |
          v
    Curated CSV Data
          |
          v
     SQLite Warehouse
          |
          v
     SQL Validation
          |
          v
   Analytical Data Marts
          |
          v
 Business Insights & Analysis
          |
          v
    Streamlit Dashboard
```

## 3. Pipeline Components

### Data Ingestion
- Reads raw UPI transaction data from CSV.
- Validates required fields and transaction records.
- Separates valid and rejected records.
- Generates execution logs.

### Data Quality Validation
- Checks required columns.
- Validates transaction ID uniqueness.
- Checks positive transaction amounts.
- Validates timestamps, statuses, and transaction types.
- Checks failure reasons and merchant names.
- Validates currency and required identifiers.

### Data Transformation
- Standardizes text and categorical values.
- Converts transaction amounts and timestamps.
- Extracts date, year, month, day, hour, and weekday.
- Creates transaction status indicator columns.
- Saves curated transaction data.

### Data Warehouse
- Uses SQLite as the analytical database.
- Loads curated UPI transaction records into `upi_transactions`.
- Verifies database record counts and column compatibility.

### SQL Validation
- Validates transaction counts and transaction values.
- Checks transaction status distribution.
- Identifies duplicate transaction IDs.
- Checks missing identifiers.
- Calculates transaction success rate.

### Analytics and Business Intelligence
- Analyzes bank performance.
- Compares payment application performance.
- Examines transaction failure reasons.
- Identifies hourly and weekday transaction patterns.
- Generates business insights and recommendations.

### Dashboard
- Built using Streamlit, Pandas, and Plotly.
- Displays transaction KPIs and performance charts.
- Supports date, bank, and payment application filters.
- Provides transaction exploration and CSV export.

## 4. Current Pipeline Execution Results

Based on the completed pipeline execution:

| Metric | Result |
|---|---:|
| Input transactions | 10,000 |
| Processed transactions | 10,000 |
| Rejected transactions | 0 |
| Curated transactions | 10,000 |
| SQLite records | 10,000 |
| Data quality checks | 10 passed |
| Mart reconciliation checks | 24 passed |
| SQL validation queries | 6 completed |

## 5. Technology Stack

- Python
- Pandas
- SQLite
- SQL
- Streamlit
- Plotly
- Git and GitHub

## 6. Project Data Disclaimer

This module uses synthetic UPI transaction data for learning, engineering practice, analytics, and portfolio demonstration. It does not contain real customer or payment-system records.
