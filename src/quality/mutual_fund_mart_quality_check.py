
import sqlite3
from pathlib import Path


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

MARTS = [
    "mart_mf_investor_performance",
    "mart_mf_scheme_performance",
    "mart_mf_daily_performance",
    "mart_mf_category_performance",
]

checks = []


# --------------------------------------------------
# 2. VALIDATION HELPER
# --------------------------------------------------

def add_check(name, condition, details=""):

    status = "PASSED" if condition else "FAILED"

    checks.append({
        "name": name,
        "status": status,
        "details": details
    })

    print(
        f"{name}: {status}"
        + (f" | {details}" if details else "")
    )


def get_value(conn, query):

    result = conn.execute(query).fetchone()

    return result[0] if result else 0


def compare_values(actual, expected, tolerance=0.01):

    return abs(
        float(actual or 0) - float(expected or 0)
    ) <= tolerance


# --------------------------------------------------
# 3. MAIN QUALITY VALIDATION
# --------------------------------------------------

def run_quality_checks():

    print("=" * 65)
    print("FINTECH 360 - MUTUAL FUNDS MART QUALITY VALIDATION")
    print("=" * 65)

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    global checks
    checks = []

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("PRAGMA foreign_keys = ON")

        # ------------------------------------------
        # CHECK 1: MART EXISTENCE
        # ------------------------------------------

        print("\n1. MART EXISTENCE CHECKS")
        print("-" * 65)

        existing_views = {
            row[0]
            for row in conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'view'
                """
            ).fetchall()
        }

        for mart in MARTS:

            add_check(
                f"{mart} exists",
                mart in existing_views
            )

        missing_marts = [
            mart for mart in MARTS
            if mart not in existing_views
        ]

        if missing_marts:
            raise RuntimeError(
                f"Missing analytical marts: {missing_marts}"
            )

        # ------------------------------------------
        # CHECK 2: MART RECORD COUNTS
        # ------------------------------------------

        print("\n2. MART RECORD COUNT CHECKS")
        print("-" * 65)

        source_investors = get_value(
            conn,
            "SELECT COUNT(*) FROM mf_investors"
        )

        source_schemes = get_value(
            conn,
            "SELECT COUNT(*) FROM mf_schemes"
        )

        expected_daily = get_value(
            conn,
            """
            SELECT COUNT(DISTINCT transaction_date)
            FROM mf_transactions
            """
        )

        expected_categories = get_value(
            conn,
            """
            SELECT COUNT(DISTINCT fund_category)
            FROM mf_schemes
            """
        )

        actual_counts = {
            "mart_mf_investor_performance":
                get_value(conn, "SELECT COUNT(*) FROM mart_mf_investor_performance"),

            "mart_mf_scheme_performance":
                get_value(conn, "SELECT COUNT(*) FROM mart_mf_scheme_performance"),

            "mart_mf_daily_performance":
                get_value(conn, "SELECT COUNT(*) FROM mart_mf_daily_performance"),

            "mart_mf_category_performance":
                get_value(conn, "SELECT COUNT(*) FROM mart_mf_category_performance"),
        }

        expected_counts = {
            "mart_mf_investor_performance": source_investors,
            "mart_mf_scheme_performance": source_schemes,
            "mart_mf_daily_performance": expected_daily,
            "mart_mf_category_performance": expected_categories,
        }

        for mart in MARTS:

            actual = actual_counts[mart]
            expected = expected_counts[mart]

            add_check(
                f"{mart} record count",
                actual == expected,
                f"Actual: {actual}, Expected: {expected}"
            )

        # ------------------------------------------
        # CHECK 3: TRANSACTION COUNT RECONCILIATION
        # ------------------------------------------

        print("\n3. TRANSACTION COUNT RECONCILIATION")
        print("-" * 65)

        source_transactions = get_value(
            conn,
            "SELECT COUNT(*) FROM mf_transactions"
        )

        for mart in MARTS:

            actual = get_value(
                conn,
                f"SELECT COALESCE(SUM(total_transactions), 0) FROM {mart}"
            )

            add_check(
                f"{mart} transaction count",
                actual == source_transactions,
                f"Actual: {actual}, Source: {source_transactions}"
            )

        # ------------------------------------------
        # CHECK 4: STATUS COUNT RECONCILIATION
        # ------------------------------------------

        print("\n4. TRANSACTION STATUS RECONCILIATION")
        print("-" * 65)

        for status in ["SUCCESS", "FAILED"]:

            source_count = get_value(
                conn,
                f"""
                SELECT COUNT(*)
                FROM mf_transactions
                WHERE transaction_status = '{status}'
                """
            )

            for mart in MARTS:

                actual = get_value(
                    conn,
                    f"""
                    SELECT COALESCE(SUM(
                        {'successful_transactions' if status == 'SUCCESS' else 'failed_transactions'}
                    ), 0)
                    FROM {mart}
                    """
                )

                add_check(
                    f"{mart} {status.lower()} count",
                    actual == source_count,
                    f"Actual: {actual}, Source: {source_count}"
                )

        # ------------------------------------------
        # CHECK 5: FINANCIAL AMOUNT RECONCILIATION
        # ------------------------------------------

        print("\n5. FINANCIAL AMOUNT RECONCILIATION")
        print("-" * 65)

        amount_checks = {
            "total_purchase_amount": """
                SELECT COALESCE(SUM(amount), 0)
                FROM mf_transactions
                WHERE transaction_status = 'SUCCESS'
                AND transaction_type = 'PURCHASE'
            """,

            "total_redemption_amount": """
                SELECT COALESCE(SUM(amount), 0)
                FROM mf_transactions
                WHERE transaction_status = 'SUCCESS'
                AND transaction_type = 'REDEMPTION'
            """,
        }

        for column, query in amount_checks.items():

            source_amount = get_value(conn, query)

            for mart in [
                "mart_mf_investor_performance",
                "mart_mf_scheme_performance",
                "mart_mf_category_performance",
            ]:

                actual = get_value(
                    conn,
                    f"""
                    SELECT COALESCE(SUM({column}), 0)
                    FROM {mart}
                    """
                )

                add_check(
                    f"{mart} {column}",
                    compare_values(actual, source_amount),
                    f"Actual: {actual:.2f}, Source: {source_amount:.2f}"
                )

        # Daily mart amount reconciliation
        daily_amount = get_value(
            conn,
            """
            SELECT COALESCE(SUM(total_successful_transaction_amount), 0)
            FROM mart_mf_daily_performance
            """
        )

        source_success_amount = get_value(
            conn,
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM mf_transactions
            WHERE transaction_status = 'SUCCESS'
            """
        )

        add_check(
            "Daily successful transaction amount",
            compare_values(daily_amount, source_success_amount),
            f"Actual: {daily_amount:.2f}, Source: {source_success_amount:.2f}"
        )

        # ------------------------------------------
        # CHECK 6: SUCCESS RATE VALIDATION
        # ------------------------------------------

        print("\n6. SUCCESS RATE VALIDATION")
        print("-" * 65)

        rate_checks = [
            (
                "mart_mf_scheme_performance",
                """
                SELECT COUNT(*)
                FROM mart_mf_scheme_performance
                WHERE success_rate_percentage IS NOT
                    ROUND(
                        100.0 * successful_transactions /
                        NULLIF(total_transactions, 0), 2
                    )
                """
            ),
            (
                "mart_mf_category_performance",
                """
                SELECT COUNT(*)
                FROM mart_mf_category_performance
                WHERE success_rate_percentage IS NOT
                    ROUND(
                        100.0 * successful_transactions /
                        NULLIF(total_transactions, 0), 2
                    )
                """
            ),
            (
                "mart_mf_daily_performance",
                """
                SELECT COUNT(*)
                FROM mart_mf_daily_performance
                WHERE success_rate_percentage IS NOT
                    ROUND(
                        100.0 * successful_transactions /
                        NULLIF(total_transactions, 0), 2
                    )
                """
            ),
        ]

        for mart, query in rate_checks:

            invalid_rates = get_value(conn, query)

            add_check(
                f"{mart} success rate",
                invalid_rates == 0,
                f"Incorrect rates: {invalid_rates}"
            )

        # ------------------------------------------
        # CHECK 7: DAILY PURCHASE AND REDEMPTION
        # ------------------------------------------

        print("\n7. DAILY TRANSACTION TYPE VALIDATION")
        print("-" * 65)

        invalid_daily = get_value(
            conn,
            """
            SELECT COUNT(*)
            FROM mart_mf_daily_performance
            WHERE successful_purchases != (
                SELECT COUNT(*)
                FROM mf_transactions t
                WHERE t.transaction_date =
                    mart_mf_daily_performance.transaction_date
                AND t.transaction_type = 'PURCHASE'
                AND t.transaction_status = 'SUCCESS'
            )
            OR successful_redemptions != (
                SELECT COUNT(*)
                FROM mf_transactions t
                WHERE t.transaction_date =
                    mart_mf_daily_performance.transaction_date
                AND t.transaction_type = 'REDEMPTION'
                AND t.transaction_status = 'SUCCESS'
            )
            """
        )

        add_check(
            "Daily purchase and redemption counts",
            invalid_daily == 0,
            f"Incorrect daily records: {invalid_daily}"
        )

        # ------------------------------------------
        # CHECK 8: DUPLICATE AGGREGATION KEYS
        # ------------------------------------------

        print("\n8. DUPLICATE AGGREGATION CHECKS")
        print("-" * 65)

        duplicate_queries = {
            "Investor mart": """
                SELECT COUNT(*) FROM (
                    SELECT investor_id
                    FROM mart_mf_investor_performance
                    GROUP BY investor_id
                    HAVING COUNT(*) > 1
                )
            """,

            "Scheme mart": """
                SELECT COUNT(*) FROM (
                    SELECT scheme_id
                    FROM mart_mf_scheme_performance
                    GROUP BY scheme_id
                    HAVING COUNT(*) > 1
                )
            """,

            "Daily mart": """
                SELECT COUNT(*) FROM (
                    SELECT transaction_date
                    FROM mart_mf_daily_performance
                    GROUP BY transaction_date
                    HAVING COUNT(*) > 1
                )
            """,

            "Category mart": """
                SELECT COUNT(*) FROM (
                    SELECT fund_category
                    FROM mart_mf_category_performance
                    GROUP BY fund_category
                    HAVING COUNT(*) > 1
                )
            """,
        }

        for name, query in duplicate_queries.items():

            duplicates = get_value(conn, query)

            add_check(
                f"{name} duplicate keys",
                duplicates == 0,
                f"Duplicates: {duplicates}"
            )

        # ------------------------------------------
        # CHECK 9: FOREIGN KEY INTEGRITY
        # ------------------------------------------

        print("\n9. FOREIGN KEY INTEGRITY")
        print("-" * 65)

        foreign_key_errors = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        add_check(
            "Database foreign key integrity",
            len(foreign_key_errors) == 0,
            f"Violations: {len(foreign_key_errors)}"
        )

    # --------------------------------------------------
    # 10. FINAL SUMMARY
    # --------------------------------------------------

    total_checks = len(checks)

    passed = sum(
        check["status"] == "PASSED"
        for check in checks
    )

    failed = total_checks - passed

    print("\n" + "=" * 65)
    print("MUTUAL FUNDS MART QUALITY SUMMARY")
    print("=" * 65)

    print(f"Total checks : {total_checks}")
    print(f"Passed       : {passed}")
    print(f"Failed       : {failed}")

    print("=" * 65)

    if failed == 0:

        print("ALL MUTUAL FUNDS MART QUALITY CHECKS PASSED!")

    else:

        print("MUTUAL FUNDS MART QUALITY VALIDATION FAILED!")

        print("\nFailed checks:")

        for check in checks:

            if check["status"] == "FAILED":

                print(
                    f"- {check['name']}: {check['details']}"
                )

        raise SystemExit(1)


# --------------------------------------------------
# 11. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_quality_checks()
