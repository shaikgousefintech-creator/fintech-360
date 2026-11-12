
import sqlite3
from pathlib import Path
import math

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
    / "digital_gold"
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


# --------------------------------------------------
# 3. MAIN VALIDATION
# --------------------------------------------------

def run_business_insights_quality_checks():

    global total_checks, passed_checks, failed_checks

    total_checks = 0
    passed_checks = 0
    failed_checks = 0

    print("=" * 65)
    print("FINTECH 360 - DIGITAL GOLD BUSINESS INSIGHTS VALIDATION")
    print("=" * 65)

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    if not INSIGHTS_DIR.exists():
        raise FileNotFoundError(
            f"Insights directory not found: {INSIGHTS_DIR}"
        )

    datasets = {
        "top_customers": load_csv("dg_top_customers.csv"),
        "segments": load_csv("dg_customer_segment_insights.csv"),
        "cities": load_csv("dg_city_wise_insights.csv"),
        "transaction_types": load_csv("dg_transaction_type_insights.csv"),
        "modes": load_csv("dg_investment_mode_insights.csv"),
        "monthly": load_csv("dg_monthly_gold_flows.csv"),
    }

    print("\n1. DATASET RECORD COUNT CHECKS")
    print("-" * 65)

    expected_counts = {
        "top_customers": 20,
        "segments": 2,
        "cities": 10,
        "transaction_types": 2,
        "modes": 4,
    }

    for name, expected in expected_counts.items():

        actual = len(datasets[name])

        check(
            actual == expected,
            f"{name} records | Actual: {actual}, Expected: {expected}"
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
        # 4. TOP CUSTOMER VALIDATION
        # --------------------------------------------------

        print("\n2. TOP CUSTOMER VALIDATION")
        print("-" * 65)

        top = datasets["top_customers"]

        expected_top = pd.read_sql_query(
            """
            SELECT
                customer_id,

                ROUND(
                    total_gold_bought_grams
                    - total_gold_sold_grams,
                    6
                ) AS net_gold_accumulated_grams

            FROM mart_dg_customer_performance

            ORDER BY
                net_gold_accumulated_grams DESC,
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
                top["net_gold_accumulated_grams"].sum(),
                expected_top["net_gold_accumulated_grams"].sum(),
                tolerance=0.000001
            ),
            "Top 20 customer net gold accumulation reconciliation"
        )

        # --------------------------------------------------
        # 5. CUSTOMER SEGMENT VALIDATION
        # --------------------------------------------------

        print("\n3. CUSTOMER SEGMENT VALIDATION")
        print("-" * 65)

        segments = datasets["segments"]

        source_customers = pd.read_sql_query(
            """
            SELECT COUNT(*) AS total_customers
            FROM dg_customers
            """,
            conn
        ).iloc[0]["total_customers"]

        check(
            segments["total_customers"].sum() == source_customers,
            "Customer segment total customer count"
        )

        check(
            segments["total_transactions"].sum()
            == source["total_transactions"],
            "Customer segment transaction count"
        )

        check(
            segments["successful_transactions"].sum()
            == source["successful_transactions"],
            "Customer segment successful transaction count"
        )

        check(
            segments["failed_transactions"].sum()
            == source["failed_transactions"],
            "Customer segment failed transaction count"
        )

        check(
            segments["pending_transactions"].sum()
            == source["pending_transactions"],
            "Customer segment pending transaction count"
        )

        check(
            values_match(
                segments["total_buy_amount"].sum(),
                source["buy_amount"]
            ),
            "Customer segment BUY amount reconciliation"
        )

        check(
            values_match(
                segments["total_sell_amount"].sum(),
                source["sell_amount"]
            ),
            "Customer segment SELL amount reconciliation"
        )

        check(
            values_match(
                segments["net_gold_accumulated_grams"].sum(),
                source["gold_bought_grams"] - source["gold_sold_grams"],
                tolerance=0.000001
            ),
            "Customer segment net gold accumulation reconciliation"
        )

        # --------------------------------------------------
        # 6. CITY-WISE CUSTOMER VALIDATION
        # --------------------------------------------------

        print("\n4. CITY-WISE CUSTOMER VALIDATION")
        print("-" * 65)

        cities = datasets["cities"]

        expected_cities = pd.read_sql_query(
            """
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
                    SUM(
                        total_gold_bought_grams
                        - total_gold_sold_grams
                    ), 6
                ) AS net_gold_accumulated_grams

            FROM mart_dg_customer_performance

            GROUP BY city

            ORDER BY net_gold_accumulated_grams DESC
            """,
            conn
        )

        cities = cities.sort_values(
            "city"
        ).reset_index(drop=True)

        expected_cities = expected_cities.sort_values(
            "city"
        ).reset_index(drop=True)

        check(
            cities["city"].tolist()
            == expected_cities["city"].tolist(),
            "City-wise location coverage"
        )

        check(
            cities["total_customers"].sum() == source_customers,
            "City-wise total customer count"
        )

        check(
            cities["total_transactions"].sum()
            == source["total_transactions"],
            "City-wise transaction count"
        )

        check(
            cities["successful_transactions"].sum()
            == source["successful_transactions"],
            "City-wise successful transaction count"
        )

        check(
            cities["failed_transactions"].sum()
            == source["failed_transactions"],
            "City-wise failed transaction count"
        )

        check(
            cities["pending_transactions"].sum()
            == source["pending_transactions"],
            "City-wise pending transaction count"
        )

        check(
            values_match(
                cities["total_buy_amount"].sum(),
                source["buy_amount"]
            ),
            "City-wise BUY amount reconciliation"
        )

        check(
            values_match(
                cities["total_sell_amount"].sum(),
                source["sell_amount"]
            ),
            "City-wise SELL amount reconciliation"
        )

        check(
            values_match(
                cities["net_gold_accumulated_grams"].sum(),
                source["gold_bought_grams"] - source["gold_sold_grams"],
                tolerance=0.000001
            ),
            "City-wise net gold accumulation reconciliation"
        )

        # --------------------------------------------------
        # 7. BUY AND SELL VALIDATION
        # --------------------------------------------------

        print("\n5. BUY AND SELL VALIDATION")
        print("-" * 65)

        transaction_types = datasets["transaction_types"]

        check(
            transaction_types["total_transactions"].sum()
            == source["total_transactions"],
            "BUY/SELL transaction count"
        )

        check(
            transaction_types["successful_transactions"].sum()
            == source["successful_transactions"],
            "BUY/SELL successful transaction count"
        )

        check(
            transaction_types["failed_transactions"].sum()
            == source["failed_transactions"],
            "BUY/SELL failed transaction count"
        )

        check(
            transaction_types["pending_transactions"].sum()
            == source["pending_transactions"],
            "BUY/SELL pending transaction count"
        )

        check(
            values_match(
                transaction_types["total_successful_amount"].sum(),
                source["successful_amount"]
            ),
            "BUY/SELL successful amount reconciliation"
        )

        check(
            values_match(
                transaction_types[
                    "total_successful_gold_quantity_grams"
                ].sum(),
                source["gold_bought_grams"] + source["gold_sold_grams"],
                tolerance=0.000001
            ),
            "BUY/SELL successful gold quantity reconciliation"
        )

        # --------------------------------------------------
        # 8. INVESTMENT MODE VALIDATION
        # --------------------------------------------------

        print("\n6. INVESTMENT MODE VALIDATION")
        print("-" * 65)

        modes = datasets["modes"]

        check(
            modes["total_transactions"].sum()
            == source["total_transactions"],
            "Investment mode transaction count"
        )

        check(
            modes["successful_transactions"].sum()
            == source["successful_transactions"],
            "Investment mode successful transaction count"
        )

        check(
            modes["failed_transactions"].sum()
            == source["failed_transactions"],
            "Investment mode failed transaction count"
        )

        check(
            modes["pending_transactions"].sum()
            == source["pending_transactions"],
            "Investment mode pending transaction count"
        )

        check(
            values_match(
                modes["successful_transaction_amount"].sum(),
                source["successful_amount"]
            ),
            "Investment mode successful amount"
        )

        check(
            values_match(
                modes["successful_gold_quantity_grams"].sum(),
                source["gold_bought_grams"] + source["gold_sold_grams"],
                tolerance=0.000001
            ),
            "Investment mode successful gold quantity"
        )

        check(
            set(modes["investment_mode"])
            == {"UPI", "BANK_TRANSFER", "CARD", "WALLET"},
            "Expected investment modes"
        )

        # --------------------------------------------------
        # 9. MONTHLY GOLD FLOW VALIDATION
        # --------------------------------------------------

        print("\n7. MONTHLY GOLD FLOW VALIDATION")
        print("-" * 65)

        monthly = datasets["monthly"]

        expected_monthly = pd.read_sql_query(
            """
            SELECT
                SUBSTR(transaction_date, 1, 7)
                    AS transaction_month,

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

                ROUND(SUM(CASE
                    WHEN transaction_type = 'BUY'
                     AND transaction_status = 'SUCCESS'
                    THEN amount ELSE 0
                END), 2) AS successful_buy_amount,

                ROUND(SUM(CASE
                    WHEN transaction_type = 'SELL'
                     AND transaction_status = 'SUCCESS'
                    THEN amount ELSE 0
                END), 2) AS successful_sell_amount,

                ROUND(SUM(CASE
                    WHEN transaction_type = 'BUY'
                     AND transaction_status = 'SUCCESS'
                    THEN gold_quantity_grams

                    WHEN transaction_type = 'SELL'
                     AND transaction_status = 'SUCCESS'
                    THEN -gold_quantity_grams

                    ELSE 0
                END), 6) AS net_gold_accumulated_grams

            FROM dg_transactions

            GROUP BY SUBSTR(transaction_date, 1, 7)

            ORDER BY transaction_month
            """,
            conn
        )

        monthly = monthly.sort_values(
            "transaction_month"
        ).reset_index(drop=True)

        expected_monthly = expected_monthly.sort_values(
            "transaction_month"
        ).reset_index(drop=True)

        check(
            len(monthly) == len(expected_monthly),
            "Monthly dataset record count"
        )

        check(
            monthly["transaction_month"].tolist()
            == expected_monthly["transaction_month"].tolist(),
            "Monthly date coverage"
        )

        check(
            monthly["total_transactions"].sum()
            == source["total_transactions"],
            "Monthly transaction count reconciliation"
        )

        check(
            monthly["successful_transactions"].sum()
            == source["successful_transactions"],
            "Monthly successful transaction reconciliation"
        )

        check(
            monthly["failed_transactions"].sum()
            == source["failed_transactions"],
            "Monthly failed transaction reconciliation"
        )

        check(
            monthly["pending_transactions"].sum()
            == source["pending_transactions"],
            "Monthly pending transaction reconciliation"
        )

        check(
            values_match(
                monthly["successful_buy_amount"].sum(),
                source["buy_amount"]
            ),
            "Monthly BUY amount reconciliation"
        )

        check(
            values_match(
                monthly["successful_sell_amount"].sum(),
                source["sell_amount"]
            ),
            "Monthly SELL amount reconciliation"
        )

        check(
            values_match(
                monthly["net_successful_transaction_amount"].sum(),
                source["buy_amount"] - source["sell_amount"]
            ),
            "Monthly net transaction amount reconciliation"
        )

        check(
            values_match(
                monthly["net_gold_accumulated_grams"].sum(),
                source["gold_bought_grams"] - source["gold_sold_grams"],
                tolerance=0.000001
            ),
            "Monthly net gold accumulation reconciliation"
        )

    # --------------------------------------------------
    # 10. FINAL SUMMARY
    # --------------------------------------------------

    print("\n" + "=" * 65)
    print("DIGITAL GOLD BUSINESS INSIGHTS QUALITY SUMMARY")
    print("=" * 65)

    print(f"Total checks : {total_checks}")
    print(f"Passed       : {passed_checks}")
    print(f"Failed       : {failed_checks}")

    print("=" * 65)

    if failed_checks == 0:

        print(
            "ALL DIGITAL GOLD BUSINESS INSIGHTS CHECKS PASSED!"
        )

    else:

        print(
            "SOME BUSINESS INSIGHTS CHECKS FAILED."
        )

        raise AssertionError(
            f"{failed_checks} business insights check(s) failed."
        )


# --------------------------------------------------
# 11. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_business_insights_quality_checks()
