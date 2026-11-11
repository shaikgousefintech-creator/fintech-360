
import sqlite3
from pathlib import Path

import pandas as pd


# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "curated" / "mutual_funds"
DB_PATH = (
    BASE_DIR
    / "data"
    / "warehouse"
    / "database"
    / "fintech360.db"
)


# CSV files and their corresponding database tables
LOAD_CONFIG = [
    {
        "file": "mutual_fund_investors_curated.csv",
        "table": "mf_investors",
        "columns": [
            "investor_id",
            "investor_name",
            "age",
            "gender",
            "city",
            "registration_date",
            "investor_segment",
        ],
    },
    {
        "file": "mutual_fund_schemes_curated.csv",
        "table": "mf_schemes",
        "columns": [
            "scheme_id",
            "scheme_name",
            "fund_house",
            "fund_category",
            "risk_level",
            "benchmark",
            "expense_ratio",
            "launch_date",
        ],
    },
    {
        "file": "mutual_fund_nav_history_curated.csv",
        "table": "mf_nav_history",
        "columns": [
            "nav_id",
            "scheme_id",
            "nav_date",
            "nav_value",
        ],
    },
    {
        "file": "mutual_fund_transactions_curated.csv",
        "table": "mf_transactions",
        "columns": [
            "investment_id",
            "investor_id",
            "scheme_id",
            "transaction_date",
            "transaction_type",
            "investment_mode",
            "amount",
            "nav",
            "units",
            "transaction_status",
            "failure_reason",
        ],
    },
]


def load_mutual_funds():

    print("=" * 60)
    print("FINTECH 360 - MUTUAL FUNDS SQLITE DATA LOADING")
    print("=" * 60)

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"SQLite database not found: {DB_PATH}"
        )

    # Read and validate all CSV files before modifying the database
    datasets = {}

    for config in LOAD_CONFIG:

        file_path = DATA_DIR / config["file"]

        if not file_path.exists():
            raise FileNotFoundError(
                f"Input file not found: {file_path}"
            )

        df = pd.read_csv(file_path)

        missing_columns = [
            column
            for column in config["columns"]
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"{config['file']} is missing columns: "
                f"{missing_columns}"
            )

        datasets[config["table"]] = df

        print(
            f"Read: {config['file']} | "
            f"Records: {len(df):,}"
        )

    conn = sqlite3.connect(DB_PATH)

    try:

        # Enable foreign-key enforcement for this connection
        conn.execute("PRAGMA foreign_keys = ON")

        with conn:

            # Clear only Mutual Funds tables.
            # Child tables are cleared before parent tables.
            conn.execute("DELETE FROM mf_transactions")
            conn.execute("DELETE FROM mf_nav_history")
            conn.execute("DELETE FROM mf_schemes")
            conn.execute("DELETE FROM mf_investors")

            # Load data in parent-to-child order
            for config in LOAD_CONFIG:

                table = config["table"]
                columns = config["columns"]

                df = datasets[table]

                # Keep only columns defined in the SQL schema
                df = df[columns].astype(object)
                df = df.where(pd.notna(df), None)

                column_names = ", ".join(columns)
                placeholders = ", ".join(
                    ["?"] * len(columns)
                )

                sql = (
                    f"INSERT INTO {table} "
                    f"({column_names}) "
                    f"VALUES ({placeholders})"
                )

                conn.executemany(
                    sql,
                    df.itertuples(
                        index=False,
                        name=None
                    )
                )

                print(
                    f"Loaded: {table} | "
                    f"Records: {len(df):,}"
                )

            # Verify foreign-key relationships
            fk_errors = conn.execute(
                "PRAGMA foreign_key_check"
            ).fetchall()

            if fk_errors:
                raise ValueError(
                    f"Foreign-key validation failed: {fk_errors}"
                )

            # Verify database integrity
            integrity = conn.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0]

            if integrity != "ok":
                raise ValueError(
                    f"Database integrity check failed: {integrity}"
                )

        print("\n" + "=" * 60)
        print("MUTUAL FUNDS LOADING SUMMARY")
        print("=" * 60)

        for config in LOAD_CONFIG:

            table = config["table"]

            count = conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"{table}: {count:,} records")

        print("\nForeign-key check: PASSED")
        print("Database integrity check: PASSED")
        print("MUTUAL FUNDS DATA LOADING COMPLETED")

    finally:
        conn.close()


if __name__ == "__main__":
    load_mutual_funds()
