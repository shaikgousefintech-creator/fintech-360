
import sqlite3
import math
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = (
    BASE_DIR
    / "data"
    / "warehouse"
    / "database"
    / "fintech360.db"
)

INSIGHTS_DIR = (
    BASE_DIR
    / "data"
    / "warehouse"
    / "cash_loans"
    / "business_insights"
)

total_checks = 0
passed_checks = 0
failed_checks = 0


# --------------------------------------------------
# 2. VALIDATION HELPERS
# --------------------------------------------------

def check(condition, description):

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

    return math.isclose(
        float(actual),
        float(expected),
        rel_tol=0,
        abs_tol=tolerance
    )


def load_csv(filename):

    path = INSIGHTS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Insights file not found: {path}"
        )

    return pd.read_csv(path)


def validate_columns(df, columns, description):

    missing = set(columns) - set(df.columns)

    check(
        len(missing) == 0,
        f"{description} | Missing columns: {sorted(missing)}"
    )


def validate_unique(df, column, description):

    duplicates = df[column].duplicated().sum()

    check(
        duplicates == 0,
        f"{description} | Duplicates: {duplicates}"
    )


def validate_numeric_match(
    actual,
    expected,
    description,
    tolerance=0.01
):

    if len(actual) != len(expected):
        check(False, description)
        return

    valid = all(
        values_match(a, e, tolerance)
        for a, e in zip(actual, expected)
    )

    check(valid, description)


# --------------------------------------------------
# 3. MAIN VALIDATION
# --------------------------------------------------

def run_business_insights_quality_checks():

    global total_checks, passed_checks, failed_checks

    total_checks = 0
    passed_checks = 0
    failed_checks = 0

    print("=" * 70)
    print("FINTECH 360 - CASH LOANS BUSINESS INSIGHTS VALIDATION")
    print("=" * 70)

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    if not INSIGHTS_DIR.exists():
        raise FileNotFoundError(
            f"Insights directory not found: {INSIGHTS_DIR}"
        )

    # --------------------------------------------------
    # 4. LOAD BUSINESS INSIGHTS DATASETS
    # --------------------------------------------------

    datasets = {

        "top_customers": load_csv(
            "cl_top_customers.csv"
        ),

        "segments": load_csv(
            "cl_customer_segment_insights.csv"
        ),

        "products": load_csv(
            "cl_loan_product_insights.csv"
        ),

        "employment": load_csv(
            "cl_employment_type_insights.csv"
        ),

        "repayment_risk": load_csv(
            "cl_repayment_risk_insights.csv"
        ),

        "monthly": load_csv(
            "cl_monthly_loan_flows.csv"
        )
    }

    # --------------------------------------------------
    # 5. DATASET RECORD COUNT VALIDATION
    # --------------------------------------------------

    print("\n1. DATASET RECORD COUNT CHECKS")
    print("-" * 70)

    expected_counts = {

        "top_customers": 20,

        "segments": pd.read_sql_query(
            """
            SELECT COUNT(DISTINCT customer_segment)
            FROM cl_customers
            """,
            sqlite3.connect(DB_PATH)
        ).iloc[0, 0],

        "products": pd.read_sql_query(
            """
            SELECT COUNT(*)
            FROM cl_loan_products
            """,
            sqlite3.connect(DB_PATH)
        ).iloc[0, 0],

        "employment": pd.read_sql_query(
            """
            SELECT COUNT(DISTINCT employment_type)
            FROM cl_loan_applications
            """,
            sqlite3.connect(DB_PATH)
        ).iloc[0, 0],

        "repayment_risk": pd.read_sql_query(
            """
            SELECT COUNT(*)
            FROM mart_cl_repayment_performance
            WHERE overdue_installments > 0
               OR overdue_outstanding_amount > 0
            """,
            sqlite3.connect(DB_PATH)
        ).iloc[0, 0],

        "monthly": None
    }

    # Monthly record count is derived from all three date sources.
    with sqlite3.connect(DB_PATH) as conn:

        monthly_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT SUBSTR(application_date, 1, 7) AS month
                FROM cl_loan_applications

                UNION

                SELECT SUBSTR(disbursement_date, 1, 7)
                FROM cl_loan_disbursements
                WHERE disbursement_date IS NOT NULL

                UNION

                SELECT SUBSTR(due_date, 1, 7)
                FROM cl_loan_repayments
            )
            """
        ).fetchone()[0]

        expected_counts["monthly"] = monthly_count

        for name, df in datasets.items():

            actual = len(df)
            expected = expected_counts[name]

            check(
                actual == expected,
                (
                    f"{name} records | "
                    f"Actual: {actual}, Expected: {expected}"
                )
            )

        # --------------------------------------------------
        # 6. REQUIRED COLUMN VALIDATION
        # --------------------------------------------------

        print("\n2. REQUIRED COLUMN VALIDATION")
        print("-" * 70)

        required_columns = {

            "top_customers": [
                "customer_id",
                "customer_name",
                "customer_segment",
                "total_disbursed_amount",
                "total_amount_collected",
                "total_outstanding_amount"
            ],

            "segments": [
                "customer_segment",
                "total_customers",
                "total_applications",
                "approved_applications",
                "total_disbursed_amount",
                "total_amount_collected"
            ],

            "products": [
                "product_id",
                "product_name",
                "loan_type",
                "total_applications",
                "approved_applications",
                "approval_rate_percentage",
                "total_disbursed_amount"
            ],

            "employment": [
                "employment_type",
                "total_applications",
                "approved_applications",
                "total_disbursed_amount",
                "approval_rate_percentage"
            ],

            "repayment_risk": [
                "due_date",
                "total_installments",
                "overdue_installments",
                "total_outstanding_amount",
                "overdue_outstanding_amount"
            ],

            "monthly": [
                "activity_month",
                "total_applications",
                "approved_applications",
                "total_disbursed_amount",
                "total_installments",
                "total_amount_collected",
                "total_outstanding_amount"
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
            "top_customers": "customer_id",
            "segments": "customer_segment",
            "products": "product_id",
            "employment": "employment_type",
            "repayment_risk": "due_date",
            "monthly": "activity_month"
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

            "top_customers": [
                "customer_id",
                "customer_name",
                "customer_segment"
            ],

            "segments": [
                "customer_segment",
                "total_customers"
            ],

            "products": [
                "product_id",
                "product_name",
                "loan_type"
            ],

            "employment": [
                "employment_type",
                "total_applications"
            ],

            "repayment_risk": [
                "due_date",
                "total_installments"
            ],

            "monthly": [
                "activity_month"
            ]
        }

        for name, columns in required_values.items():

            missing = int(
                datasets[name][columns].isna().sum().sum()
            )

            check(
                missing == 0,
                f"{name} required values | Missing: {missing}"
            )

        # --------------------------------------------------
        # 9. TOP CUSTOMER VALIDATION
        # --------------------------------------------------

        print("\n5. TOP CUSTOMER VALIDATION")
        print("-" * 70)

        top = datasets["top_customers"]

        expected_top = pd.read_sql_query(
            """
            SELECT
                customer_id,
                total_disbursed_amount

            FROM mart_cl_customer_performance

            ORDER BY
                total_disbursed_amount DESC,
                customer_id

            LIMIT 20
            """,
            conn
        )

        check(
            top["customer_id"].tolist()
            == expected_top["customer_id"].tolist(),
            "Top 20 customer ranking"
        )

        check(
            values_match(
                top["total_disbursed_amount"].sum(),
                expected_top["total_disbursed_amount"].sum()
            ),
            "Top 20 customer disbursed amount reconciliation"
        )

        # --------------------------------------------------
        # 10. SOURCE TRANSACTION TOTALS
        # --------------------------------------------------

        application_source = conn.execute(
            """
            SELECT
                COUNT(*),

                SUM(CASE
                    WHEN application_status = 'APPROVED'
                    THEN 1 ELSE 0
                END),

                SUM(CASE
                    WHEN application_status = 'REJECTED'
                    THEN 1 ELSE 0
                END),

                SUM(CASE
                    WHEN application_status = 'CANCELLED'
                    THEN 1 ELSE 0
                END),

                SUM(requested_amount),

                SUM(COALESCE(approved_amount, 0))

            FROM cl_loan_applications
            """
        ).fetchone()

        disbursement_source = conn.execute(
            """
            SELECT
                COUNT(*),

                SUM(CASE
                    WHEN disbursement_status = 'SUCCESS'
                    THEN 1 ELSE 0
                END),

                SUM(CASE
                    WHEN disbursement_status = 'FAILED'
                    THEN 1 ELSE 0
                END),

                SUM(CASE
                    WHEN disbursement_status = 'PENDING'
                    THEN 1 ELSE 0
                END),

                SUM(CASE
                    WHEN disbursement_status = 'SUCCESS'
                    THEN disbursed_amount ELSE 0
                END)

            FROM cl_loan_disbursements
            """
        ).fetchone()

        repayment_source = conn.execute(
            """
            SELECT
                COUNT(*),

                SUM(total_due_amount),

                SUM(amount_paid),

                SUM(total_due_amount - amount_paid),

                SUM(CASE
                    WHEN repayment_status = 'OVERDUE'
                    THEN total_due_amount - amount_paid
                    ELSE 0
                END)

            FROM cl_loan_repayments
            """
        ).fetchone()

        # --------------------------------------------------
        # 11. CUSTOMER SEGMENT VALIDATION
        # --------------------------------------------------

        print("\n6. CUSTOMER SEGMENT VALIDATION")
        print("-" * 70)

        segments = datasets["segments"]

        segment_checks = [

            (
                segments["total_customers"].sum(),
                conn.execute(
                    "SELECT COUNT(*) FROM cl_customers"
                ).fetchone()[0],
                "Segment customer count"
            ),

            (
                segments["total_applications"].sum(),
                application_source[0],
                "Segment application count"
            ),

            (
                segments["approved_applications"].sum(),
                application_source[1],
                "Segment approved application count"
            ),

            (
                segments["rejected_applications"].sum(),
                application_source[2],
                "Segment rejected application count"
            ),

            (
                segments["total_requested_amount"].sum(),
                application_source[4],
                "Segment requested amount"
            ),

            (
                segments["total_approved_amount"].sum(),
                application_source[5],
                "Segment approved amount"
            ),

            (
                segments["successful_disbursements"].sum(),
                disbursement_source[1],
                "Segment successful disbursement count"
            ),

            (
                segments["total_disbursed_amount"].sum(),
                disbursement_source[4],
                "Segment disbursed amount"
            ),

            (
                segments["total_amount_collected"].sum(),
                repayment_source[2],
                "Segment collected amount"
            )
        ]

        for actual, expected, description in segment_checks:

            check(
                values_match(actual, expected),
                description
            )

        # --------------------------------------------------
        # 12. LOAN PRODUCT VALIDATION
        # --------------------------------------------------

        print("\n7. LOAN PRODUCT VALIDATION")
        print("-" * 70)

        products = datasets["products"]

        product_checks = [

            (
                products["total_applications"].sum(),
                application_source[0],
                "Product application count"
            ),

            (
                products["approved_applications"].sum(),
                application_source[1],
                "Product approved application count"
            ),

            (
                products["rejected_applications"].sum(),
                application_source[2],
                "Product rejected application count"
            ),

            (
                products["total_requested_amount"].sum(),
                application_source[4],
                "Product requested amount"
            ),

            (
                products["total_approved_amount"].sum(),
                application_source[5],
                "Product approved amount"
            ),

            (
                products["successful_disbursements"].sum(),
                disbursement_source[1],
                "Product successful disbursement count"
            ),

            (
                products["total_disbursed_amount"].sum(),
                disbursement_source[4],
                "Product disbursed amount"
            ),

            (
                products["total_amount_collected"].sum(),
                repayment_source[2],
                "Product collected amount"
            )
        ]

        for actual, expected, description in product_checks:

            check(
                values_match(actual, expected),
                description
            )

        # --------------------------------------------------
        # 13. EMPLOYMENT TYPE VALIDATION
        # --------------------------------------------------

        print("\n8. EMPLOYMENT TYPE VALIDATION")
        print("-" * 70)

        employment = datasets["employment"]

        expected_employment = pd.read_sql_query(
            """
            SELECT
                employment_type,

                COUNT(*) AS total_applications,

                SUM(CASE
                    WHEN application_status = 'APPROVED'
                    THEN 1 ELSE 0
                END) AS approved_applications,

                SUM(CASE
                    WHEN application_status = 'REJECTED'
                    THEN 1 ELSE 0
                END) AS rejected_applications,

                SUM(CASE
                    WHEN application_status = 'CANCELLED'
                    THEN 1 ELSE 0
                END) AS cancelled_applications,

                ROUND(
                    SUM(requested_amount), 2
                ) AS total_requested_amount,

                ROUND(
                    SUM(COALESCE(approved_amount, 0)), 2
                ) AS total_approved_amount

            FROM cl_loan_applications

            GROUP BY employment_type

            ORDER BY employment_type
            """,
            conn
        )

        employment_sorted = employment.sort_values(
            "employment_type"
        ).reset_index(drop=True)

        expected_employment = expected_employment.sort_values(
            "employment_type"
        ).reset_index(drop=True)

        check(
            employment_sorted["employment_type"].tolist()
            == expected_employment["employment_type"].tolist(),
            "Employment type coverage"
        )

        check(
            employment["total_applications"].sum()
            == application_source[0],
            "Employment application count"
        )

        check(
            employment["approved_applications"].sum()
            == application_source[1],
            "Employment approved application count"
        )

        check(
            employment["rejected_applications"].sum()
            == application_source[2],
            "Employment rejected application count"
        )

        check(
            values_match(
                employment["total_requested_amount"].sum(),
                application_source[4]
            ),
            "Employment requested amount"
        )

        check(
            values_match(
                employment["total_approved_amount"].sum(),
                application_source[5]
            ),
            "Employment approved amount"
        )

        check(
            employment["total_disbursement_attempts"].sum()
            == disbursement_source[0],
            "Employment disbursement attempt count"
        )

        check(
            employment["successful_disbursements"].sum()
            == disbursement_source[1],
            "Employment successful disbursement count"
        )

        check(
            employment["failed_disbursements"].sum()
            == disbursement_source[2],
            "Employment failed disbursement count"
        )

        check(
            employment["pending_disbursements"].sum()
            == disbursement_source[3],
            "Employment pending disbursement count"
        )

        check(
            values_match(
                employment["total_disbursed_amount"].sum(),
                disbursement_source[4]
            ),
            "Employment disbursed amount"
        )

        # --------------------------------------------------
        # 14. REPAYMENT RISK VALIDATION
        # --------------------------------------------------

        print("\n9. REPAYMENT RISK VALIDATION")
        print("-" * 70)

        risk = datasets["repayment_risk"]

        expected_risk = pd.read_sql_query(
            """
            SELECT
                due_date,
                total_installments,
                paid_installments,
                partial_installments,
                pending_installments,
                overdue_installments,
                failed_installments,
                total_due_amount,
                total_amount_collected,
                total_outstanding_amount,
                overdue_outstanding_amount,
                paid_installment_rate_percentage,
                average_late_days

            FROM mart_cl_repayment_performance

            WHERE overdue_installments > 0
               OR overdue_outstanding_amount > 0

            ORDER BY
                overdue_outstanding_amount DESC,
                due_date
            """,
            conn
        )

        check(
            risk["due_date"].tolist()
            == expected_risk["due_date"].tolist(),
            "Repayment risk date coverage and ranking"
        )

        risk_columns = [
            "total_installments",
            "paid_installments",
            "partial_installments",
            "pending_installments",
            "overdue_installments",
            "failed_installments",
            "total_due_amount",
            "total_amount_collected",
            "total_outstanding_amount",
            "overdue_outstanding_amount",
            "paid_installment_rate_percentage",
            "average_late_days"
        ]

        for column in risk_columns:

            validate_numeric_match(
                risk[column].tolist(),
                expected_risk[column].tolist(),
                f"Repayment risk {column} reconciliation"
            )

        check(
            risk["overdue_outstanding_amount"].sum()
            <= risk["total_outstanding_amount"].sum() + 0.01,
            "Overdue outstanding does not exceed total outstanding"
        )

        # --------------------------------------------------
        # 15. MONTHLY LOAN FLOW VALIDATION
        # --------------------------------------------------

        print("\n10. MONTHLY LOAN FLOW VALIDATION")
        print("-" * 70)

        monthly = datasets["monthly"]

        expected_monthly = pd.read_sql_query(
            """
            WITH application_metrics AS (

                SELECT
                    SUBSTR(application_date, 1, 7)
                        AS activity_month,

                    COUNT(*) AS total_applications,

                    SUM(CASE
                        WHEN application_status = 'APPROVED'
                        THEN 1 ELSE 0
                    END) AS approved_applications,

                    SUM(CASE
                        WHEN application_status = 'REJECTED'
                        THEN 1 ELSE 0
                    END) AS rejected_applications,

                    ROUND(
                        SUM(requested_amount), 2
                    ) AS total_requested_amount,

                    ROUND(
                        SUM(COALESCE(approved_amount, 0)), 2
                    ) AS total_approved_amount

                FROM cl_loan_applications

                GROUP BY SUBSTR(application_date, 1, 7)
            ),

            disbursement_metrics AS (

                SELECT
                    SUBSTR(disbursement_date, 1, 7)
                        AS activity_month,

                    COUNT(*) AS total_disbursement_attempts,

                    SUM(CASE
                        WHEN disbursement_status = 'SUCCESS'
                        THEN 1 ELSE 0
                    END) AS successful_disbursements,

                    ROUND(
                        SUM(CASE
                            WHEN disbursement_status = 'SUCCESS'
                            THEN disbursed_amount
                            ELSE 0
                        END), 2
                    ) AS total_disbursed_amount

                FROM cl_loan_disbursements

                WHERE disbursement_date IS NOT NULL

                GROUP BY SUBSTR(disbursement_date, 1, 7)
            ),

            repayment_metrics AS (

                SELECT
                    SUBSTR(due_date, 1, 7)
                        AS activity_month,

                    COUNT(*) AS total_installments,

                    ROUND(
                        SUM(total_due_amount), 2
                    ) AS total_repayment_due,

                    ROUND(
                        SUM(amount_paid), 2
                    ) AS total_amount_collected,

                    ROUND(
                        SUM(total_due_amount - amount_paid), 2
                    ) AS total_outstanding_amount,

                    ROUND(
                        SUM(CASE
                            WHEN repayment_status = 'OVERDUE'
                            THEN total_due_amount - amount_paid
                            ELSE 0
                        END), 2
                    ) AS overdue_outstanding_amount

                FROM cl_loan_repayments

                GROUP BY SUBSTR(due_date, 1, 7)
            ),

            all_months AS (

                SELECT activity_month FROM application_metrics

                UNION

                SELECT activity_month FROM disbursement_metrics

                UNION

                SELECT activity_month FROM repayment_metrics
            )

            SELECT
                m.activity_month,

                COALESCE(
                    a.total_applications, 0
                ) AS total_applications,

                COALESCE(
                    a.approved_applications, 0
                ) AS approved_applications,

                COALESCE(
                    a.rejected_applications, 0
                ) AS rejected_applications,

                COALESCE(
                    a.total_requested_amount, 0
                ) AS total_requested_amount,

                COALESCE(
                    a.total_approved_amount, 0
                ) AS total_approved_amount,

                COALESCE(
                    d.total_disbursement_attempts, 0
                ) AS total_disbursement_attempts,

                COALESCE(
                    d.successful_disbursements, 0
                ) AS successful_disbursements,

                COALESCE(
                    d.total_disbursed_amount, 0
                ) AS total_disbursed_amount,

                COALESCE(
                    r.total_installments, 0
                ) AS total_installments,

                COALESCE(
                    r.total_repayment_due, 0
                ) AS total_repayment_due,

                COALESCE(
                    r.total_amount_collected, 0
                ) AS total_amount_collected,

                COALESCE(
                    r.total_outstanding_amount, 0
                ) AS total_outstanding_amount,

                COALESCE(
                    r.overdue_outstanding_amount, 0
                ) AS overdue_outstanding_amount

            FROM all_months m

            LEFT JOIN application_metrics a
                ON m.activity_month = a.activity_month

            LEFT JOIN disbursement_metrics d
                ON m.activity_month = d.activity_month

            LEFT JOIN repayment_metrics r
                ON m.activity_month = r.activity_month

            ORDER BY m.activity_month
            """,
            conn
        )

        monthly = monthly.sort_values(
            "activity_month"
        ).reset_index(drop=True)

        expected_monthly = expected_monthly.sort_values(
            "activity_month"
        ).reset_index(drop=True)

        check(
            monthly["activity_month"].tolist()
            == expected_monthly["activity_month"].tolist(),
            "Monthly date coverage"
        )

        monthly_columns = [
            "total_applications",
            "approved_applications",
            "rejected_applications",
            "total_requested_amount",
            "total_approved_amount",
            "total_disbursement_attempts",
            "successful_disbursements",
            "total_disbursed_amount",
            "total_installments",
            "total_repayment_due",
            "total_amount_collected",
            "total_outstanding_amount",
            "overdue_outstanding_amount"
        ]

        for column in monthly_columns:

            validate_numeric_match(
                monthly[column].tolist(),
                expected_monthly[column].tolist(),
                f"Monthly {column} reconciliation"
            )

        # --------------------------------------------------
        # 16. FINAL SUMMARY
        # --------------------------------------------------

    print("\n" + "=" * 70)
    print("CASH LOANS BUSINESS INSIGHTS QUALITY SUMMARY")
    print("=" * 70)

    print(f"Total checks : {total_checks}")
    print(f"Passed       : {passed_checks}")
    print(f"Failed       : {failed_checks}")

    print("=" * 70)

    if failed_checks == 0:

        print(
            "ALL CASH LOANS BUSINESS INSIGHTS CHECKS PASSED!"
        )

    else:

        print(
            "SOME BUSINESS INSIGHTS CHECKS FAILED."
        )

        raise AssertionError(
            f"{failed_checks} business insights check(s) failed."
        )


# --------------------------------------------------
# 17. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_business_insights_quality_checks()
