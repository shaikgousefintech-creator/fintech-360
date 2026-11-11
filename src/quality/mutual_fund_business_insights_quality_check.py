
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
    / "mutual_funds"
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


def values_match(actual, expected, tolerance=5.00):

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

    print("=" * 65)
    print("FINTECH 360 - MUTUAL FUNDS BUSINESS INSIGHTS VALIDATION")
    print("=" * 65)

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    datasets = {
        "top_investors": load_csv("mf_top_investors.csv"),
        "segments": load_csv("mf_investor_segment_insights.csv"),
        "schemes": load_csv("mf_scheme_insights.csv"),
        "categories": load_csv("mf_category_insights.csv"),
        "modes": load_csv("mf_investment_mode_insights.csv"),
        "monthly": load_csv("mf_monthly_investment_flows.csv"),
    }

    print("\n1. DATASET RECORD COUNT CHECKS")
    print("-" * 65)

    expected_counts = {
        "top_investors": 20,
        "segments": 2,
        "schemes": 20,
        "categories": 4,
        "modes": 3,
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
                    WHEN transaction_type = 'PURCHASE'
                     AND transaction_status = 'SUCCESS'
                    THEN amount ELSE 0
                END) AS purchase_amount,

                SUM(CASE
                    WHEN transaction_type = 'REDEMPTION'
                     AND transaction_status = 'SUCCESS'
                    THEN amount ELSE 0
                END) AS redemption_amount,

                SUM(CASE
                    WHEN transaction_status = 'SUCCESS'
                    THEN amount ELSE 0
                END) AS successful_amount

            FROM mf_transactions
            """,
            conn
        ).iloc[0]

        # --------------------------------------------------
        # 4. TOP INVESTOR VALIDATION
        # --------------------------------------------------

        print("\n2. TOP INVESTOR VALIDATION")
        print("-" * 65)

        top = datasets["top_investors"]

        expected_top = pd.read_sql_query(
            """
            SELECT
                investor_id,
                net_investment_amount

            FROM mart_mf_investor_performance

            ORDER BY
                net_investment_amount DESC,
                investor_id

            LIMIT 20
            """,
            conn
        )

        check(
            top["investor_id"].tolist()
            == expected_top["investor_id"].tolist(),
            "Top 20 investor ranking"
        )

        check(
            values_match(
                top["net_investment_amount"].sum(),
                expected_top["net_investment_amount"].sum()
            ),
            "Top 20 investor net investment reconciliation"
        )

        # --------------------------------------------------
        # 5. INVESTOR SEGMENT VALIDATION
        # --------------------------------------------------

        print("\n3. INVESTOR SEGMENT VALIDATION")
        print("-" * 65)

        segments = datasets["segments"]

        check(
            segments["total_investors"].sum() == 1000,
            "Investor segment total investor count"
        )

        check(
            segments["total_transactions"].sum()
            == source["total_transactions"],
            "Investor segment transaction count"
        )

        check(
            values_match(
                segments["net_investment_amount"].sum(),
                source["purchase_amount"]
                - source["redemption_amount"]
            ),
            "Investor segment net investment reconciliation"
        )

        check(
            values_match(
                segments["total_purchase_amount"].sum(),
                source["purchase_amount"]
            ),
            "Investor segment purchase amount reconciliation"
        )

        check(
            values_match(
                segments["total_redemption_amount"].sum(),
                source["redemption_amount"]
            ),
            "Investor segment redemption amount reconciliation"
        )

        # --------------------------------------------------
        # 6. SCHEME AND CATEGORY VALIDATION
        # --------------------------------------------------

        print("\n4. SCHEME AND CATEGORY VALIDATION")
        print("-" * 65)

        for name in ["schemes", "categories"]:

            df = datasets[name]

            check(
                df["total_transactions"].sum()
                == source["total_transactions"],
                f"{name.title()} transaction count"
            )

            check(
                values_match(
                    df["total_purchase_amount"].sum(),
                    source["purchase_amount"]
                ),
                f"{name.title()} purchase amount"
            )

            check(
                values_match(
                    df["total_redemption_amount"].sum(),
                    source["redemption_amount"]
                ),
                f"{name.title()} redemption amount"
            )

            check(
                values_match(
                    df["net_investment_amount"].sum(),
                    source["purchase_amount"]
                    - source["redemption_amount"]
                ),
                f"{name.title()} net investment"
            )

        # --------------------------------------------------
        # 7. INVESTMENT MODE VALIDATION
        # --------------------------------------------------

        print("\n5. INVESTMENT MODE VALIDATION")
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
            values_match(
                modes["successful_transaction_amount"].sum(),
                source["successful_amount"]
            ),
            "Investment mode successful amount"
        )

        check(
            set(modes["investment_mode"])
            == {"SIP", "LUMP_SUM", "NOT_APPLICABLE"},
            "Expected investment modes"
        )

        # --------------------------------------------------
        # 8. MONTHLY INVESTMENT FLOW VALIDATION
        # --------------------------------------------------

        print("\n6. MONTHLY INVESTMENT FLOW VALIDATION")
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

                ROUND(SUM(CASE
                    WHEN transaction_type = 'PURCHASE'
                     AND transaction_status = 'SUCCESS'
                    THEN amount ELSE 0
                END), 2) AS successful_purchase_amount,

                ROUND(SUM(CASE
                    WHEN transaction_type = 'REDEMPTION'
                     AND transaction_status = 'SUCCESS'
                    THEN amount ELSE 0
                END), 2) AS successful_redemption_amount

            FROM mf_transactions

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
            values_match(
                monthly["successful_purchase_amount"].sum(),
                source["purchase_amount"]
            ),
            "Monthly purchase amount reconciliation"
        )

        check(
            values_match(
                monthly["successful_redemption_amount"].sum(),
                source["redemption_amount"]
            ),
            "Monthly redemption amount reconciliation"
        )

        check(
            values_match(
                monthly["net_successful_transaction_amount"].sum(),
                source["purchase_amount"]
                - source["redemption_amount"]
            ),
            "Monthly net investment reconciliation"
        )

    # --------------------------------------------------
    # 9. FINAL SUMMARY
    # --------------------------------------------------

    print("\n" + "=" * 65)
    print("MUTUAL FUNDS BUSINESS INSIGHTS QUALITY SUMMARY")
    print("=" * 65)

    print(f"Total checks : {total_checks}")
    print(f"Passed       : {passed_checks}")
    print(f"Failed       : {failed_checks}")

    print("=" * 65)

    if failed_checks == 0:

        print(
            "ALL MUTUAL FUNDS BUSINESS INSIGHTS CHECKS PASSED!"
        )

    else:

        print(
            "SOME BUSINESS INSIGHTS CHECKS FAILED."
        )

        raise AssertionError(
            f"{failed_checks} business insights check(s) failed."
        )


# --------------------------------------------------
# 10. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_business_insights_quality_checks()
