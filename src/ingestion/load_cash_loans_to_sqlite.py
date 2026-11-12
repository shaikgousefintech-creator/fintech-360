
import sqlite3
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "curated" / "cash_loans"

DB_PATH = (
    BASE_DIR
    / "data"
    / "warehouse"
    / "database"
    / "fintech360.db"
)


# --------------------------------------------------
# 2. CSV FILES AND DATABASE TABLE CONFIGURATION
# --------------------------------------------------

LOAD_CONFIG = [
    {
        "file": "cash_loan_customers_curated.csv",
        "table": "cl_customers",
        "columns": [
            "customer_id",
            "customer_name",
            "age",
            "gender",
            "city",
            "registration_date",
            "customer_segment",
        ],
    },
    {
        "file": "cash_loan_products_curated.csv",
        "table": "cl_loan_products",
        "columns": [
            "product_id",
            "product_name",
            "loan_type",
            "min_loan_amount",
            "max_loan_amount",
            "annual_interest_rate",
            "min_tenure_months",
            "max_tenure_months",
            "processing_fee_percentage",
            "launch_date",
        ],
    },
    {
        "file": "cash_loan_applications_curated.csv",
        "table": "cl_loan_applications",
        "columns": [
            "application_id",
            "customer_id",
            "product_id",
            "application_date",
            "requested_amount",
            "approved_amount",
            "credit_score",
            "employment_type",
            "monthly_income",
            "application_status",
            "rejection_reason",
        ],
    },
    {
        "file": "cash_loan_disbursements_curated.csv",
        "table": "cl_loan_disbursements",
        "columns": [
            "disbursement_id",
            "application_id",
            "disbursement_date",
            "disbursed_amount",
            "disbursement_status",
            "failure_reason",
        ],
    },
    {
        "file": "cash_loan_repayments_curated.csv",
        "table": "cl_loan_repayments",
        "columns": [
            "repayment_id",
            "disbursement_id",
            "installment_number",
            "due_date",
            "payment_date",
            "principal_amount",
            "interest_amount",
            "total_due_amount",
            "amount_paid",
            "repayment_status",
            "late_days",
        ],
    },
]


# --------------------------------------------------
# 3. CASH LOANS SQLITE LOADING
# --------------------------------------------------

def load_cash_loans():

    print("=" * 65)
    print("FINTECH 360 - CASH LOANS SQLITE DATA LOADING")
    print("=" * 65)

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"SQLite database not found: {DB_PATH}"
        )

    # Read and validate all CSV files before modifying the database.

    datasets = {}

    for config in LOAD_CONFIG:

        file_path = DATA_DIR / config["file"]

        if not file_path.exists():
            raise FileNotFoundError(
                f"Input file not found: {file_path}"
            )

        df = pd.read_csv(
            file_path,
            low_memory=False
        )

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

        # Enable foreign-key enforcement.

        conn.execute("PRAGMA foreign_keys = ON")

        with conn:

            # Clear existing Cash Loans records.
            # Child tables must be cleared before parent tables.

            conn.execute(
                "DELETE FROM cl_loan_repayments"
            )

            conn.execute(
                "DELETE FROM cl_loan_disbursements"
            )

            conn.execute(
                "DELETE FROM cl_loan_applications"
            )

            conn.execute(
                "DELETE FROM cl_loan_products"
            )

            conn.execute(
                "DELETE FROM cl_customers"
            )

            # Load records in parent-to-child order.

            for config in LOAD_CONFIG:

                table = config["table"]
                columns = config["columns"]

                df = datasets[table]

                # Keep only columns defined in the SQL schema.

                df = df[columns].astype(object)

                # Convert pandas missing values into Python None.
                # SQLite stores Python None as SQL NULL.

                df = df.where(
                    pd.notna(df),
                    None
                )

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

            # Verify foreign-key relationships.

            fk_errors = conn.execute(
                "PRAGMA foreign_key_check"
            ).fetchall()

            if fk_errors:
                raise ValueError(
                    f"Foreign-key validation failed: {fk_errors}"
                )

            # Verify database integrity.

            integrity = conn.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0]

            if integrity != "ok":
                raise ValueError(
                    f"Database integrity check failed: {integrity}"
                )

        # Display loading summary after successful commit.

        print("\n" + "=" * 65)
        print("CASH LOANS LOADING SUMMARY")
        print("=" * 65)

        for config in LOAD_CONFIG:

            table = config["table"]

            count = conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(
                f"{table}: {count:,} records"
            )

        print("\nForeign-key check: PASSED")
        print("Database integrity check: PASSED")

        print("\nCASH LOANS DATA LOADING COMPLETED")

    finally:

        conn.close()


# --------------------------------------------------
# 4. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    load_cash_loans()
