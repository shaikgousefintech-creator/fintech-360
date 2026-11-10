# FINTECH 360° – UPI Analytics & Business Insights

## 1. Overview

The UPI analytics module analyzes transaction performance across banks, payment applications, failure reasons, hours, and weekdays.

The objective is to convert transaction-level data into business insights that help identify operational issues and performance patterns.

## 2. Analytical Components

The module generates five analytical datasets:

| Dataset | Analysis |
|---|---|
| `upi_bank_failure_analysis.csv` | Failure performance by payer bank |
| `upi_app_failure_analysis.csv` | Failure performance by payment application |
| `upi_failure_reason_analysis.csv` | Transaction failures by failure reason |
| `upi_hourly_analysis.csv` | Transaction performance by hour |
| `upi_weekday_analysis.csv` | Transaction performance by weekday |

## 3. Bank Failure Analysis

**Output:** `upi_bank_failure_analysis.csv`

Measures transaction volume, failed transaction count, failed transaction value, and failure rate for each bank.

Observed findings:

- ICICI had the highest failure rate among the displayed leading banks: 4.53%.
- PNB had the lowest overall bank failure rate: 3.59%.

**Business implication:** Banks with higher failure rates should be investigated for possible processing, availability, or response-time issues.

## 4. Payment Application Failure Analysis

**Output:** `upi_app_failure_analysis.csv`

Compares payment applications using total transactions, failed transactions, failed transaction value, and failure rate.

Observed findings:

- BHIM had the highest failure rate: 4.41%.
- PhonePe had the lowest failure rate: 3.54%.

**Business implication:** Payment application performance should be monitored to identify integration and transaction-processing issues.

## 5. Failure Reason Analysis

**Output:** `upi_failure_reason_analysis.csv`

Identifies the most common reasons for failed transactions.

Observed findings:

- INSUFFICIENT_BALANCE: 106 failures (26.30%).
- TRANSACTION_TIMEOUT: 106 failures (26.30%).
- INVALID_VPA: 99 failures (24.57%).

**Business implication:** Common failure reasons can guide improvements in customer guidance, validation, and transaction processing.

## 6. Hourly Transaction Analysis

**Output:** `upi_hourly_analysis.csv`

Analyzes transaction volume, successful transactions, failed transactions, pending transactions, transaction value, and success/failure rates by hour.

Observed finding:

- 14:00 had the highest hourly failure rate: 6.62%, across 408 transactions.

**Business implication:** Monitoring transaction processing and bank response times during higher-failure periods can help identify operational bottlenecks.

## 7. Weekday Transaction Analysis

**Output:** `upi_weekday_analysis.csv`

Compares transaction performance across weekdays.

Observed finding:

- Sunday had the highest weekday failure rate: 5.15%.

**Business implication:** Monitoring service reliability and failure patterns on Sunday may help identify day-specific operational issues.

## 8. Business Recommendations

| Area | Recommendation |
|---|---|
| Bank performance | Investigate banks with comparatively high failure rates |
| Payment application performance | Review application integration and error-handling mechanisms |
| Failure reasons | Address common causes such as insufficient balance and transaction timeouts |
| Transaction timing | Monitor transaction processing during hours with higher failure rates |
| Weekday performance | Investigate day-specific failure patterns |

These recommendations are based on observed transaction patterns and should be treated as investigation priorities, not proof of root causes.

## 9. Key Analytical Metrics

The analysis uses the following measures:

- **Total Transactions:** Number of transaction records.
- **Failed Transactions:** Number of transactions with FAILED status.
- **Failed Transaction Value:** Sum of amounts for failed transactions.
- **Failure Rate:** Failed transactions divided by total transactions, multiplied by 100.
- **Success Rate:** Successful transactions divided by total transactions, multiplied by 100.
- **Transaction Value:** Sum of transaction amounts.

## 10. Business Value

This module demonstrates how transaction data can support:

- Bank performance monitoring.
- Payment application comparisons.
- Failure trend identification.
- Time-based operational analysis.
- Data-driven business recommendations.

All findings are based on the synthetic UPI dataset generated for the FINTECH 360° project.
