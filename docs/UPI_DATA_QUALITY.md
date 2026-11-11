# FINTECH 360 - UPI Data Quality & Reconciliation

## 1. Overview

Data quality validation ensures that UPI transaction records meet defined business and technical rules before they are used for analytical processing and reporting.

The UPI module implements multiple levels of validation:

- Ingestion-level record validation.
- Python-based source data quality checks.
- SQL-based warehouse validation.
- Analytical mart reconciliation.
- Automated testing of validation and analytics logic.

These checks help maintain data consistency and improve the reliability of downstream analytics.

## 2. Python Data Quality Validation

**Script:** `src/quality/upi_quality_checks.py`

The validation process checks the UPI transaction dataset against 10 rules.

| No. | Validation Check | Purpose |
|---|---|---|
| 1 | Required columns present | Ensures all mandatory columns exist |
| 2 | Unique transaction IDs | Prevents duplicate transaction identifiers |
| 3 | Valid transaction amounts | Ensures amounts are numeric and positive |
| 4 | Valid timestamps | Checks timestamp values can be parsed |
| 5 | Valid transaction statuses | Allows SUCCESS, FAILED, and PENDING |
| 6 | Failed transactions have reasons | Checks failure reason availability |
| 7 | P2M transactions have merchant names | Ensures merchant details exist for P2M |
| 8 | Valid transaction types | Allows P2P and P2M |
| 9 | No missing transaction identifiers | Checks transaction, payer, and payee IDs |
| 10 | Valid currency | Ensures currency is INR |

**Observed validation result:**

- Total records: 10,000
- Passed checks: 10
- Failed checks: 0

## 3. Ingestion-Level Validation

**Script:** `src/ingestion/upi_ingestion.py`

During ingestion, incoming records are validated and separated into two categories:

- **Processed records:** Records that pass the ingestion validation rules.
- **Rejected records:** Records containing one or more validation errors.

Rejection reasons are stored in the `rejection_reason` column.

**Outputs:**

- `data/processed/upi/upi_transactions_processed.csv`
- `data/rejected/upi/upi_transactions_rejected.csv`

**Observed result:**

| Metric | Result |
|---|---:|
| Input records | 10,000 |
| Processed records | 10,000 |
| Rejected records | 0 |

## 4. SQL-Based Data Validation

**SQL file:** `sql/transformations/02_validate_upi_data.sql`

**Execution script:** `src/common/run_sql.py`

Six SQL validation queries are executed against the SQLite warehouse.

| Query | Validation |
|---|---|
| 1 | Total transaction count |
| 2 | Transaction count by status |
| 3 | Total transaction value |
| 4 | Duplicate transaction ID detection |
| 5 | Missing transaction identifier detection |
| 6 | Transaction success rate calculation |

**Observed results:**

| Metric | Result |
|---|---:|
| Total transactions | 10,000 |
| Successful transactions | 9,399 |
| Failed transactions | 403 |
| Pending transactions | 198 |
| Duplicate transaction IDs | 0 |
| Missing identifiers | 0 |
| Success rate | 93.99% |

## 5. Analytical Mart Reconciliation

**Script:** `src/quality/upi_mart_quality_check.py`

The reconciliation process compares analytical mart results with the underlying transaction data.

Three analytical marts are validated:

1. `mart_upi_daily_performance`
2. `mart_upi_bank_performance`
3. `mart_upi_payment_app_performance`

Each mart is checked for:

- Total transaction count consistency.
- Successful transaction count consistency.
- Failed transaction count consistency.
- Pending transaction count consistency.
- Total transaction value consistency.
- Successful transaction value consistency.
- Expected aggregation groups.
- Correctly calculated success rates.

**Observed reconciliation result:**

| Metric | Result |
|---|---:|
| Total checks | 24 |
| Passed checks | 24 |
| Failed checks | 0 |

## 6. Automated Testing

The project uses Pytest to verify ingestion, data quality, analytics and business insight functionality.

Run the complete test suite:

```powershell
python -m pytest tests/ -v
```

The test suite covers:

- UPI ingestion validation.
- Invalid transaction rejection.
- Duplicate transaction detection.
- Data quality rules.
- UPI analytics calculations.
- Business insights generation.
- Missing and invalid input handling.
- Analytical output generation.

**Latest recorded test result:**

| Metric | Result |
|---|---:|
| Total automated tests | 35 |
| Passed | 35 |
| Failed | 0 |

## 7. Data Reliability Workflow

The validation process follows this sequence:

1. Validate incoming records during ingestion.
2. Separate valid and rejected records.
3. Run source-level data quality checks.
4. Transform and standardize valid records.
5. Load curated records into SQLite.
6. Execute SQL validation queries.
7. Reconcile analytical marts against source transactions.
8. Execute automated tests to verify pipeline functionality.

## 8. Business Importance

Data quality and reconciliation help prevent:

- Duplicate transaction records.
- Invalid transaction amounts.
- Missing transaction identifiers.
- Incorrect transaction status values.
- Incomplete failure information.
- Incorrect analytical aggregations.
- Inconsistent dashboard metrics.

These checks improve confidence in the data used by business analysts and decision-makers.

## 9. Project Results

During the recorded successful execution:

- 10,000 source transactions were processed.
- No records were rejected.
- All 10 Python data quality checks passed.
- All 6 SQL validation queries completed.
- All 24 analytical mart reconciliation checks passed.
- All 35 automated tests passed.

These results represent observed execution and test runs using synthetic UPI transaction data. They are not guaranteed results for every future execution.

## 10. Project Data Disclaimer

This module uses synthetic UPI transaction data for learning, engineering practice, analytics and portfolio demonstration.

It does not contain real customer information or actual payment-system transaction records.