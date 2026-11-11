
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
# 4. INVESTOR BEHAVIOR ANALYSIS
# --------------------------------------------------

def generate_investor_behavior(conn):

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

            ROUND(
                100.0 * successful_transactions
                / NULLIF(total_transactions, 0),
                2
            ) AS success_rate_percentage

        FROM mart_mf_investor_performance
    """

    return export_dataset(
        conn,
        query,
        "mf_investor_behavior.csv",
        ["net_investment_amount"]
    )


# --------------------------------------------------
# 5. INVESTOR SEGMENT ANALYSIS
# --------------------------------------------------

def generate_investor_segment_analysis(conn):

    query = """
        SELECT
            investor_segment,

            COUNT(*) AS total_investors,

            SUM(total_transactions) AS total_transactions,

            SUM(successful_transactions)
                AS successful_transactions,

            SUM(failed_transactions)
                AS failed_transactions,

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
    """

    return export_dataset(
        conn,
        query,
        "mf_investor_segment_analysis.csv",
        ["investor_segment"]
    )


# --------------------------------------------------
# 6. SCHEME PERFORMANCE ANALYSIS
# --------------------------------------------------

def generate_scheme_performance(conn):

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
            success_rate_percentage,

            ROUND(
                total_purchase_amount
                - total_redemption_amount,
                2
            ) AS net_investment_amount

        FROM mart_mf_scheme_performance
    """

    return export_dataset(
        conn,
        query,
        "mf_scheme_performance.csv",
        ["net_investment_amount"]
    )


# --------------------------------------------------
# 7. FUND CATEGORY ANALYSIS
# --------------------------------------------------

def generate_category_performance(conn):

    query = """
        SELECT
            fund_category,
            total_transactions,
            successful_transactions,
            failed_transactions,
            total_purchase_amount,
            total_redemption_amount,
            success_rate_percentage,

            ROUND(
                total_purchase_amount
                - total_redemption_amount,
                2
            ) AS net_investment_amount

        FROM mart_mf_category_performance
    """

    return export_dataset(
        conn,
        query,
        "mf_category_performance.csv",
        ["net_investment_amount"]
    )


# --------------------------------------------------
# 8. DAILY INVESTMENT TRENDS
# --------------------------------------------------

def generate_daily_trends(conn):

    query = """
        SELECT
            transaction_date,
            total_transactions,
            successful_transactions,
            failed_transactions,
            successful_purchases,
            successful_redemptions,
            total_successful_transaction_amount,
            total_purchase_amount,
            total_redemption_amount,
            success_rate_percentage

        FROM mart_mf_daily_performance
    """

    return export_dataset(
        conn,
        query,
        "mf_daily_trends.csv",
        ["transaction_date"]
    )


# --------------------------------------------------
# 9. SIP VS LUMP-SUM ANALYSIS
# --------------------------------------------------

def generate_investment_mode_analysis(conn):

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
                SUM(
                    CASE
                        WHEN transaction_status = 'FAILED'
                        THEN amount ELSE 0
                    END
                ), 2
            ) AS failed_transaction_amount,

            ROUND(
                SUM(
                    CASE
                        WHEN transaction_status = 'SUCCESS'
                        THEN units ELSE 0
                    END
                ), 4
            ) AS successful_units,

            ROUND(
                100.0 * SUM(
                    CASE
                        WHEN transaction_status = 'SUCCESS'
                        THEN 1 ELSE 0
                    END
                ) / COUNT(*),
                2
            ) AS success_rate_percentage,

            ROUND(
                AVG(
                    CASE
                        WHEN transaction_status = 'SUCCESS'
                        THEN amount
                    END
                ), 2
            ) AS average_successful_transaction_amount

        FROM mf_transactions

        GROUP BY investment_mode
    """

    return export_dataset(
        conn,
        query,
        "mf_investment_mode_analysis.csv",
        ["investment_mode"]
    )


# --------------------------------------------------
# 10. PURCHASE VS REDEMPTION ANALYSIS
# --------------------------------------------------

def generate_purchase_redemption_analysis(conn):

    query = """
        SELECT
            transaction_type,

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
                SUM(
                    CASE
                        WHEN transaction_status = 'FAILED'
                        THEN amount ELSE 0
                    END
                ), 2
            ) AS failed_transaction_amount,

            ROUND(
                SUM(
                    CASE
                        WHEN transaction_status = 'SUCCESS'
                        THEN units ELSE 0
                    END
                ), 4
            ) AS successful_units,

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

        GROUP BY transaction_type
    """

    return export_dataset(
        conn,
        query,
        "mf_purchase_redemption_analysis.csv",
        ["transaction_type"]
    )


# --------------------------------------------------
# 11. RUN ALL ANALYTICS
# --------------------------------------------------

def run_mutual_fund_analytics():

    print("=" * 65)
    print("FINTECH 360 - MUTUAL FUNDS BUSINESS ANALYTICS")
    print("=" * 65)

    functions = [
        generate_investor_behavior,
        generate_investor_segment_analysis,
        generate_scheme_performance,
        generate_category_performance,
        generate_daily_trends,
        generate_investment_mode_analysis,
        generate_purchase_redemption_analysis,
    ]

    try:

        with get_connection() as conn:

            for function in functions:
                function(conn)

        print("\n" + "=" * 65)
        print("MUTUAL FUNDS ANALYTICS SUMMARY")
        print("=" * 65)

        print("Datasets generated:", len(functions))
        print("Output directory:", OUTPUT_DIR)
        print("MUTUAL FUNDS ANALYTICS COMPLETED SUCCESSFULLY!")
        print("=" * 65)

    except Exception as error:

        print("\nMUTUAL FUNDS ANALYTICS FAILED!")
        print(f"Error: {error}")

        raise


# --------------------------------------------------
# 12. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_mutual_fund_analytics()
