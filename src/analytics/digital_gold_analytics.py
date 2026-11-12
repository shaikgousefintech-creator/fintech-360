
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
    / "digital_gold"
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
            total_transactions,
            successful_transactions,
            failed_transactions,
            pending_transactions,
            total_buy_amount,
            total_sell_amount,
            total_gold_bought_grams,
            total_gold_sold_grams,

            ROUND(
                100.0 * successful_transactions
                / NULLIF(total_transactions, 0),
                2
            ) AS success_rate_percentage

        FROM mart_dg_customer_performance
    """

    return export_dataset(
        conn,
        query,
        "dg_customer_behavior.csv",
        ["total_buy_amount"]
    )


# --------------------------------------------------
# 5. CUSTOMER SEGMENT ANALYSIS
# --------------------------------------------------

def generate_customer_segment_analysis(conn):

    query = """
        SELECT
            customer_segment,
            total_customers,
            total_transactions,
            successful_transactions,
            failed_transactions,
            pending_transactions,
            total_buy_amount,
            total_sell_amount,
            success_rate_percentage,

            ROUND(
                total_buy_amount - total_sell_amount,
                2
            ) AS net_purchase_amount,

            ROUND(
                total_buy_amount
                / NULLIF(total_customers, 0),
                2
            ) AS average_buy_amount_per_customer

        FROM mart_dg_customer_segment_performance
    """

    return export_dataset(
        conn,
        query,
        "dg_customer_segment_analysis.csv",
        ["customer_segment"]
    )


# --------------------------------------------------
# 6. DAILY GOLD TRANSACTION TRENDS
# --------------------------------------------------

def generate_daily_trends(conn):

    query = """
        SELECT
            transaction_date,
            total_transactions,
            successful_transactions,
            failed_transactions,
            pending_transactions,
            successful_buy_transactions,
            successful_sell_transactions,
            total_successful_transaction_amount,
            total_buy_amount,
            total_sell_amount,
            success_rate_percentage

        FROM mart_dg_daily_performance
    """

    return export_dataset(
        conn,
        query,
        "dg_daily_trends.csv",
        ["transaction_date"]
    )


# --------------------------------------------------
# 7. INVESTMENT MODE ANALYSIS
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

            SUM(
                CASE
                    WHEN transaction_status = 'PENDING'
                    THEN 1 ELSE 0
                END
            ) AS pending_transactions,

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
                        WHEN transaction_status = 'PENDING'
                        THEN amount ELSE 0
                    END
                ), 2
            ) AS pending_transaction_amount,

            ROUND(
                SUM(
                    CASE
                        WHEN transaction_status = 'SUCCESS'
                        THEN gold_quantity_grams ELSE 0
                    END
                ), 6
            ) AS successful_gold_quantity_grams,

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

        FROM dg_transactions

        GROUP BY investment_mode
    """

    return export_dataset(
        conn,
        query,
        "dg_investment_mode_analysis.csv",
        ["investment_mode"]
    )


# --------------------------------------------------
# 8. BUY VS SELL ANALYSIS
# --------------------------------------------------

def generate_buy_sell_analysis(conn):

    query = """
        SELECT
            transaction_type,
            total_transactions,
            successful_transactions,
            failed_transactions,
            pending_transactions,
            total_successful_amount,
            total_successful_gold_quantity_grams,
            success_rate_percentage

        FROM mart_dg_transaction_type_performance
    """

    return export_dataset(
        conn,
        query,
        "dg_buy_sell_analysis.csv",
        ["transaction_type"]
    )


# --------------------------------------------------
# 9. GOLD PRICE TRENDS
# --------------------------------------------------

def generate_gold_price_trends(conn):

    query = """
        SELECT
            price_date,
            gold_price_per_gram,
            buy_price_per_gram,
            sell_price_per_gram,

            ROUND(
                gold_price_per_gram
                - LAG(gold_price_per_gram) OVER (
                    ORDER BY price_date
                ),
                2
            ) AS daily_price_change,

            ROUND(
                100.0 * (
                    gold_price_per_gram
                    - LAG(gold_price_per_gram) OVER (
                        ORDER BY price_date
                    )
                ) / NULLIF(
                    LAG(gold_price_per_gram) OVER (
                        ORDER BY price_date
                    ), 0
                ),
                2
            ) AS daily_price_change_percentage

        FROM dg_price_history

        ORDER BY price_date
    """

    return export_dataset(
        conn,
        query,
        "dg_gold_price_trends.csv",
        ["price_date"]
    )


# --------------------------------------------------
# 10. CUSTOMER WALLET BALANCE ANALYSIS
# --------------------------------------------------

def generate_wallet_balance_analysis(conn):

    query = """
        WITH latest_wallet_balance AS (

            SELECT
                customer_id,
                balance_after_grams,
                entry_date,

                ROW_NUMBER() OVER (
                    PARTITION BY customer_id
                    ORDER BY entry_date DESC, ledger_id DESC
                ) AS row_num

            FROM dg_wallet_ledger
        )

        SELECT
            c.customer_id,
            c.customer_name,
            c.customer_segment,
            c.city,

            COALESCE(
                w.balance_after_grams,
                0
            ) AS current_gold_balance_grams,

            w.entry_date AS last_ledger_entry_date

        FROM dg_customers c

        LEFT JOIN latest_wallet_balance w
            ON c.customer_id = w.customer_id
            AND w.row_num = 1
    """

    return export_dataset(
        conn,
        query,
        "dg_wallet_balance_analysis.csv",
        ["current_gold_balance_grams"]
    )


# --------------------------------------------------
# 11. RUN ALL ANALYTICS
# --------------------------------------------------

def run_digital_gold_analytics():

    print("=" * 65)
    print("FINTECH 360 - DIGITAL GOLD BUSINESS ANALYTICS")
    print("=" * 65)

    functions = [
        generate_customer_behavior,
        generate_customer_segment_analysis,
        generate_daily_trends,
        generate_investment_mode_analysis,
        generate_buy_sell_analysis,
        generate_gold_price_trends,
        generate_wallet_balance_analysis,
    ]

    try:

        with get_connection() as conn:

            for function in functions:
                function(conn)

        print("\n" + "=" * 65)
        print("DIGITAL GOLD ANALYTICS SUMMARY")
        print("=" * 65)

        print("Datasets generated:", len(functions))
        print("Output directory:", OUTPUT_DIR)
        print("DIGITAL GOLD ANALYTICS COMPLETED SUCCESSFULLY!")
        print("=" * 65)

    except Exception as error:

        print("\nDIGITAL GOLD ANALYTICS FAILED!")
        print(f"Error: {error}")

        raise


# --------------------------------------------------
# 12. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_digital_gold_analytics()
