# FINTECH 360° – UPI Data Quality & Reconciliation

## 1. Overview

Data quality validation ensures that UPI transaction records meet defined business and technical rules before they are used for analytics.

The UPI module implements two levels of validation:

- Python-based source data quality validation.
- SQL and analytical mart reconciliation.

## 2. Python Data Quality Validation

**Script:** `src/quality/upi_quality_checks.py`

The validation process checks the raw UPI transaction dataset against 10 rules.

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

During ingestion, records are validated and separated into two categories:

- Processed records: Records that pass validation.
- Rejected records: Records containing one or more validation errors.

Rejection reasons are stored in the `rejection_reason` column.

**Observed result:**

- Input records: 10,000
- Processed records: 10,000
- Rejected records: 0

## 4. SQL-Based Data Validation

**SQL file:** `sql/transformations/02_validate_upi_data.sql`

**Execution script:** `src/common/run_sql.py`

Six SQL validation queries are executed.

| Query | Validation |
|---|---|
| 1 | Total transaction count |
| 2 | Transaction count by status |
| 3 | Total transaction value |
| 4 | Duplicate transaction ID detection |
| 5 | Missing transaction identifier detection |
| 6 | Transaction success rate calculation |

**Observed results:**

- Total transactions: 10,000
- Successful transactions: 9,399
- Failed transactions: 403
- Pending transactions: 198
- Duplicate transaction IDs: 0
- Missing identifiers: 0
- Success rate: 93.99%

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

## 6. Data Reliability Workflow

The validation process follows this sequence:

1. Validate incoming records during ingestion.
2. Separate valid and rejected records.
3. Run source-level data quality checks.
4. Transform and standardize valid records.
5. Load curated records into SQLite.
6. Execute SQL validation queries.
7. Reconcile analytical marts against source transactions.

## 7. Business Importance

These checks help prevent:

- Duplicate transaction records.
- Invalid transaction amounts.
- Missing transaction identifiers.
- Incorrect transaction status values.
- Incomplete failure information.
- Incorrect analytical aggregations.
- Inconsistent dashboard metrics.

## 8. Project Results

During the recorded successful execution:

- 10,000 source transactions were processed.
- No records were rejected.
- All 10 Python data quality checks passed.
- All 6 SQL validation queries completed.
- All 24 analytical mart reconciliation checks passed.

The module demonstrates source-level validation, transformation checks, SQL validation, and analytical reconciliation using synthetic UPI transaction data.
