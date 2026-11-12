
import sqlite3
from pathlib import Path
import math

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

ANALYTICS_DIR = (
    BASE_DIR
    / "data"
    / "warehouse"
    / "digital_gold"
)


# --------------------------------------------------
# 2. VALIDATION FRAMEWORK
# --------------------------------------------------

total_checks = 0
passed_checks = 0
failed_checks = 0


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

    path = ANALYTICS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Analytics file not found: {path}"
        )

    return pd.read_csv(path)


# --------------------------------------------------
# 3. MAIN VALIDATION
# --------------------------------------------------

def run_analytics_quality_checks():

    global total_checks, passed_checks, failed_checks

    total_checks = 0
    passed_checks = 0
    failed_checks = 0

    print("=" * 65)
    print("FINTECH 360 - DIGITAL GOLD ANALYTICS QUALITY VALIDATION")
    print("=" * 65)

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    if not ANALYTICS_DIR.exists():
        raise FileNotFoundError(
            f"Analytics directory not found: {ANALYTICS_DIR}"
        )

    # Load all seven analytics datasets
    datasets = {
        "customer": load_csv("dg_customer_behavior.csv"),
        "segment": load_csv("dg_customer_segment_analysis.csv"),
        "daily": load_csv("dg_daily_trends.csv"),
        "mode": load_csv("dg_investment_mode_analysis.csv"),
        "type": load_csv("dg_buy_sell_analysis.csv"),
        "price": load_csv("dg_gold_price_trends.csv"),
        "wallet": load_csv("dg_wallet_balance_analysis.csv"),
    }

    print("\n1. ANALYTICS FILE RECORD COUNTS")
    print("-" * 65)

    expected_rows = {
        "customer": 5000,
        "segment": 2,
        "daily": 679,
        "mode": 4,
        "type": 2,
        "price": 700,
        "wallet": 5000,
    }

    for name, df in datasets.items():

        check(
            len(df) == expected_rows[name],
            (
                f"{name} dataset row count | "
                f"Actual: {len(df)}, "
                f"Expected: {expected_rows[name]}"
            )
        )

    with sqlite3.connect(DB_PATH) as conn:

        source = pd.read_sql_query(
            """
            SELECT
                COUNT(*) AS total_transactions,

                SUM(CASE
                    WHEN transaction_status = 'SUCCESS'
                    THEN 1 ELSE 0
                END) AS successful_transactions,

                SUM(CASE
                    WHEN transaction_status = 'FAILED'
                    THEN 1 ELSE 0
                END) AS failed_transactions,

                SUM(CASE
                    WHEN transaction_status = 'PENDING'
                    THEN 1 ELSE 0
                END) AS pending_transactions,

                SUM(CASE
                    WHEN transaction_type = 'BUY'
                     AND transaction_status = 'SUCCESS'
                    THEN amount ELSE 0
                END) AS buy_amount,

                SUM(CASE
                    WHEN transaction_type = 'SELL'
                     AND transaction_status = 'SUCCESS'
                    THEN amount ELSE 0
                END) AS sell_amount,

                SUM(CASE
                    WHEN transaction_status = 'SUCCESS'
                    THEN amount ELSE 0
                END) AS successful_amount,

                SUM(CASE
                    WHEN transaction_status = 'FAILED'
                    THEN amount ELSE 0
                END) AS failed_amount,

                SUM(CASE
                    WHEN transaction_status = 'PENDING'
                    THEN amount ELSE 0
                END) AS pending_amount,

                SUM(CASE
                    WHEN transaction_type = 'BUY'
                     AND transaction_status = 'SUCCESS'
                    THEN gold_quantity_grams ELSE 0
                END) AS gold_bought_grams,

                SUM(CASE
                    WHEN transaction_type = 'SELL'
                     AND transaction_status = 'SUCCESS'
                    THEN gold_quantity_grams ELSE 0
                END) AS gold_sold_grams

            FROM dg_transactions
            """,
            conn
        ).iloc[0]

        # --------------------------------------------------
        # 4. CUSTOMER RECONCILIATION
        # --------------------------------------------------

        print("\n2. CUSTOMER ANALYTICS RECONCILIATION")
        print("-" * 65)

        customer = datasets["customer"]

        check(
            customer["total_transactions"].sum()
            == source["total_transactions"],
            "Customer transaction count reconciliation"
        )

        check(
            customer["successful_transactions"].sum()
            == source["successful_transactions"],
            "Customer successful transaction reconciliation"
        )

        check(
            customer["failed_transactions"].sum()
            == source["failed_transactions"],
            "Customer failed transaction reconciliation"
        )

        check(
            customer["pending_transactions"].sum()
            == source["pending_transactions"],
            "Customer pending transaction reconciliation"
        )

        check(
            values_match(
                customer["total_buy_amount"].sum(),
                source["buy_amount"]
            ),
            "Customer BUY amount reconciliation"
        )

        check(
            values_match(
                customer["total_sell_amount"].sum(),
                source["sell_amount"]
            ),
            "Customer SELL amount reconciliation"
        )

        check(
            values_match(
                customer["total_gold_bought_grams"].sum(),
                source["gold_bought_grams"],
                tolerance=0.000001
            ),
            "Customer gold bought quantity reconciliation"
        )

        check(
            values_match(
                customer["total_gold_sold_grams"].sum(),
                source["gold_sold_grams"],
                tolerance=0.000001
            ),
            "Customer gold sold quantity reconciliation"
        )

        # --------------------------------------------------
        # 5. CUSTOMER SEGMENT RECONCILIATION
        # --------------------------------------------------

        print("\n3. CUSTOMER SEGMENT RECONCILIATION")
        print("-" * 65)

        segment = datasets["segment"]

        source_customers = pd.read_sql_query(
            "SELECT COUNT(*) AS total_customers FROM dg_customers",
            conn
        ).iloc[0]["total_customers"]

        check(
            segment["total_customers"].sum() == source_customers,
            "Customer segment customer count reconciliation"
        )

        check(
            segment["total_transactions"].sum()
            == source["total_transactions"],
            "Segment transaction count reconciliation"
        )

        check(
            segment["successful_transactions"].sum()
            == source["successful_transactions"],
            "Segment successful transaction reconciliation"
        )

        check(
            segment["failed_transactions"].sum()
            == source["failed_transactions"],
            "Segment failed transaction reconciliation"
        )

        check(
            segment["pending_transactions"].sum()
            == source["pending_transactions"],
            "Segment pending transaction reconciliation"
        )

        check(
            values_match(
                segment["total_buy_amount"].sum(),
                source["buy_amount"]
            ),
            "Segment BUY amount reconciliation"
        )

        check(
            values_match(
                segment["total_sell_amount"].sum(),
                source["sell_amount"]
            ),
            "Segment SELL amount reconciliation"
        )

        # --------------------------------------------------
        # 6. DAILY TREND RECONCILIATION
        # --------------------------------------------------

        print("\n4. DAILY TREND RECONCILIATION")
        print("-" * 65)

        daily = datasets["daily"]

        check(
            daily["total_transactions"].sum()
            == source["total_transactions"],
            "Daily total transaction reconciliation"
        )

        check(
            daily["successful_transactions"].sum()
            == source["successful_transactions"],
            "Daily successful transaction reconciliation"
        )

        check(
            daily["failed_transactions"].sum()
            == source["failed_transactions"],
            "Daily failed transaction reconciliation"
        )

        check(
            daily["pending_transactions"].sum()
            == source["pending_transactions"],
            "Daily pending transaction reconciliation"
        )

        check(
            daily["successful_buy_transactions"].sum()
            == int(source["successful_transactions"]) - int(
                pd.read_sql_query(
                    """
                    SELECT COUNT(*)
                    FROM dg_transactions
                    WHERE transaction_type = 'SELL'
                    AND transaction_status = 'SUCCESS'
                    """,
                    conn
                ).iloc[0, 0]
            ),
            "Daily successful BUY count reconciliation"
        )

        check(
            values_match(
                daily["total_buy_amount"].sum(),
                source["buy_amount"]
            ),
            "Daily BUY amount reconciliation"
        )

        check(
            values_match(
                daily["total_sell_amount"].sum(),
                source["sell_amount"]
            ),
            "Daily SELL amount reconciliation"
        )

        check(
            values_match(
                daily["total_successful_transaction_amount"].sum(),
                source["successful_amount"]
            ),
            "Daily successful transaction amount reconciliation"
        )

        # --------------------------------------------------
        # 7. INVESTMENT MODE RECONCILIATION
        # --------------------------------------------------

        print("\n5. INVESTMENT MODE RECONCILIATION")
        print("-" * 65)

        mode = datasets["mode"]

        check(
            mode["total_transactions"].sum()
            == source["total_transactions"],
            "Investment mode transaction count reconciliation"
        )

        check(
            mode["successful_transactions"].sum()
            == source["successful_transactions"],
            "Investment mode successful transaction reconciliation"
        )

        check(
            mode["failed_transactions"].sum()
            == source["failed_transactions"],
            "Investment mode failed transaction reconciliation"
        )

        check(
            mode["pending_transactions"].sum()
            == source["pending_transactions"],
            "Investment mode pending transaction reconciliation"
        )

        check(
            values_match(
                mode["successful_transaction_amount"].sum(),
                source["successful_amount"]
            ),
            "Investment mode successful amount reconciliation"
        )

        check(
            values_match(
                mode["failed_transaction_amount"].sum(),
                source["failed_amount"]
            ),
            "Investment mode failed amount reconciliation"
        )

        check(
            values_match(
                mode["pending_transaction_amount"].sum(),
                source["pending_amount"]
            ),
            "Investment mode pending amount reconciliation"
        )

        check(
            values_match(
                mode["successful_gold_quantity_grams"].sum(),
                source["gold_bought_grams"] + source["gold_sold_grams"],
                tolerance=0.000001
            ),
            "Investment mode successful gold quantity reconciliation"
        )

        # --------------------------------------------------
        # 8. BUY AND SELL RECONCILIATION
        # --------------------------------------------------

        print("\n6. BUY AND SELL RECONCILIATION")
        print("-" * 65)

        transaction_type = datasets["type"]

        check(
            transaction_type["total_transactions"].sum()
            == source["total_transactions"],
            "BUY/SELL transaction count reconciliation"
        )

        check(
            transaction_type["successful_transactions"].sum()
            == source["successful_transactions"],
            "BUY/SELL successful transaction reconciliation"
        )

        check(
            transaction_type["failed_transactions"].sum()
            == source["failed_transactions"],
            "BUY/SELL failed transaction reconciliation"
        )

        check(
            transaction_type["pending_transactions"].sum()
            == source["pending_transactions"],
            "BUY/SELL pending transaction reconciliation"
        )

        check(
            values_match(
                transaction_type["total_successful_amount"].sum(),
                source["successful_amount"]
            ),
            "BUY/SELL successful amount reconciliation"
        )

        check(
            values_match(
                transaction_type[
                    "total_successful_gold_quantity_grams"
                ].sum(),
                source["gold_bought_grams"] + source["gold_sold_grams"],
                tolerance=0.000001
            ),
            "BUY/SELL successful gold quantity reconciliation"
        )

        # --------------------------------------------------
        # 9. GOLD PRICE HISTORY VALIDATION
        # --------------------------------------------------

        print("\n7. GOLD PRICE HISTORY VALIDATION")
        print("-" * 65)

        price = datasets["price"]

        source_price_count = pd.read_sql_query(
            "SELECT COUNT(*) AS total FROM dg_price_history",
            conn
        ).iloc[0]["total"]

        check(
            len(price) == source_price_count,
            "Gold price history record count reconciliation"
        )

        source_price_dates = pd.read_sql_query(
            """
            SELECT COUNT(DISTINCT price_date) AS total
            FROM dg_price_history
            """,
            conn
        ).iloc[0]["total"]

        check(
            price["price_date"].nunique() == source_price_dates,
            "Gold price history date uniqueness"
        )

        source_prices = pd.read_sql_query(
            """
            SELECT
                price_date,
                gold_price_per_gram,
                buy_price_per_gram,
                sell_price_per_gram
            FROM dg_price_history
            ORDER BY price_date
            """,
            conn
        )

        price_comparison = price.merge(
            source_prices,
            on="price_date",
            how="left",
            suffixes=("_analytics", "_source")
        )

        price_mismatches = (
            (
                price_comparison["gold_price_per_gram_analytics"]
                - price_comparison["gold_price_per_gram_source"]
            ).abs() > 0.000001
        ).sum()

        check(
            price_mismatches == 0,
            "Gold market price reconciliation"
        )

        buy_price_mismatches = (
            (
                price_comparison["buy_price_per_gram_analytics"]
                - price_comparison["buy_price_per_gram_source"]
            ).abs() > 0.000001
        ).sum()

        check(
            buy_price_mismatches == 0,
            "Gold BUY price reconciliation"
        )

        sell_price_mismatches = (
            (
                price_comparison["sell_price_per_gram_analytics"]
                - price_comparison["sell_price_per_gram_source"]
            ).abs() > 0.000001
        ).sum()

        check(
            sell_price_mismatches == 0,
            "Gold SELL price reconciliation"
        )

        # --------------------------------------------------
        # 10. WALLET BALANCE RECONCILIATION
        # --------------------------------------------------

        print("\n8. WALLET BALANCE RECONCILIATION")
        print("-" * 65)

        wallet = datasets["wallet"]

        source_wallet = pd.read_sql_query(
            """
            WITH latest_wallet_balance AS (

                SELECT
                    customer_id,
                    balance_after_grams,

                    ROW_NUMBER() OVER (
                        PARTITION BY customer_id
                        ORDER BY entry_date DESC, ledger_id DESC
                    ) AS row_num

                FROM dg_wallet_ledger
            )

            SELECT
                c.customer_id,
                COALESCE(
                    w.balance_after_grams,
                    0
                ) AS current_gold_balance_grams

            FROM dg_customers c

            LEFT JOIN latest_wallet_balance w
                ON c.customer_id = w.customer_id
                AND w.row_num = 1
            """,
            conn
        )

        wallet_comparison = wallet.merge(
            source_wallet,
            on="customer_id",
            how="left",
            suffixes=("_analytics", "_source")
        )

        wallet_mismatches = (
            (
                wallet_comparison["current_gold_balance_grams_analytics"]
                - wallet_comparison["current_gold_balance_grams_source"]
            ).abs() > 0.000001
        ).sum()

        check(
            wallet_mismatches == 0,
            "Customer wallet balance reconciliation"
        )

        check(
            wallet["customer_id"].nunique() == source_customers,
            "Wallet dataset customer uniqueness"
        )

    # --------------------------------------------------
    # 11. FINAL SUMMARY
    # --------------------------------------------------

    print("\n" + "=" * 65)
    print("DIGITAL GOLD ANALYTICS QUALITY SUMMARY")
    print("=" * 65)

    print(f"Total checks : {total_checks}")
    print(f"Passed       : {passed_checks}")
    print(f"Failed       : {failed_checks}")

    print("=" * 65)

    if failed_checks == 0:
        print("ALL DIGITAL GOLD ANALYTICS QUALITY CHECKS PASSED!")
    else:
        print("SOME DIGITAL GOLD ANALYTICS QUALITY CHECKS FAILED.")

        raise AssertionError(
            f"{failed_checks} analytics quality check(s) failed."
        )


# --------------------------------------------------
# 12. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_analytics_quality_checks()
