
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
    / "mutual_funds"
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
# 4. TOP INVESTOR INSIGHTS
# --------------------------------------------------

def generate_top_investors(conn):

    query = """
        SELECT
            investor_id,
            investor_name,
            investor_segment,
            city,
            total_transactions,
            successful_transactions,
            failed_transactions,
            total_purchase_amount,
            total_redemption_amount,
            net_investment_amount,
            success_rate_percentage

        FROM (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    ORDER BY net_investment_amount DESC,
                             investor_id
                ) AS investor_rank

            FROM (
                SELECT
                    *,
                    ROUND(
                        100.0 * successful_transactions
                        / NULLIF(total_transactions, 0),
                        2
                    ) AS success_rate_percentage

                FROM mart_mf_investor_performance
            )
        )

        WHERE investor_rank <= 20

        ORDER BY investor_rank
    """

    return export_dataset(
        conn,
        query,
        "mf_top_investors.csv"
    )


# --------------------------------------------------
# 5. INVESTOR SEGMENT INSIGHTS
# --------------------------------------------------

def generate_segment_insights(conn):

    query = """
        SELECT
            investor_segment,
            COUNT(*) AS total_investors,
            SUM(total_transactions) AS total_transactions,
            SUM(successful_transactions)
                AS successful_transactions,
            SUM(failed_transactions) AS failed_transactions,

            ROUND(
                SUM(total_purchase_amount), 2
            ) AS total_purchase_amount,

            ROUND(
                SUM(total_redemption_amount), 2
            ) AS total_redemption_amount,

            ROUND(
                SUM(net_investment_amount), 2
            ) AS net_investment_amount,

            ROUND(
                100.0 * SUM(successful_transactions)
                / NULLIF(SUM(total_transactions), 0),
                2
            ) AS success_rate_percentage,

            ROUND(
                AVG(net_investment_amount), 2
            ) AS average_net_investment_per_investor

        FROM mart_mf_investor_performance

        GROUP BY investor_segment

        ORDER BY net_investment_amount DESC
    """

    return export_dataset(
        conn,
        query,
        "mf_investor_segment_insights.csv"
    )


# --------------------------------------------------
# 6. SCHEME INSIGHTS
# --------------------------------------------------

def generate_scheme_insights(conn):

    query = """
        SELECT
            scheme_id,
            scheme_name,
            fund_house,
            fund_category,
            risk_level,
            expense_ratio,
            total_transactions,
            successful_transactions,
            failed_transactions,
            total_purchase_amount,
            total_redemption_amount,

            ROUND(
                total_purchase_amount
                - total_redemption_amount,
                2
            ) AS net_investment_amount,

            success_rate_percentage

        FROM mart_mf_scheme_performance

        ORDER BY
            total_purchase_amount DESC,
            scheme_id
    """

    return export_dataset(
        conn,
        query,
        "mf_scheme_insights.csv"
    )


# --------------------------------------------------
# 7. FUND CATEGORY INSIGHTS
# --------------------------------------------------

def generate_category_insights(conn):

    query = """
        SELECT
            fund_category,
            total_transactions,
            successful_transactions,
            failed_transactions,
            total_purchase_amount,
            total_redemption_amount,

            ROUND(
                total_purchase_amount
                - total_redemption_amount,
                2
            ) AS net_investment_amount,

            success_rate_percentage

        FROM mart_mf_category_performance

        ORDER BY net_investment_amount DESC
    """

    return export_dataset(
        conn,
        query,
        "mf_category_insights.csv"
    )


# --------------------------------------------------
# 8. INVESTMENT MODE INSIGHTS
# --------------------------------------------------

def generate_investment_mode_insights(conn):

    query = """
        SELECT
            investment_mode,

            COUNT(*) AS total_transactions,

            SUM(
                CASE
                    WHEN transaction_status = 'SUCCESS'
                    THEN 1 ELSE 0
                END
            ) AS successful_transactions,

            SUM(
                CASE
                    WHEN transaction_status = 'FAILED'
                    THEN 1 ELSE 0
                END
            ) AS failed_transactions,

            ROUND(
                SUM(
                    CASE
                        WHEN transaction_status = 'SUCCESS'
                        THEN amount ELSE 0
                    END
                ), 2
            ) AS successful_transaction_amount,

            ROUND(
                AVG(
                    CASE
                        WHEN transaction_status = 'SUCCESS'
                        THEN amount
                    END
                ), 2
            ) AS average_successful_transaction_amount,

            ROUND(
                100.0 * SUM(
                    CASE
                        WHEN transaction_status = 'SUCCESS'
                        THEN 1 ELSE 0
                    END
                ) / COUNT(*),
                2
            ) AS success_rate_percentage

        FROM mf_transactions

        GROUP BY investment_mode

        ORDER BY successful_transaction_amount DESC
    """

    return export_dataset(
        conn,
        query,
        "mf_investment_mode_insights.csv"
    )


# --------------------------------------------------
# 9. MONTHLY INVESTMENT FLOW INSIGHTS
# --------------------------------------------------

def generate_monthly_flow_insights(conn):

    query = """
        SELECT
            SUBSTR(transaction_date, 1, 7) AS transaction_month,

            COUNT(*) AS total_transactions,

            SUM(
                CASE
                    WHEN transaction_status = 'SUCCESS'
                    THEN 1 ELSE 0
                END
            ) AS successful_transactions,

            SUM(
                CASE
                    WHEN transaction_status = 'FAILED'
                    THEN 1 ELSE 0
                END
            ) AS failed_transactions,

            ROUND(
                SUM(
                    CASE
                        WHEN transaction_type = 'PURCHASE'
                         AND transaction_status = 'SUCCESS'
                        THEN amount ELSE 0
                    END
                ), 2
            ) AS successful_purchase_amount,

            ROUND(
                SUM(
                    CASE
                        WHEN transaction_type = 'REDEMPTION'
                         AND transaction_status = 'SUCCESS'
                        THEN amount ELSE 0
                    END
                ), 2
            ) AS successful_redemption_amount,

            ROUND(
                SUM(
                    CASE
                        WHEN transaction_type = 'PURCHASE'
                         AND transaction_status = 'SUCCESS'
                        THEN amount

                        WHEN transaction_type = 'REDEMPTION'
                         AND transaction_status = 'SUCCESS'
                        THEN -amount

                        ELSE 0
                    END
                ), 2
            ) AS net_successful_transaction_amount

        FROM mf_transactions

        GROUP BY SUBSTR(transaction_date, 1, 7)

        ORDER BY transaction_month
    """

    return export_dataset(
        conn,
        query,
        "mf_monthly_investment_flows.csv"
    )


# --------------------------------------------------
# 10. PRINT DATA-DRIVEN BUSINESS FINDINGS
# --------------------------------------------------

def print_business_findings(
    investors,
    segments,
    schemes,
    categories,
    modes,
    monthly
):

    print("\n" + "=" * 65)
    print("MUTUAL FUNDS BUSINESS FINDINGS")
    print("=" * 65)

    if not investors.empty:

        top_investor = investors.iloc[0]

        print("\n1. TOP INVESTOR")
        print(
            f"Investor: {top_investor['investor_name']}"
        )
        print(
            f"Segment: {top_investor['investor_segment']}"
        )
        print(
            f"Net investment: "
            f"Rs. {top_investor['net_investment_amount']:,.2f}"
        )

    if not segments.empty:

        top_segment = segments.iloc[0]

        print("\n2. LEADING INVESTOR SEGMENT")
        print(
            f"Segment: {top_segment['investor_segment']}"
        )
        print(
            f"Net investment: "
            f"Rs. {top_segment['net_investment_amount']:,.2f}"
        )

    if not schemes.empty:

        top_scheme = schemes.iloc[0]

        print("\n3. HIGHEST PURCHASE ACTIVITY SCHEME")
        print(
            f"Scheme: {top_scheme['scheme_name']}"
        )
        print(
            f"Purchase amount: "
            f"Rs. {top_scheme['total_purchase_amount']:,.2f}"
        )

    if not categories.empty:

        top_category = categories.iloc[0]

        print("\n4. LEADING FUND CATEGORY BY NET INVESTMENT")
        print(
            f"Category: {top_category['fund_category']}"
        )
        print(
            f"Net investment: "
            f"Rs. {top_category['net_investment_amount']:,.2f}"
        )

    if not modes.empty:

        purchase_modes = modes[
            modes["investment_mode"].isin(
                ["SIP", "LUMP_SUM"]
            )
        ]

        if not purchase_modes.empty:

            top_mode = purchase_modes.iloc[0]

            print("\n5. LEADING PURCHASE INVESTMENT MODE")
            print(
                f"Mode: {top_mode['investment_mode']}"
            )
            print(
                f"Successful amount: "
                f"Rs. {top_mode['successful_transaction_amount']:,.2f}"
            )

    if not monthly.empty:

        peak_month = monthly.loc[
            monthly["successful_purchase_amount"].idxmax()
        ]

        print("\n6. HIGHEST MONTHLY PURCHASE ACTIVITY")
        print(
            f"Month: {peak_month['transaction_month']}"
        )
        print(
            f"Successful purchases: "
            f"Rs. {peak_month['successful_purchase_amount']:,.2f}"
        )

    print("\n" + "=" * 65)

    print(
        "Note: These findings describe synthetic transaction activity."
    )
    print(
        "They do not represent investment returns or actual AUM."
    )

    print("=" * 65)


# --------------------------------------------------
# 11. RUN BUSINESS INSIGHTS
# --------------------------------------------------

def run_business_insights():

    print("=" * 65)
    print("FINTECH 360 - MUTUAL FUNDS BUSINESS INSIGHTS")
    print("=" * 65)

    try:

        with get_connection() as conn:

            investors = generate_top_investors(conn)

            segments = generate_segment_insights(conn)

            schemes = generate_scheme_insights(conn)

            categories = generate_category_insights(conn)

            modes = generate_investment_mode_insights(conn)

            monthly = generate_monthly_flow_insights(conn)

        print_business_findings(
            investors,
            segments,
            schemes,
            categories,
            modes,
            monthly
        )

        print("\nBUSINESS INSIGHTS SUMMARY")
        print("-" * 65)
        print("Datasets generated: 6")
        print(f"Output directory: {OUTPUT_DIR}")
        print("MUTUAL FUNDS BUSINESS INSIGHTS COMPLETED!")

    except Exception as error:

        print("\nBUSINESS INSIGHTS GENERATION FAILED!")
        print(f"Error: {error}")

        raise


# --------------------------------------------------
# 12. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_business_insights()
