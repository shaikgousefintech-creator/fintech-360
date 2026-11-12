# FINTECH 360° - Cash Loans Analytics and Business Insights

## 1. Overview

The Cash Loans analytics layer converts warehouse data into analytical datasets and business insights.

It uses Python and SQL queries to analyze customer behavior, loan applications, disbursements, repayment performance, employment types and repayment risk.

The module has two main components:

1. Cash Loans Analytics.
2. Cash Loans Business Insights.

Both components read data from the centralized SQLite warehouse and export results as CSV datasets.

## 2. Analytics Architecture

```text id="c9w4ns"
                  SQLITE DATA WAREHOUSE
                             |
                             v
                    CASH LOANS TABLES
                             |
                             v
                     PYTHON ANALYTICS
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
          CUSTOMER        LOAN PRODUCT    APPLICATION
          ANALYSIS         ANALYSIS         ANALYSIS
              |              |              |
              v              |              v
          SEGMENT             |         DAILY TRENDS
          ANALYSIS            |              |
              |               |              |
              +---------------+--------------+
                             |
                             v
                    DISBURSEMENT ANALYSIS
                             |
                             v
                    REPAYMENT ANALYSIS
                             |
                             v
                  ANALYTICAL CSV DATASETS
                             |
                             v
                  ANALYTICS QUALITY CHECKS
                             |
                             v
                     BUSINESS INSIGHTS
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
         TOP CUSTOMERS    PRODUCT       EMPLOYMENT
                          INSIGHTS       INSIGHTS
                             |
                             v
                     REPAYMENT RISK
                         INSIGHTS
                             |
                             v
                   MONTHLY LOAN FLOWS
                             |
                             v
                 BUSINESS INSIGHT CSVs
                             |
                             v
              BUSINESS INSIGHTS QUALITY
                             |
                             v
                   STREAMLIT DASHBOARD
```

## 3. Cash Loans Analytics

**Script:** `src/analytics/cash_loan_analytics.py`

The analytics layer generates seven analytical datasets.

### 3.1 Customer Behavior Analysis

Analyzes customer-level loan activity.

Provides information about:

- Customer application activity.
- Loan approval and disbursement activity.
- Successful disbursement amounts.
- Customer-level loan behavior.

### 3.2 Customer Segment Analysis

Analyzes loan activity across customer segments.

Helps compare:

- Customer counts.
- Application activity.
- Successful disbursement amounts.
- Segment-level lending behavior.

### 3.3 Loan Product Performance

Analyzes performance across different loan products.

Provides:

- Loan application activity.
- Approved application counts.
- Disbursement activity.
- Successful disbursement amounts.
- Product-level performance comparisons.

### 3.4 Daily Application Trends

Analyzes loan application activity over time.

Helps monitor daily application volume and application patterns.

### 3.5 Daily Disbursement Trends

Analyzes successful loan disbursement activity over time.

Helps identify changes in disbursement volume and financial amounts.

### 3.6 Repayment Performance

Analyzes repayment installment performance.

Provides information about:

- Paid installments.
- Partial payments.
- Pending installments.
- Overdue installments.
- Failed repayment records.
- Repayment amounts and outstanding values.

### 3.7 Employment Type Analysis

Analyzes loan activity across employment categories.

Helps compare application activity, approval rates and disbursement performance by employment type.

## 4. Business Insights

**Script:** `src/analytics/cash_loan_business_insights.py`

The business-insights layer converts analytical outputs into business-focused findings.

It generates six business insight datasets.

### 4.1 Top Customer Insights

Identifies customers with the highest successful loan disbursement activity based on the implemented business calculations.

### 4.2 Customer Segment Insights

Highlights loan application and disbursement behavior across customer segments.

Helps compare customer groups based on lending activity.

### 4.3 Loan Product Insights

Compares loan products using:

- Application activity.
- Approval performance.
- Successful disbursement amounts.
- Product-level lending patterns.

### 4.4 Employment Type Insights

Analyzes lending behavior across employment types.

Helps identify differences in application activity, approval performance and disbursement amounts.

### 4.5 Repayment Risk Insights

Analyzes repayment risk using installment-level information.

Highlights:

- Overdue installments.
- Overdue amounts.
- Repayment status.
- Outstanding repayment patterns.

These insights help identify repayment issues in the synthetic loan dataset.

### 4.6 Monthly Loan Flow Insights

Analyzes monthly loan application and disbursement activity.

Helps identify changes in lending volume and successful disbursement amounts over time.

## 5. Analytical Output Datasets

The analytics layer produces seven CSV datasets, while the business-insights layer produces six CSV datasets.

**Analytics output directory:**

`data/warehouse/cash_loans/analytics/`

**Business insights output directory:**

`data/warehouse/cash_loans/business_insights/`

The datasets support further analysis, quality validation and dashboard reporting.

## 6. Quality Validation

The analytics and business-insights layers have separate quality validation scripts.

**Analytics quality validation:**

`src/quality/cash_loan_analytics_quality_checks.py`

Recorded result: **82/82 checks passed.**

**Business insights quality validation:**

`src/quality/cash_loan_business_insights_quality_checks.py`

Recorded result: **82/82 checks passed.**

These checks compare analytical outputs with warehouse calculations and validate the consistency of generated datasets.

## 7. Loan and Repayment Financial Interpretation

Cash Loans analytics distinguishes between loan applications, approvals, successful disbursements and repayment collections.

For the current synthetic dataset:

| Metric | Amount |
|---|---:|
| Successful loan disbursements | ₹171.61 Cr |
| Amount collected | ₹51.26 Cr |
| Overdue outstanding | ₹637.04 L |

**Collection Ratio:**

The project's collection ratio is calculated as:

`Collected Amount / Total Due Amount`

The denominator includes future pending installments. Therefore, this ratio should not be interpreted as a mature-loan recovery rate.

**Overdue Outstanding:**

Overdue outstanding represents installments classified as OVERDUE. It should not be interpreted as total portfolio credit risk exposure.

Successful disbursement amounts should not be interpreted as revenue or profitability.

## 8. Dashboard Integration

**Dashboard:** `src/dashboard/cash_loan_dashboard.py`

The Cash Loans dashboard is integrated into the unified FINTECH 360° application.

It presents:

- Customer and loan application KPIs.
- Application status distribution.
- Loan product performance.
- Disbursement analysis.
- Repayment performance.
- Overdue and repayment risk analysis.
- Monthly loan trends.
- Employment type analysis.
- Interactive data exploration.

**Main application:**

`src/dashboard/app.py`

The unified application provides access to Cash Loans alongside UPI Payments, Mutual Funds and Digital Gold.

## 9. Business Value

The Cash Loans analytics layer demonstrates how customer, application, disbursement and repayment data can be converted into useful lending business information.

It supports:

- Understanding customer loan behavior.
- Comparing customer segments.
- Evaluating loan product performance.
- Monitoring application and disbursement trends.
- Analyzing repayment performance.
- Identifying overdue installments.
- Comparing employment types.
- Monitoring monthly lending activity.

These insights demonstrate the practical use of data engineering, SQL analytics and business intelligence in the lending domain.

## 10. Project Data Disclaimer

All Cash Loans data and business findings in this project are synthetic.

The results demonstrate analytical methods and reporting techniques. They do not represent actual lending institution performance, real customer credit histories or real loan portfolio risk.
