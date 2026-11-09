
"""
FINTECH 360
UPI ANALYTICAL MART RECONCILIATION

Purpose:
Validate analytical marts against the original
UPI transaction warehouse table.
"""

import sqlite3
from pathlib import Path
import math
import sys


# --------------------------------------------------
# 1. DATABASE CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = (
    PROJECT_ROOT
    / "data"
    / "warehouse"
    / "database"
    / "fintech360.db"
)


# --------------------------------------------------
# 2. RECONCILIATION FUNCTION
# --------------------------------------------------

def run_mart_quality_checks():

    print("=" * 65)
    print("FINTECH 360 - UPI MART RECONCILIATION")
    print("=" * 65)

    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    results = []

    def check(description, passed):

        status = "PASS" if passed else "FAIL"

        print(f"[{status}] {description}")

        results.append(passed)

    try:

        # ------------------------------------------
        # 3. SOURCE TABLE METRICS
        # ------------------------------------------

        source = cursor.execute("""
            SELECT
                COUNT(*),

                SUM(CASE WHEN status = 'SUCCESS'
                    THEN 1 ELSE 0 END),

                SUM(CASE WHEN status = 'FAILED'
                    THEN 1 ELSE 0 END),

                SUM(CASE WHEN status = 'PENDING'
                    THEN 1 ELSE 0 END),

                SUM(amount),

                SUM(CASE WHEN status = 'SUCCESS'
                    THEN amount ELSE 0 END)

            FROM upi_transactions
        """).fetchone()

        (
            source_total,
            source_success,
            source_failed,
            source_pending,
            source_value,
            source_success_value
        ) = source

        # ------------------------------------------
        # 4. MART DEFINITIONS
        # ------------------------------------------

        marts = [
            (
                "Daily Performance",
                "mart_upi_daily_performance",
                "transaction_date",
                "transaction_date"
            ),
            (
                "Bank Performance",
                "mart_upi_bank_performance",
                "payer_bank",
                "payer_bank"
            ),
            (
                "Payment App Performance",
                "mart_upi_payment_app_performance",
                "payment_app",
                "payment_app"
            )
        ]

        # ------------------------------------------
        # 5. VALIDATE EACH MART
        # ------------------------------------------

        for name, view, group_column, source_column in marts:

            print(f"\n--- {name} MART ---")

            mart = cursor.execute(f"""
                SELECT
                    COUNT(*),
                    SUM(total_transactions),
                    SUM(successful_transactions),
                    SUM(failed_transactions),
                    SUM(pending_transactions),
                    SUM(total_transaction_value),
                    SUM(successful_transaction_value)
                FROM {view}
            """).fetchone()

            (
                mart_groups,
                mart_total,
                mart_success,
                mart_failed,
                mart_pending,
                mart_value,
                mart_success_value
            ) = mart

            # Transaction count reconciliation

            check(
                "Total transaction counts match",
                mart_total == source_total
            )

            check(
                "Successful transaction counts match",
                mart_success == source_success
            )

            check(
                "Failed transaction counts match",
                mart_failed == source_failed
            )

            check(
                "Pending transaction counts match",
                mart_pending == source_pending
            )

            # Transaction value reconciliation

            check(
                "Total transaction values match",
                math.isclose(
                    mart_value or 0,
                    source_value or 0,
                    abs_tol=0.01
                )
            )

            check(
                "Successful transaction values match",
                math.isclose(
                    mart_success_value or 0,
                    source_success_value or 0,
                    abs_tol=0.01
                )
            )

            # Group coverage validation

            expected_groups = cursor.execute(f"""
                SELECT COUNT(DISTINCT {source_column})
                FROM upi_transactions
            """).fetchone()[0]

            check(
                "Expected aggregation groups present",
                mart_groups == expected_groups
            )

            # Success rate validation

            inconsistent_rates = cursor.execute(f"""
                SELECT COUNT(*)
                FROM {view}
                WHERE ABS(
                    success_rate_percentage -
                    ROUND(
                        100.0 * successful_transactions /
                        NULLIF(total_transactions, 0),
                        2
                    )
                ) > 0.01
            """).fetchone()[0]

            check(
                "Success rates correctly calculated",
                inconsistent_rates == 0
            )

        # ------------------------------------------
        # 6. FINAL QUALITY REPORT
        # ------------------------------------------

        passed = sum(results)
        failed = len(results) - passed

        print("\n" + "=" * 65)
        print("UPI MART RECONCILIATION REPORT")
        print("=" * 65)

        print(f"Total checks : {len(results)}")
        print(f"Passed checks: {passed}")
        print(f"Failed checks: {failed}")

        if failed == 0:
            print("\nUPI MART RECONCILIATION SUCCESSFUL!")
        else:
            print("\nUPI MART RECONCILIATION FAILED!")
            sys.exit(1)

    finally:
        db.close()


# --------------------------------------------------
# 7. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_mart_quality_checks()
