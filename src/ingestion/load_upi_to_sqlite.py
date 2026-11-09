
import sqlite3
import pandas as pd
from pathlib import Path


# Project directories
BASE_DIR = Path(__file__).resolve().parents[2]

CSV_PATH = (
    BASE_DIR
    / "data"
    / "curated"
    / "upi"
    / "upi_transactions_curated.csv"
)

DB_PATH = (
    BASE_DIR
    / "data"
    / "warehouse"
    / "database"
    / "fintech360.db"
)


def load_upi_data():

    print("=" * 55)
    print("FINTECH 360 - UPI SQLITE DATA LOADER")
    print("=" * 55)

    # Check input files
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    # Read curated data
    df = pd.read_csv(CSV_PATH)

    print(f"Source records: {len(df)}")

    # Connect to SQLite
    with sqlite3.connect(DB_PATH) as conn:

        # Read database table columns
        db_columns = [
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(upi_transactions)"
            ).fetchall()
        ]

        if not db_columns:
            raise RuntimeError(
                "upi_transactions table does not exist."
            )

        # Validate columns
        missing = set(db_columns) - set(df.columns)

        if missing:
            raise ValueError(
                f"Missing CSV columns: {missing}"
            )

        # Match database column order
        df = df[db_columns]

        # Convert missing values to SQL NULL
        df = df.astype(object).where(
            pd.notna(df), None
        )

        # Insert or update records
        placeholders = ", ".join(["?"] * len(db_columns))
        columns = ", ".join(db_columns)

        sql = f"""
            INSERT OR REPLACE INTO upi_transactions
            ({columns})
            VALUES ({placeholders})
        """

        conn.executemany(
            sql,
            df.itertuples(index=False, name=None)
        )

        # Verify loaded records
        result = conn.execute(
            "SELECT COUNT(*) FROM upi_transactions"
        ).fetchone()[0]

        print(f"Records loaded: {len(df)}")
        print(f"Records in database: {result}")

    print("\nUPI DATA LOADING COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    load_upi_data()
