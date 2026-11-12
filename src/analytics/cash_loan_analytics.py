
import sqlite3
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

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "warehouse"
    / "cash_loans"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. DATABASE CONNECTION
# --------------------------------------------------

def get_connection():

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    return sqlite3.connect(DB_PATH)


# --------------------------------------------------
# 3. EXPORT ANALYTICAL DATASET
# --------------------------------------------------

def export_dataset(conn, query, output_file, sort_columns=None):

    df = pd.read_sql_query(query, conn)

    if sort_columns:
        df = df.sort_values(
            by=sort_columns
        ).reset_index(drop=True)

    output_path = OUTPUT_DIR / output_file

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"Created: {output_file} | Records: {len(df):,}"
    )

    return df


# --------------------------------------------------
# 4. CUSTOMER BEHAVIOR ANALYSIS
# --------------------------------------------------

def generate_customer_behavior(conn):

    query = """
        SELECT
            customer_id,
            customer_name,
            customer_segment,
            city,
            age,

            total_applications,
            approved_applications,
            rejected_applications,
            cancelled_applications,

            total_requested_amount,
            total_approved_amount,

            total_disbursement_attempts,
            successful_disbursements,
            failed_disbursements,
            pending_disbursements,
            total_disbursed_amount,

            total_installments,
            paid_installments,
            partial_installments,
            pending_installments,
            overdue_installments,
            failed_installments,

            total_repayment_due,
            total_amount_collected,
            total_outstanding_amount,
            overdue_outstanding_amount,

            ROUND(
                100.0 * approved_applications
                / NULLIF(total_applications, 0),
                2
            ) AS approval_rate_percentage,

            ROUND(
                100.0 * successful_disbursements
                / NULLIF(total_disbursement_attempts, 0),
                2
            ) AS disbursement_success_rate_percentage,

            ROUND(
                100.0 * total_amount_collected
                / NULLIF(total_repayment_due, 0),
                2
            ) AS repayment_collection_rate_percentage

        FROM mart_cl_customer_performance
    """

    return export_dataset(
        conn,
        query,
        "cl_customer_behavior.csv",
        ["total_disbursed_amount"]
    )


# --------------------------------------------------
# 5. CUSTOMER SEGMENT ANALYSIS
# --------------------------------------------------

def generate_customer_segment_analysis(conn):

    query = """
        SELECT
            customer_segment,

            COUNT(*) AS total_customers,

            SUM(total_applications)
                AS total_applications,

            SUM(approved_applications)
                AS approved_applications,

            SUM(rejected_applications)
                AS rejected_applications,

            ROUND(
                SUM(total_requested_amount), 2
            ) AS total_requested_amount,

            ROUND(
                SUM(total_approved_amount), 2
            ) AS total_approved_amount,

            ROUND(
                100.0 * SUM(approved_applications)
                / NULLIF(SUM(total_applications), 0),
                2
            ) AS approval_rate_percentage,

            SUM(successful_disbursements)
                AS successful_disbursements,

            ROUND(
                SUM(total_disbursed_amount), 2
            ) AS total_disbursed_amount,

            SUM(total_installments)
                AS total_installments,

            ROUND(
                SUM(total_amount_collected), 2
            ) AS total_amount_collected,

            ROUND(
                SUM(total_outstanding_amount), 2
            ) AS total_outstanding_amount,

            ROUND(
                SUM(overdue_outstanding_amount), 2
            ) AS overdue_outstanding_amount,

            ROUND(
                SUM(total_amount_collected)
                / NULLIF(SUM(total_repayment_due), 0)
                * 100.0,
                2
            ) AS repayment_collection_rate_percentage,

            ROUND(
                SUM(total_disbursed_amount)
                / NULLIF(COUNT(*), 0),
                2
            ) AS average_disbursed_amount_per_customer

        FROM mart_cl_customer_performance

        GROUP BY customer_segment
    """

    return export_dataset(
        conn,
        query,
        "cl_customer_segment_analysis.csv",
        ["customer_segment"]
    )


# --------------------------------------------------
# 6. LOAN PRODUCT PERFORMANCE ANALYSIS
# --------------------------------------------------

def generate_loan_product_performance(conn):

    query = """
        SELECT
            product_id,
            product_name,
            loan_type,
            min_loan_amount,
            max_loan_amount,
            annual_interest_rate,
            min_tenure_months,
            max_tenure_months,
            processing_fee_percentage,

            total_applications,
            approved_applications,
            rejected_applications,
            cancelled_applications,

            total_requested_amount,
            total_approved_amount,
            approval_rate_percentage,

            total_disbursement_attempts,
            successful_disbursements,
            failed_disbursements,
            pending_disbursements,

            total_disbursed_amount,

            total_installments,
            total_repayment_due,
            total_amount_collected,
            total_outstanding_amount,
            overdue_outstanding_amount

        FROM mart_cl_product_performance
    """

    return export_dataset(
        conn,
        query,
        "cl_loan_product_performance.csv",
        ["total_disbursed_amount"]
    )


# --------------------------------------------------
# 7. DAILY APPLICATION TRENDS
# --------------------------------------------------

def generate_daily_application_trends(conn):

    query = """
        SELECT
            application_date,

            total_applications,
            approved_applications,
            rejected_applications,
            draft_applications,
            submitted_applications,
            under_review_applications,
            cancelled_applications,

            total_requested_amount,
            total_approved_amount,

            approval_rate_percentage

        FROM mart_cl_application_performance
    """

    return export_dataset(
        conn,
        query,
        "cl_daily_application_trends.csv",
        ["application_date"]
    )


# --------------------------------------------------
# 8. DAILY DISBURSEMENT TRENDS
# --------------------------------------------------

def generate_daily_disbursement_trends(conn):

    query = """
        SELECT
            disbursement_date,

            total_disbursement_attempts,
            successful_disbursements,
            failed_disbursements,
            pending_disbursements,

            total_disbursed_amount,

            disbursement_success_rate_percentage

        FROM mart_cl_disbursement_performance
    """

    return export_dataset(
        conn,
        query,
        "cl_daily_disbursement_trends.csv",
        ["disbursement_date"]
    )


# --------------------------------------------------
# 9. REPAYMENT PERFORMANCE ANALYSIS
# --------------------------------------------------

def generate_repayment_performance(conn):

    query = """
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
            average_late_days,

            ROUND(
                100.0 * total_amount_collected
                / NULLIF(total_due_amount, 0),
                2
            ) AS repayment_collection_rate_percentage

        FROM mart_cl_repayment_performance
    """

    return export_dataset(
        conn,
        query,
        "cl_repayment_performance.csv",
        ["due_date"]
    )


# --------------------------------------------------
# 10. EMPLOYMENT TYPE ANALYSIS
# --------------------------------------------------

def generate_employment_type_analysis(conn):

    query = """
        WITH application_metrics AS (

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
                ) AS total_approved_amount,

                ROUND(
                    AVG(credit_score), 2
                ) AS average_credit_score,

                ROUND(
                    AVG(monthly_income), 2
                ) AS average_monthly_income

            FROM cl_loan_applications

            GROUP BY employment_type
        ),

        disbursement_metrics AS (

            SELECT
                a.employment_type,

                COUNT(d.disbursement_id)
                    AS total_disbursement_attempts,

                SUM(CASE
                    WHEN d.disbursement_status = 'SUCCESS'
                    THEN 1 ELSE 0
                END) AS successful_disbursements,

                ROUND(
                    SUM(CASE
                        WHEN d.disbursement_status = 'SUCCESS'
                        THEN d.disbursed_amount
                        ELSE 0
                    END),
                    2
                ) AS total_disbursed_amount

            FROM cl_loan_applications a

            INNER JOIN cl_loan_disbursements d
                ON a.application_id = d.application_id

            GROUP BY a.employment_type
        )

        SELECT
            am.employment_type,

            am.total_applications,
            am.approved_applications,
            am.rejected_applications,
            am.cancelled_applications,

            am.total_requested_amount,
            am.total_approved_amount,

            ROUND(
                100.0 * am.approved_applications
                / NULLIF(am.total_applications, 0),
                2
            ) AS approval_rate_percentage,

            am.average_credit_score,
            am.average_monthly_income,

            COALESCE(
                dm.total_disbursement_attempts, 0
            ) AS total_disbursement_attempts,

            COALESCE(
                dm.successful_disbursements, 0
            ) AS successful_disbursements,

            COALESCE(
                dm.total_disbursed_amount, 0
            ) AS total_disbursed_amount

        FROM application_metrics am

        LEFT JOIN disbursement_metrics dm
            ON am.employment_type = dm.employment_type
    """

    return export_dataset(
        conn,
        query,
        "cl_employment_type_analysis.csv",
        ["total_applications"]
    )


# --------------------------------------------------
# 11. RUN ALL ANALYTICS
# --------------------------------------------------

def run_cash_loan_analytics():

    print("=" * 65)
    print("FINTECH 360 - CASH LOANS BUSINESS ANALYTICS")
    print("=" * 65)

    functions = [
        generate_customer_behavior,
        generate_customer_segment_analysis,
        generate_loan_product_performance,
        generate_daily_application_trends,
        generate_daily_disbursement_trends,
        generate_repayment_performance,
        generate_employment_type_analysis,
    ]

    try:

        with get_connection() as conn:

            for function in functions:
                function(conn)

        print("\n" + "=" * 65)
        print("CASH LOANS ANALYTICS SUMMARY")
        print("=" * 65)

        print("Datasets generated:", len(functions))
        print("Output directory:", OUTPUT_DIR)

        print("CASH LOANS ANALYTICS COMPLETED SUCCESSFULLY!")

        print("=" * 65)

    except Exception as error:

        print("\nCASH LOANS ANALYTICS FAILED!")
        print(f"Error: {error}")

        raise


# --------------------------------------------------
# 12. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_cash_loan_analytics()
