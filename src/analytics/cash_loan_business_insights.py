
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
    / "business_insights"
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
# 3. EXPORT DATASET
# --------------------------------------------------

def export_dataset(conn, query, filename):

    df = pd.read_sql_query(query, conn)

    output_path = OUTPUT_DIR / filename

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"Created: {filename} | Records: {len(df):,}"
    )

    return df


# --------------------------------------------------
# 4. TOP CUSTOMER INSIGHTS
# --------------------------------------------------

def generate_top_customers(conn):

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

            total_requested_amount,
            total_approved_amount,

            total_disbursement_attempts,
            successful_disbursements,
            failed_disbursements,
            pending_disbursements,

            total_disbursed_amount,

            total_installments,
            paid_installments,
            overdue_installments,

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
                100.0 * total_amount_collected
                / NULLIF(total_repayment_due, 0),
                2
            ) AS repayment_collection_rate_percentage

        FROM mart_cl_customer_performance

        ORDER BY
            total_disbursed_amount DESC,
            customer_id

        LIMIT 20
    """

    return export_dataset(
        conn,
        query,
        "cl_top_customers.csv"
    )


# --------------------------------------------------
# 5. CUSTOMER SEGMENT INSIGHTS
# --------------------------------------------------

def generate_segment_insights(conn):

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

            SUM(successful_disbursements)
                AS successful_disbursements,

            ROUND(
                SUM(total_disbursed_amount), 2
            ) AS total_disbursed_amount,

            SUM(total_installments)
                AS total_installments,

            SUM(paid_installments)
                AS paid_installments,

            SUM(overdue_installments)
                AS overdue_installments,

            ROUND(
                SUM(total_repayment_due), 2
            ) AS total_repayment_due,

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
                100.0 * SUM(approved_applications)
                / NULLIF(SUM(total_applications), 0),
                2
            ) AS approval_rate_percentage,

            ROUND(
                100.0 * SUM(total_amount_collected)
                / NULLIF(SUM(total_repayment_due), 0),
                2
            ) AS repayment_collection_rate_percentage

        FROM mart_cl_customer_performance

        GROUP BY customer_segment

        ORDER BY total_disbursed_amount DESC
    """

    return export_dataset(
        conn,
        query,
        "cl_customer_segment_insights.csv"
    )


# --------------------------------------------------
# 6. LOAN PRODUCT INSIGHTS
# --------------------------------------------------

def generate_product_insights(conn):

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
            overdue_outstanding_amount,

            ROUND(
                100.0 * total_amount_collected
                / NULLIF(total_repayment_due, 0),
                2
            ) AS repayment_collection_rate_percentage

        FROM mart_cl_product_performance

        ORDER BY
            total_disbursed_amount DESC,
            product_id
    """

    return export_dataset(
        conn,
        query,
        "cl_loan_product_insights.csv"
    )


# --------------------------------------------------
# 7. EMPLOYMENT TYPE INSIGHTS
# --------------------------------------------------

def generate_employment_insights(conn):

    query = """
        WITH application_metrics AS (

            SELECT
                employment_type,

                COUNT(*) AS total_applications,

                SUM(
                    CASE
                        WHEN application_status = 'APPROVED'
                        THEN 1 ELSE 0
                    END
                ) AS approved_applications,

                SUM(
                    CASE
                        WHEN application_status = 'REJECTED'
                        THEN 1 ELSE 0
                    END
                ) AS rejected_applications,

                SUM(
                    CASE
                        WHEN application_status = 'CANCELLED'
                        THEN 1 ELSE 0
                    END
                ) AS cancelled_applications,

                ROUND(
                    SUM(requested_amount), 2
                ) AS total_requested_amount,

                ROUND(
                    SUM(COALESCE(approved_amount, 0)), 2
                ) AS total_approved_amount

            FROM cl_loan_applications

            GROUP BY employment_type
        ),

        disbursement_metrics AS (

            SELECT
                a.employment_type,

                COUNT(d.disbursement_id)
                    AS total_disbursement_attempts,

                SUM(
                    CASE
                        WHEN d.disbursement_status = 'SUCCESS'
                        THEN 1 ELSE 0
                    END
                ) AS successful_disbursements,

                SUM(
                    CASE
                        WHEN d.disbursement_status = 'FAILED'
                        THEN 1 ELSE 0
                    END
                ) AS failed_disbursements,

                SUM(
                    CASE
                        WHEN d.disbursement_status = 'PENDING'
                        THEN 1 ELSE 0
                    END
                ) AS pending_disbursements,

                ROUND(
                    SUM(
                        CASE
                            WHEN d.disbursement_status = 'SUCCESS'
                            THEN d.disbursed_amount
                            ELSE 0
                        END
                    ), 2
                ) AS total_disbursed_amount

            FROM cl_loan_applications a

            INNER JOIN cl_loan_disbursements d
                ON a.application_id = d.application_id

            GROUP BY a.employment_type
        )

        SELECT
            a.employment_type,

            a.total_applications,
            a.approved_applications,
            a.rejected_applications,
            a.cancelled_applications,

            a.total_requested_amount,
            a.total_approved_amount,

            ROUND(
                100.0 * a.approved_applications
                / NULLIF(a.total_applications, 0),
                2
            ) AS approval_rate_percentage,

            COALESCE(
                d.total_disbursement_attempts, 0
            ) AS total_disbursement_attempts,

            COALESCE(
                d.successful_disbursements, 0
            ) AS successful_disbursements,

            COALESCE(
                d.failed_disbursements, 0
            ) AS failed_disbursements,

            COALESCE(
                d.pending_disbursements, 0
            ) AS pending_disbursements,

            COALESCE(
                d.total_disbursed_amount, 0
            ) AS total_disbursed_amount,

            ROUND(
                100.0 * COALESCE(
                    d.successful_disbursements, 0
                )
                / NULLIF(
                    d.total_disbursement_attempts, 0
                ),
                2
            ) AS disbursement_success_rate_percentage

        FROM application_metrics a

        LEFT JOIN disbursement_metrics d
            ON a.employment_type = d.employment_type

        ORDER BY
            total_disbursed_amount DESC,
            a.employment_type
    """

    return export_dataset(
        conn,
        query,
        "cl_employment_type_insights.csv"
    )


# --------------------------------------------------
# 8. REPAYMENT RISK INSIGHTS
# --------------------------------------------------

def generate_repayment_risk_insights(conn):

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
                100.0 * overdue_installments
                / NULLIF(total_installments, 0),
                2
            ) AS overdue_installment_rate_percentage

        FROM mart_cl_repayment_performance

        WHERE overdue_installments > 0
           OR overdue_outstanding_amount > 0

        ORDER BY
            overdue_outstanding_amount DESC,
            due_date
    """

    return export_dataset(
        conn,
        query,
        "cl_repayment_risk_insights.csv"
    )


# --------------------------------------------------
# 9. MONTHLY LOAN FLOW INSIGHTS
# --------------------------------------------------

def generate_monthly_flow_insights(conn):

    query = """
        WITH application_metrics AS (

            SELECT
                SUBSTR(application_date, 1, 7)
                    AS activity_month,

                COUNT(*) AS total_applications,

                SUM(
                    CASE
                        WHEN application_status = 'APPROVED'
                        THEN 1 ELSE 0
                    END
                ) AS approved_applications,

                SUM(
                    CASE
                        WHEN application_status = 'REJECTED'
                        THEN 1 ELSE 0
                    END
                ) AS rejected_applications,

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

                SUM(
                    CASE
                        WHEN disbursement_status = 'SUCCESS'
                        THEN 1 ELSE 0
                    END
                ) AS successful_disbursements,

                ROUND(
                    SUM(
                        CASE
                            WHEN disbursement_status = 'SUCCESS'
                            THEN disbursed_amount
                            ELSE 0
                        END
                    ), 2
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
                    SUM(
                        CASE
                            WHEN repayment_status = 'OVERDUE'
                            THEN total_due_amount - amount_paid
                            ELSE 0
                        END
                    ), 2
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
    """

    return export_dataset(
        conn,
        query,
        "cl_monthly_loan_flows.csv"
    )


# --------------------------------------------------
# 10. PRINT DATA-DRIVEN BUSINESS FINDINGS
# --------------------------------------------------

def print_business_findings(
    customers,
    segments,
    products,
    employment,
    repayment_risk,
    monthly
):

    print("\n" + "=" * 65)
    print("CASH LOANS BUSINESS FINDINGS")
    print("=" * 65)

    if not customers.empty:

        top_customer = customers.iloc[0]

        print("\n1. TOP CUSTOMER BY SUCCESSFUL DISBURSEMENT")

        print(
            f"Customer: {top_customer['customer_name']}"
        )

        print(
            f"Segment: {top_customer['customer_segment']}"
        )

        print(
            f"Total disbursed amount: "
            f"Rs. {top_customer['total_disbursed_amount']:,.2f}"
        )

    if not segments.empty:

        top_segment = segments.iloc[0]

        print("\n2. LEADING CUSTOMER SEGMENT")

        print(
            f"Segment: {top_segment['customer_segment']}"
        )

        print(
            f"Total customers: "
            f"{top_segment['total_customers']:,}"
        )

        print(
            f"Total disbursed amount: "
            f"Rs. {top_segment['total_disbursed_amount']:,.2f}"
        )

    if not products.empty:

        top_product = products.iloc[0]

        print("\n3. LEADING LOAN PRODUCT")

        print(
            f"Product: {top_product['product_name']}"
        )

        print(
            f"Loan type: {top_product['loan_type']}"
        )

        print(
            f"Successful disbursed amount: "
            f"Rs. {top_product['total_disbursed_amount']:,.2f}"
        )

        print(
            f"Approval rate: "
            f"{top_product['approval_rate_percentage']:.2f}%"
        )

    if not employment.empty:

        top_employment = employment.iloc[0]

        print("\n4. LEADING EMPLOYMENT TYPE BY DISBURSED AMOUNT")

        print(
            f"Employment type: "
            f"{top_employment['employment_type']}"
        )

        print(
            f"Disbursed amount: "
            f"Rs. {top_employment['total_disbursed_amount']:,.2f}"
        )

        print(
            f"Approval rate: "
            f"{top_employment['approval_rate_percentage']:.2f}%"
        )

    if not repayment_risk.empty:

        highest_risk = repayment_risk.iloc[0]

        print("\n5. HIGHEST OVERDUE OUTSTANDING DATE")

        print(
            f"Due date: {highest_risk['due_date']}"
        )

        print(
            f"Overdue outstanding amount: "
            f"Rs. {highest_risk['overdue_outstanding_amount']:,.2f}"
        )

        print(
            f"Overdue installments: "
            f"{highest_risk['overdue_installments']:,}"
        )

    if not monthly.empty:

        peak_month = monthly.loc[
            monthly["total_disbursed_amount"].idxmax()
        ]

        print("\n6. HIGHEST MONTHLY DISBURSEMENT ACTIVITY")

        print(
            f"Month: {peak_month['activity_month']}"
        )

        print(
            f"Successful disbursed amount: "
            f"Rs. {peak_month['total_disbursed_amount']:,.2f}"
        )

    print("\n" + "=" * 65)

    print(
        "Note: These findings describe synthetic loan activity."
    )

    print(
        "Disbursed amounts include successful disbursements only."
    )

    print(
        "Overdue outstanding amounts represent unpaid amounts "
        "on installments classified as OVERDUE."
    )

    print(
        "These metrics do not represent actual lender profitability "
        "or a complete credit-risk assessment."
    )

    print("=" * 65)


# --------------------------------------------------
# 11. RUN BUSINESS INSIGHTS
# --------------------------------------------------

def run_business_insights():

    print("=" * 65)
    print("FINTECH 360 - CASH LOANS BUSINESS INSIGHTS")
    print("=" * 65)

    try:

        with get_connection() as conn:

            customers = generate_top_customers(conn)

            segments = generate_segment_insights(conn)

            products = generate_product_insights(conn)

            employment = generate_employment_insights(conn)

            repayment_risk = generate_repayment_risk_insights(conn)

            monthly = generate_monthly_flow_insights(conn)

        print_business_findings(
            customers,
            segments,
            products,
            employment,
            repayment_risk,
            monthly
        )

        print("\nBUSINESS INSIGHTS SUMMARY")
        print("-" * 65)

        print("Datasets generated: 6")

        print(f"Output directory: {OUTPUT_DIR}")

        print("CASH LOANS BUSINESS INSIGHTS COMPLETED!")

    except Exception as error:

        print("\nBUSINESS INSIGHTS GENERATION FAILED!")

        print(f"Error: {error}")

        raise


# --------------------------------------------------
# 12. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_business_insights()
