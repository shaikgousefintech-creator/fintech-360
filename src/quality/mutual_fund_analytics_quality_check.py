
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
    / "mutual_funds"
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

    print("=" * 65)
    print("FINTECH 360 - MUTUAL FUNDS ANALYTICS QUALITY VALIDATION")
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
        "investor": load_csv("mf_investor_behavior.csv"),
        "segment": load_csv("mf_investor_segment_analysis.csv"),
        "scheme": load_csv("mf_scheme_performance.csv"),
        "category": load_csv("mf_category_performance.csv"),
        "daily": load_csv("mf_daily_trends.csv"),
        "mode": load_csv("mf_investment_mode_analysis.csv"),
        "type": load_csv("mf_purchase_redemption_analysis.csv"),
    }

    print("\n1. ANALYTICS FILE RECORD COUNTS")
    print("-" * 65)

    expected_rows = {
        "investor": 1000,
        "segment": 2,
        "scheme": 20,
        "category": 4,
        "daily": 485,
        "mode": 3,
        "type": 2,
    }

    for name, df in datasets.items():

        check(
            len(df) == expected_rows[name],
            f"{name} dataset row count | Actual: {len(df)}, Expected: {expected_rows[name]}"
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
        # 4. INVESTOR RECONCILIATION
        # --------------------------------------------------

        print("\n2. INVESTOR ANALYTICS RECONCILIATION")
        print("-" * 65)

        investor = datasets["investor"]

        check(
            investor["total_transactions"].sum()
            == source["total_transactions"],
            "Investor transaction count reconciliation"
        )

        check(
            investor["successful_transactions"].sum()
            == source["successful_transactions"],
            "Investor successful transaction reconciliation"
        )

        check(
            investor["failed_transactions"].sum()
            == source["failed_transactions"],
            "Investor failed transaction reconciliation"
        )

        check(
            values_match(
                investor["total_purchase_amount"].sum(),
                source["purchase_amount"]
            ),
            "Investor purchase amount reconciliation"
        )

        check(
            values_match(
                investor["total_redemption_amount"].sum(),
                source["redemption_amount"]
            ),
            "Investor redemption amount reconciliation"
        )

        # --------------------------------------------------
        # 5. SEGMENT RECONCILIATION
        # --------------------------------------------------

        print("\n3. INVESTOR SEGMENT RECONCILIATION")
        print("-" * 65)

        segment = datasets["segment"]

        check(
            segment["total_investors"].sum() == 1000,
            "Segment investor count reconciliation"
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
            values_match(
                segment["total_purchase_amount"].sum(),
                source["purchase_amount"]
            ),
            "Segment purchase amount reconciliation"
        )

        check(
            values_match(
                segment["total_redemption_amount"].sum(),
                source["redemption_amount"]
            ),
            "Segment redemption amount reconciliation"
        )

        # --------------------------------------------------
        # 6. SCHEME AND CATEGORY RECONCILIATION
        # --------------------------------------------------

        print("\n4. SCHEME AND CATEGORY RECONCILIATION")
        print("-" * 65)

        for name in ["scheme", "category"]:

            df = datasets[name]

            check(
                df["total_transactions"].sum()
                == source["total_transactions"],
                f"{name.title()} transaction count reconciliation"
            )

            check(
                df["successful_transactions"].sum()
                == source["successful_transactions"],
                f"{name.title()} successful transaction reconciliation"
            )

            check(
                df["failed_transactions"].sum()
                == source["failed_transactions"],
                f"{name.title()} failed transaction reconciliation"
            )

            check(
                values_match(
                    df["total_purchase_amount"].sum(),
                    source["purchase_amount"]
                ),
                f"{name.title()} purchase amount reconciliation"
            )

            check(
                values_match(
                    df["total_redemption_amount"].sum(),
                    source["redemption_amount"]
                ),
                f"{name.title()} redemption amount reconciliation"
            )

        # --------------------------------------------------
        # 7. DAILY TREND RECONCILIATION
        # --------------------------------------------------

        print("\n5. DAILY TREND RECONCILIATION")
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
            values_match(
                daily["total_purchase_amount"].sum(),
                source["purchase_amount"]
            ),
            "Daily purchase amount reconciliation"
        )

        check(
            values_match(
                daily["total_redemption_amount"].sum(),
                source["redemption_amount"]
            ),
            "Daily redemption amount reconciliation"
        )

        check(
            values_match(
                daily["total_successful_transaction_amount"].sum(),
                source["successful_amount"]
            ),
            "Daily successful transaction amount reconciliation"
        )

        # --------------------------------------------------
        # 8. INVESTMENT MODE RECONCILIATION
        # --------------------------------------------------

        print("\n6. INVESTMENT MODE RECONCILIATION")
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
            values_match(
                mode["successful_transaction_amount"].sum(),
                source["successful_amount"]
            ),
            "Investment mode successful amount reconciliation"
        )

        # --------------------------------------------------
        # 9. PURCHASE AND REDEMPTION RECONCILIATION
        # --------------------------------------------------

        print("\n7. PURCHASE AND REDEMPTION RECONCILIATION")
        print("-" * 65)

        transaction_type = datasets["type"]

        check(
            transaction_type["total_transactions"].sum()
            == source["total_transactions"],
            "Purchase/redemption transaction count reconciliation"
        )

        check(
            transaction_type["successful_transactions"].sum()
            == source["successful_transactions"],
            "Purchase/redemption successful transaction reconciliation"
        )

        check(
            transaction_type["failed_transactions"].sum()
            == source["failed_transactions"],
            "Purchase/redemption failed transaction reconciliation"
        )

        check(
            values_match(
                transaction_type["successful_transaction_amount"].sum(),
                source["successful_amount"]
            ),
            "Purchase/redemption successful amount reconciliation"
        )

    # --------------------------------------------------
    # 10. FINAL SUMMARY
    # --------------------------------------------------

    print("\n" + "=" * 65)
    print("MUTUAL FUNDS ANALYTICS QUALITY SUMMARY")
    print("=" * 65)

    print(f"Total checks : {total_checks}")
    print(f"Passed       : {passed_checks}")
    print(f"Failed       : {failed_checks}")

    print("=" * 65)

    if failed_checks == 0:
        print("ALL MUTUAL FUNDS ANALYTICS QUALITY CHECKS PASSED!")
    else:
        print("SOME ANALYTICS QUALITY CHECKS FAILED.")
        raise AssertionError(
            f"{failed_checks} analytics quality check(s) failed."
        )


# --------------------------------------------------
# 11. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_analytics_quality_checks()
