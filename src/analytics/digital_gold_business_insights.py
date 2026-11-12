
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
            total_transactions,
            successful_transactions,
            failed_transactions,
            pending_transactions,
            total_buy_amount,
            total_sell_amount,
            total_gold_bought_grams,
            total_gold_sold_grams,

            ROUND(
                total_gold_bought_grams
                - total_gold_sold_grams,
                6
            ) AS net_gold_accumulated_grams,

            ROUND(
                100.0 * successful_transactions
                / NULLIF(total_transactions, 0),
                2
            ) AS success_rate_percentage

        FROM (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    ORDER BY
                        total_gold_bought_grams
                        - total_gold_sold_grams DESC,
                        customer_id
                ) AS customer_rank

            FROM mart_dg_customer_performance
        )

        WHERE customer_rank <= 20

        ORDER BY customer_rank
    """

    return export_dataset(
        conn,
        query,
        "dg_top_customers.csv"
    )


# --------------------------------------------------
# 5. CUSTOMER SEGMENT INSIGHTS
# --------------------------------------------------

def generate_segment_insights(conn):

    query = """
        SELECT
            s.customer_segment,
            s.total_customers,
            s.total_transactions,
            s.successful_transactions,
            s.failed_transactions,
            s.pending_transactions,
            s.total_buy_amount,
            s.total_sell_amount,

            ROUND(
                s.total_buy_amount
                - s.total_sell_amount,
                2
            ) AS net_purchase_amount,

            s.success_rate_percentage,

            ROUND(
                SUM(c.total_gold_bought_grams), 6
            ) AS total_gold_bought_grams,

            ROUND(
                SUM(c.total_gold_sold_grams), 6
            ) AS total_gold_sold_grams,

            ROUND(
                SUM(
                    c.total_gold_bought_grams
                    - c.total_gold_sold_grams
                ), 6
            ) AS net_gold_accumulated_grams,

            ROUND(
                SUM(
                    c.total_gold_bought_grams
                    - c.total_gold_sold_grams
                ) / NULLIF(s.total_customers, 0),
                6
            ) AS average_net_gold_per_customer

        FROM mart_dg_customer_segment_performance s

        LEFT JOIN mart_dg_customer_performance c
            ON s.customer_segment = c.customer_segment

        GROUP BY
            s.customer_segment,
            s.total_customers,
            s.total_transactions,
            s.successful_transactions,
            s.failed_transactions,
            s.pending_transactions,
            s.total_buy_amount,
            s.total_sell_amount,
            s.success_rate_percentage

        ORDER BY net_gold_accumulated_grams DESC
    """

    return export_dataset(
        conn,
        query,
        "dg_customer_segment_insights.csv"
    )


# --------------------------------------------------
# 6. CITY-WISE CUSTOMER INSIGHTS
# --------------------------------------------------

def generate_city_insights(conn):

    query = """
        SELECT
            city,

            COUNT(*) AS total_customers,

            SUM(total_transactions) AS total_transactions,

            SUM(successful_transactions)
                AS successful_transactions,

            SUM(failed_transactions)
                AS failed_transactions,

            SUM(pending_transactions)
                AS pending_transactions,

            ROUND(
                SUM(total_buy_amount), 2
            ) AS total_buy_amount,

            ROUND(
                SUM(total_sell_amount), 2
            ) AS total_sell_amount,

            ROUND(
                SUM(total_gold_bought_grams), 6
            ) AS total_gold_bought_grams,

            ROUND(
                SUM(total_gold_sold_grams), 6
            ) AS total_gold_sold_grams,

            ROUND(
                SUM(
                    total_gold_bought_grams
                    - total_gold_sold_grams
                ), 6
            ) AS net_gold_accumulated_grams

        FROM mart_dg_customer_performance

        GROUP BY city

        ORDER BY net_gold_accumulated_grams DESC
    """

    return export_dataset(
        conn,
        query,
        "dg_city_wise_insights.csv"
    )


# --------------------------------------------------
# 7. BUY AND SELL INSIGHTS
# --------------------------------------------------

def generate_transaction_type_insights(conn):

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

        ORDER BY total_successful_amount DESC
    """

    return export_dataset(
        conn,
        query,
        "dg_transaction_type_insights.csv"
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
                        WHEN transaction_status = 'SUCCESS'
                        THEN gold_quantity_grams ELSE 0
                    END
                ), 6
            ) AS successful_gold_quantity_grams,

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

        FROM dg_transactions

        GROUP BY investment_mode

        ORDER BY successful_transaction_amount DESC
    """

    return export_dataset(
        conn,
        query,
        "dg_investment_mode_insights.csv"
    )


# --------------------------------------------------
# 9. MONTHLY GOLD FLOW INSIGHTS
# --------------------------------------------------

def generate_monthly_flow_insights(conn):

    query = """
        SELECT
            SUBSTR(transaction_date, 1, 7)
                AS transaction_month,

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
                        WHEN transaction_type = 'BUY'
                         AND transaction_status = 'SUCCESS'
                        THEN amount ELSE 0
                    END
                ), 2
            ) AS successful_buy_amount,

            ROUND(
                SUM(
                    CASE
                        WHEN transaction_type = 'SELL'
                         AND transaction_status = 'SUCCESS'
                        THEN amount ELSE 0
                    END
                ), 2
            ) AS successful_sell_amount,

            ROUND(
                SUM(
                    CASE
                        WHEN transaction_type = 'BUY'
                         AND transaction_status = 'SUCCESS'
                        THEN amount

                        WHEN transaction_type = 'SELL'
                         AND transaction_status = 'SUCCESS'
                        THEN -amount

                        ELSE 0
                    END
                ), 2
            ) AS net_successful_transaction_amount,

            ROUND(
                SUM(
                    CASE
                        WHEN transaction_type = 'BUY'
                         AND transaction_status = 'SUCCESS'
                        THEN gold_quantity_grams

                        WHEN transaction_type = 'SELL'
                         AND transaction_status = 'SUCCESS'
                        THEN -gold_quantity_grams

                        ELSE 0
                    END
                ), 6
            ) AS net_gold_accumulated_grams

        FROM dg_transactions

        GROUP BY SUBSTR(transaction_date, 1, 7)

        ORDER BY transaction_month
    """

    return export_dataset(
        conn,
        query,
        "dg_monthly_gold_flows.csv"
    )


# --------------------------------------------------
# 10. PRINT DATA-DRIVEN BUSINESS FINDINGS
# --------------------------------------------------

def print_business_findings(
    customers,
    segments,
    cities,
    transaction_types,
    modes,
    monthly
):

    print("\n" + "=" * 65)
    print("DIGITAL GOLD BUSINESS FINDINGS")
    print("=" * 65)

    if not customers.empty:

        top_customer = customers.iloc[0]

        print("\n1. TOP CUSTOMER BY NET GOLD ACCUMULATION")
        print(
            f"Customer: {top_customer['customer_name']}"
        )
        print(
            f"Segment: {top_customer['customer_segment']}"
        )
        print(
            f"Net gold accumulated: "
            f"{top_customer['net_gold_accumulated_grams']:,.6f} grams"
        )

    if not segments.empty:

        top_segment = segments.iloc[0]

        print("\n2. LEADING CUSTOMER SEGMENT")
        print(
            f"Segment: {top_segment['customer_segment']}"
        )
        print(
            f"Net gold accumulated: "
            f"{top_segment['net_gold_accumulated_grams']:,.6f} grams"
        )

    if not cities.empty:

        top_city = cities.iloc[0]

        print("\n3. LEADING CITY BY NET GOLD ACCUMULATION")
        print(
            f"City: {top_city['city']}"
        )
        print(
            f"Net gold accumulated: "
            f"{top_city['net_gold_accumulated_grams']:,.6f} grams"
        )

    if not transaction_types.empty:

        top_type = transaction_types.iloc[0]

        print("\n4. HIGHEST SUCCESSFUL TRANSACTION VALUE")
        print(
            f"Transaction type: {top_type['transaction_type']}"
        )
        print(
            f"Successful amount: "
            f"Rs. {top_type['total_successful_amount']:,.2f}"
        )

    if not modes.empty:

        top_mode = modes.iloc[0]

        print("\n5. LEADING INVESTMENT MODE")
        print(
            f"Mode: {top_mode['investment_mode']}"
        )
        print(
            f"Successful amount: "
            f"Rs. {top_mode['successful_transaction_amount']:,.2f}"
        )

    if not monthly.empty:

        peak_month = monthly.loc[
            monthly["successful_buy_amount"].idxmax()
        ]

        print("\n6. HIGHEST MONTHLY BUY ACTIVITY")
        print(
            f"Month: {peak_month['transaction_month']}"
        )
        print(
            f"Successful BUY amount: "
            f"Rs. {peak_month['successful_buy_amount']:,.2f}"
        )

    print("\n" + "=" * 65)

    print(
        "Note: These findings describe synthetic transaction activity."
    )
    print(
        "Net gold accumulation represents successful BUY quantity "
        "minus successful SELL quantity."
    )
    print(
        "It does not represent investment returns or market valuation."
    )

    print("=" * 65)


# --------------------------------------------------
# 11. RUN BUSINESS INSIGHTS
# --------------------------------------------------

def run_business_insights():

    print("=" * 65)
    print("FINTECH 360 - DIGITAL GOLD BUSINESS INSIGHTS")
    print("=" * 65)

    try:

        with get_connection() as conn:

            customers = generate_top_customers(conn)

            segments = generate_segment_insights(conn)

            cities = generate_city_insights(conn)

            transaction_types = generate_transaction_type_insights(conn)

            modes = generate_investment_mode_insights(conn)

            monthly = generate_monthly_flow_insights(conn)

        print_business_findings(
            customers,
            segments,
            cities,
            transaction_types,
            modes,
            monthly
        )

        print("\nBUSINESS INSIGHTS SUMMARY")
        print("-" * 65)
        print("Datasets generated: 6")
        print(f"Output directory: {OUTPUT_DIR}")
        print("DIGITAL GOLD BUSINESS INSIGHTS COMPLETED!")

    except Exception as error:

        print("\nBUSINESS INSIGHTS GENERATION FAILED!")
        print(f"Error: {error}")

        raise


# --------------------------------------------------
# 12. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_business_insights()
