
import sqlite3
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = (
    BASE_DIR
    / "data"
    / "warehouse"
    / "database"
    / "fintech360.db"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "warehouse"
    / "cash_loans"
)


# --------------------------------------------------
# 2. VALIDATION FRAMEWORK
# --------------------------------------------------

total_checks = 0
passed_checks = 0
failed_checks = 0


def record_check(condition, description):

    global total_checks, passed_checks, failed_checks

    total_checks += 1

    if condition:
        passed_checks += 1
        status = "PASSED"
    else:
        failed_checks += 1
        status = "FAILED"

    print(f"{description}: {status}")


def values_match(actual, expected, tolerance=0.01):

    if pd.isna(actual) or pd.isna(expected):
        return False

    return abs(float(actual) - float(expected)) <= tolerance


def load_dataset(filename):

    path = OUTPUT_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Analytics dataset not found: {path}"
        )

    return pd.read_csv(path)


def validate_columns(df, columns, description):

    missing = set(columns) - set(df.columns)

    record_check(
        len(missing) == 0,
        f"{description} | Missing columns: {sorted(missing)}"
    )


def validate_unique(df, column, description):

    duplicates = df[column].duplicated().sum()

    record_check(
        duplicates == 0,
        f"{description} | Duplicates: {duplicates}"
    )


# --------------------------------------------------
# 3. MAIN VALIDATION
# --------------------------------------------------

def run_analytics_quality_checks():

    global total_checks, passed_checks, failed_checks

    total_checks = 0
    passed_checks = 0
    failed_checks = 0

    print("=" * 70)
    print("FINTECH 360 - CASH LOANS ANALYTICS QUALITY VALIDATION")
    print("=" * 70)

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    if not OUTPUT_DIR.exists():
        raise FileNotFoundError(
            f"Analytics directory not found: {OUTPUT_DIR}"
        )

    # --------------------------------------------------
    # 4. LOAD ANALYTICS DATASETS
    # --------------------------------------------------

    datasets = {
        "customer": load_dataset(
            "cl_customer_behavior.csv"
        ),
        "segment": load_dataset(
            "cl_customer_segment_analysis.csv"
        ),
        "product": load_dataset(
            "cl_loan_product_performance.csv"
        ),
        "application": load_dataset(
            "cl_daily_application_trends.csv"
        ),
        "disbursement": load_dataset(
            "cl_daily_disbursement_trends.csv"
        ),
        "repayment": load_dataset(
            "cl_repayment_performance.csv"
        ),
        "employment": load_dataset(
            "cl_employment_type_analysis.csv"
        )
    }

    with sqlite3.connect(DB_PATH) as conn:

        # --------------------------------------------------
        # 5. DATASET RECORD COUNTS
        # --------------------------------------------------

        print("\n1. ANALYTICS DATASET RECORD COUNTS")
        print("-" * 70)

        expected_counts = {
            "customer": conn.execute(
                "SELECT COUNT(*) FROM mart_cl_customer_performance"
            ).fetchone()[0],

            "segment": conn.execute(
                "SELECT COUNT(*) FROM mart_cl_customer_performance "
                "GROUP BY customer_id"
            ).fetchone(),

            "product": conn.execute(
                "SELECT COUNT(*) FROM mart_cl_product_performance"
            ).fetchone()[0],

            "application": conn.execute(
                "SELECT COUNT(*) FROM mart_cl_application_performance"
            ).fetchone()[0],

            "disbursement": conn.execute(
                "SELECT COUNT(*) FROM mart_cl_disbursement_performance"
            ).fetchone()[0],

            "repayment": conn.execute(
                "SELECT COUNT(*) FROM mart_cl_repayment_performance"
            ).fetchone()[0],

            "employment": conn.execute(
                "SELECT COUNT(DISTINCT employment_type) "
                "FROM cl_loan_applications"
            ).fetchone()[0]
        }

        # Segment count is based on actual customer segments.
        expected_counts["segment"] = conn.execute(
            "SELECT COUNT(DISTINCT customer_segment) "
            "FROM cl_customers"
        ).fetchone()[0]

        for name, df in datasets.items():

            record_check(
                len(df) == expected_counts[name],
                (
                    f"{name} dataset record count | "
                    f"Actual: {len(df)}, "
                    f"Expected: {expected_counts[name]}"
                )
            )

        # --------------------------------------------------
        # 6. REQUIRED COLUMNS
        # --------------------------------------------------

        print("\n2. REQUIRED COLUMN VALIDATION")
        print("-" * 70)

        required_columns = {
            "customer": [
                "customer_id",
                "customer_name",
                "customer_segment",
                "total_applications",
                "total_disbursed_amount",
                "total_amount_collected",
                "total_outstanding_amount"
            ],

            "segment": [
                "customer_segment",
                "total_customers",
                "total_applications",
                "approved_applications",
                "total_disbursed_amount"
            ],

            "product": [
                "product_id",
                "product_name",
                "total_applications",
                "approved_applications",
                "approval_rate_percentage",
                "total_disbursed_amount"
            ],

            "application": [
                "application_date",
                "total_applications",
                "approved_applications",
                "rejected_applications",
                "total_requested_amount",
                "approval_rate_percentage"
            ],

            "disbursement": [
                "disbursement_date",
                "total_disbursement_attempts",
                "successful_disbursements",
                "failed_disbursements",
                "pending_disbursements",
                "total_disbursed_amount"
            ],

            "repayment": [
                "due_date",
                "total_installments",
                "total_due_amount",
                "total_amount_collected",
                "total_outstanding_amount",
                "overdue_outstanding_amount"
            ],

            "employment": [
                "employment_type",
                "total_applications",
                "approved_applications",
                "approval_rate_percentage",
                "average_credit_score",
                "average_monthly_income"
            ]
        }

        for name, df in datasets.items():

            validate_columns(
                df,
                required_columns[name],
                f"{name} required columns"
            )

        # --------------------------------------------------
        # 7. DUPLICATE VALIDATION
        # --------------------------------------------------

        print("\n3. DUPLICATE VALIDATION")
        print("-" * 70)

        unique_columns = {
            "customer": "customer_id",
            "segment": "customer_segment",
            "product": "product_id",
            "application": "application_date",
            "repayment": "due_date",
            "employment": "employment_type"
        }

        for name, column in unique_columns.items():

            validate_unique(
                datasets[name],
                column,
                f"{name} uniqueness"
            )

        # --------------------------------------------------
        # 8. REQUIRED VALUE VALIDATION
        # --------------------------------------------------

        print("\n4. REQUIRED VALUE VALIDATION")
        print("-" * 70)

        required_values = {
            "customer": [
                "customer_id",
                "customer_name",
                "customer_segment"
            ],
            "segment": [
                "customer_segment",
                "total_customers"
            ],
            "product": [
                "product_id",
                "product_name",
                "loan_type"
            ],
            "application": [
                "application_date",
                "total_applications"
            ],
            "disbursement": [
                "total_disbursement_attempts"
            ],
            "repayment": [
                "due_date",
                "total_installments"
            ],
            "employment": [
                "employment_type",
                "total_applications"
            ]
        }

        for name, columns in required_values.items():

            missing = int(
                datasets[name][columns].isna().sum().sum()
            )

            record_check(
                missing == 0,
                f"{name} required values | Missing: {missing}"
            )

        # --------------------------------------------------
        # 9. SOURCE FINANCIAL TOTALS
        # --------------------------------------------------

        application_source = conn.execute("""
            SELECT
                COUNT(*),
                SUM(CASE WHEN application_status = 'APPROVED'
                    THEN 1 ELSE 0 END),
                SUM(CASE WHEN application_status = 'REJECTED'
                    THEN 1 ELSE 0 END),
                SUM(CASE WHEN application_status = 'CANCELLED'
                    THEN 1 ELSE 0 END),
                SUM(requested_amount),
                SUM(COALESCE(approved_amount, 0))
            FROM cl_loan_applications
        """).fetchone()

        disbursement_source = conn.execute("""
            SELECT
                COUNT(*),
                SUM(CASE WHEN disbursement_status = 'SUCCESS'
                    THEN 1 ELSE 0 END),
                SUM(CASE WHEN disbursement_status = 'FAILED'
                    THEN 1 ELSE 0 END),
                SUM(CASE WHEN disbursement_status = 'PENDING'
                    THEN 1 ELSE 0 END),
                SUM(CASE WHEN disbursement_status = 'SUCCESS'
                    THEN disbursed_amount ELSE 0 END)
            FROM cl_loan_disbursements
        """).fetchone()

        repayment_source = conn.execute("""
            SELECT
                COUNT(*),
                SUM(total_due_amount),
                SUM(amount_paid),
                SUM(total_due_amount - amount_paid),
                SUM(CASE WHEN repayment_status = 'OVERDUE'
                    THEN total_due_amount - amount_paid
                    ELSE 0 END)
            FROM cl_loan_repayments
        """).fetchone()

        # --------------------------------------------------
        # 10. CUSTOMER RECONCILIATION
        # --------------------------------------------------

        print("\n5. CUSTOMER ANALYTICS RECONCILIATION")
        print("-" * 70)

        customer = datasets["customer"]

        customer_checks = [
            (
                customer["total_applications"].sum(),
                application_source[0],
                "Customer application count"
            ),
            (
                customer["approved_applications"].sum(),
                application_source[1],
                "Customer approved applications"
            ),
            (
                customer["rejected_applications"].sum(),
                application_source[2],
                "Customer rejected applications"
            ),
            (
                customer["total_requested_amount"].sum(),
                application_source[4],
                "Customer requested amount"
            ),
            (
                customer["total_approved_amount"].sum(),
                application_source[5],
                "Customer approved amount"
            ),
            (
                customer["total_disbursed_amount"].sum(),
                disbursement_source[4],
                "Customer disbursed amount"
            ),
            (
                customer["total_amount_collected"].sum(),
                repayment_source[2],
                "Customer collected amount"
            ),
            (
                customer["total_outstanding_amount"].sum(),
                repayment_source[3],
                "Customer outstanding amount"
            ),
            (
                customer["overdue_outstanding_amount"].sum(),
                repayment_source[4],
                "Customer overdue amount"
            )
        ]

        for actual, expected, label in customer_checks:

            record_check(
                values_match(actual, expected),
                label + " reconciliation"
            )

        # --------------------------------------------------
        # 11. SEGMENT RECONCILIATION
        # --------------------------------------------------

        print("\n6. CUSTOMER SEGMENT RECONCILIATION")
        print("-" * 70)

        segment = datasets["segment"]

        segment_checks = [
            (
                segment["total_customers"].sum(),
                conn.execute(
                    "SELECT COUNT(*) FROM cl_customers"
                ).fetchone()[0],
                "Segment customer count"
            ),
            (
                segment["total_applications"].sum(),
                application_source[0],
                "Segment application count"
            ),
            (
                segment["approved_applications"].sum(),
                application_source[1],
                "Segment approved applications"
            ),
            (
                segment["total_requested_amount"].sum(),
                application_source[4],
                "Segment requested amount"
            ),
            (
                segment["total_disbursed_amount"].sum(),
                disbursement_source[4],
                "Segment disbursed amount"
            ),
            (
                segment["total_amount_collected"].sum(),
                repayment_source[2],
                "Segment collected amount"
            )
        ]

        for actual, expected, label in segment_checks:

            record_check(
                values_match(actual, expected),
                label + " reconciliation"
            )

        # --------------------------------------------------
        # 12. PRODUCT RECONCILIATION
        # --------------------------------------------------

        print("\n7. PRODUCT PERFORMANCE RECONCILIATION")
        print("-" * 70)

        product = datasets["product"]

        product_checks = [
            (
                product["total_applications"].sum(),
                application_source[0],
                "Product application count"
            ),
            (
                product["approved_applications"].sum(),
                application_source[1],
                "Product approved applications"
            ),
            (
                product["total_requested_amount"].sum(),
                application_source[4],
                "Product requested amount"
            ),
            (
                product["total_disbursed_amount"].sum(),
                disbursement_source[4],
                "Product disbursed amount"
            )
        ]

        for actual, expected, label in product_checks:

            record_check(
                values_match(actual, expected),
                label + " reconciliation"
            )

        # --------------------------------------------------
        # 13. DAILY APPLICATION RECONCILIATION
        # --------------------------------------------------

        print("\n8. DAILY APPLICATION RECONCILIATION")
        print("-" * 70)

        application = datasets["application"]

        application_checks = [
            (
                application["total_applications"].sum(),
                application_source[0],
                "Daily application count"
            ),
            (
                application["approved_applications"].sum(),
                application_source[1],
                "Daily approved applications"
            ),
            (
                application["rejected_applications"].sum(),
                application_source[2],
                "Daily rejected applications"
            ),
            (
                application["cancelled_applications"].sum(),
                application_source[3],
                "Daily cancelled applications"
            ),
            (
                application["total_requested_amount"].sum(),
                application_source[4],
                "Daily requested amount"
            ),
            (
                application["total_approved_amount"].sum(),
                application_source[5],
                "Daily approved amount"
            )
        ]

        for actual, expected, label in application_checks:

            record_check(
                values_match(actual, expected),
                label + " reconciliation"
            )

        # --------------------------------------------------
        # 14. DISBURSEMENT RECONCILIATION
        # --------------------------------------------------

        print("\n9. DISBURSEMENT RECONCILIATION")
        print("-" * 70)

        disbursement = datasets["disbursement"]

        disbursement_checks = [
            (
                disbursement["total_disbursement_attempts"].sum(),
                disbursement_source[0],
                "Disbursement attempt count"
            ),
            (
                disbursement["successful_disbursements"].sum(),
                disbursement_source[1],
                "Successful disbursements"
            ),
            (
                disbursement["failed_disbursements"].sum(),
                disbursement_source[2],
                "Failed disbursements"
            ),
            (
                disbursement["pending_disbursements"].sum(),
                disbursement_source[3],
                "Pending disbursements"
            ),
            (
                disbursement["total_disbursed_amount"].sum(),
                disbursement_source[4],
                "Successful disbursed amount"
            )
        ]

        for actual, expected, label in disbursement_checks:

            record_check(
                values_match(actual, expected),
                label + " reconciliation"
            )

        # --------------------------------------------------
        # 15. REPAYMENT RECONCILIATION
        # --------------------------------------------------

        print("\n10. REPAYMENT RECONCILIATION")
        print("-" * 70)

        repayment = datasets["repayment"]

        repayment_checks = [
            (
                repayment["total_installments"].sum(),
                repayment_source[0],
                "Installment count"
            ),
            (
                repayment["total_due_amount"].sum(),
                repayment_source[1],
                "Total repayment due"
            ),
            (
                repayment["total_amount_collected"].sum(),
                repayment_source[2],
                "Total amount collected"
            ),
            (
                repayment["total_outstanding_amount"].sum(),
                repayment_source[3],
                "Total outstanding amount"
            ),
            (
                repayment["overdue_outstanding_amount"].sum(),
                repayment_source[4],
                "Overdue outstanding amount"
            )
        ]

        for actual, expected, label in repayment_checks:

            record_check(
                values_match(actual, expected),
                label + " reconciliation"
            )

        # --------------------------------------------------
        # 16. EMPLOYMENT TYPE RECONCILIATION
        # --------------------------------------------------

        print("\n11. EMPLOYMENT TYPE RECONCILIATION")
        print("-" * 70)

        employment = datasets["employment"]

        employment_checks = [
            (
                employment["total_applications"].sum(),
                application_source[0],
                "Employment application count"
            ),
            (
                employment["approved_applications"].sum(),
                application_source[1],
                "Employment approved applications"
            ),
            (
                employment["rejected_applications"].sum(),
                application_source[2],
                "Employment rejected applications"
            ),
            (
                employment["total_requested_amount"].sum(),
                application_source[4],
                "Employment requested amount"
            ),
            (
                employment["total_disbursed_amount"].sum(),
                disbursement_source[4],
                "Employment disbursed amount"
            )
        ]

        for actual, expected, label in employment_checks:

            record_check(
                values_match(actual, expected),
                label + " reconciliation"
            )

        # --------------------------------------------------
        # 17. PERCENTAGE VALIDATION
        # --------------------------------------------------

        print("\n12. PERCENTAGE VALIDATION")
        print("-" * 70)

        percentage_columns = {
            "customer": [
                "approval_rate_percentage",
                "disbursement_success_rate_percentage",
                "repayment_collection_rate_percentage"
            ],
            "segment": [
                "approval_rate_percentage",
                "repayment_collection_rate_percentage"
            ],
            "product": [
                "approval_rate_percentage"
            ],
            "application": [
                "approval_rate_percentage"
            ],
            "disbursement": [
                "disbursement_success_rate_percentage"
            ],
            "repayment": [
                "paid_installment_rate_percentage",
                "repayment_collection_rate_percentage"
            ],
            "employment": [
                "approval_rate_percentage"
            ]
        }

        for name, columns in percentage_columns.items():

            for column in columns:

                values = datasets[name][column].dropna()

                record_check(
                    values.between(0, 100).all(),
                    f"{name} {column} range"
                )

        # --------------------------------------------------
        # 18. FINANCIAL CONSISTENCY
        # --------------------------------------------------

        print("\n13. FINANCIAL CONSISTENCY")
        print("-" * 70)

        record_check(
            (
                repayment["total_due_amount"]
                - repayment["total_amount_collected"]
                - repayment["total_outstanding_amount"]
            ).abs().le(0.01).all(),
            "Repayment due = collected + outstanding"
        )

        record_check(
            (
                customer["total_repayment_due"]
                - customer["total_amount_collected"]
                - customer["total_outstanding_amount"]
            ).abs().le(0.01).all(),
            "Customer due = collected + outstanding"
        )

        record_check(
            (
                repayment["overdue_outstanding_amount"]
                <= repayment["total_outstanding_amount"] + 0.01
            ).all(),
            "Overdue outstanding <= total outstanding"
        )

        record_check(
            (
                customer["total_disbursed_amount"] >= 0
            ).all(),
            "Customer disbursed amount non-negative"
        )

    # --------------------------------------------------
    # 19. FINAL SUMMARY
    # --------------------------------------------------

    print("\n" + "=" * 70)
    print("CASH LOANS ANALYTICS QUALITY SUMMARY")
    print("=" * 70)

    print(f"Total checks : {total_checks}")
    print(f"Passed       : {passed_checks}")
    print(f"Failed       : {failed_checks}")

    print("=" * 70)

    if failed_checks == 0:

        print(
            "ALL CASH LOANS ANALYTICS QUALITY CHECKS PASSED!"
        )

    else:

        print(
            "SOME CASH LOANS ANALYTICS QUALITY CHECKS FAILED."
        )

        raise AssertionError(
            f"{failed_checks} analytics quality check(s) failed."
        )


# --------------------------------------------------
# 20. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_analytics_quality_checks()
