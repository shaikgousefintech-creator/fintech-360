
import logging
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "mutual_funds"
CURATED_DIR = PROJECT_ROOT / "data" / "curated" / "mutual_funds"

CURATED_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOGGING CONFIGURATION
# --------------------------------------------------

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "mutual_fund_transformation.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    force=True
)


# --------------------------------------------------
# 3. HELPER FUNCTIONS
# --------------------------------------------------

def load_dataset(file_name, required_columns):
    """Load a CSV file and validate its required columns."""

    file_path = RAW_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{file_name} is missing columns: {missing_columns}"
        )

    logging.info(
        "Loaded %s | Records: %s",
        file_name,
        len(df)
    )

    return df


def clean_text_columns(df, columns):
    """Remove leading and trailing whitespace."""

    for column in columns:
        df[column] = df[column].str.strip()

    return df


def convert_date_column(df, column):
    """Convert a date column into a standard YYYY-MM-DD format."""

    df[column] = pd.to_datetime(
        df[column],
        errors="raise"
    )

    df[column] = df[column].dt.strftime("%Y-%m-%d")

    return df


def convert_numeric_columns(df, columns):
    """Convert selected columns into numeric data types."""

    for column in columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="raise"
        )

    return df


def save_dataset(df, file_name):
    """Save the transformed dataset."""

    output_path = CURATED_DIR / file_name

    df.to_csv(
        output_path,
        index=False
    )

    logging.info(
        "Saved %s | Records: %s",
        file_name,
        len(df)
    )

    print(
        f"Created: {file_name} | Records: {len(df):,}"
    )


# --------------------------------------------------
# 4. INVESTOR TRANSFORMATION
# --------------------------------------------------

def transform_investors():

    df = load_dataset(
        "mutual_fund_investors.csv",
        [
            "investor_id",
            "investor_name",
            "age",
            "gender",
            "city",
            "registration_date",
            "investor_segment"
        ]
    )

    df = clean_text_columns(
        df,
        [
            "investor_id",
            "investor_name",
            "gender",
            "city",
            "investor_segment"
        ]
    )

    df = convert_numeric_columns(
        df,
        ["age"]
    )

    df["age"] = df["age"].astype("int64")

    df = convert_date_column(
        df,
        "registration_date"
    )

    df["gender"] = df["gender"].str.upper()
    df["investor_segment"] = df["investor_segment"].str.upper()

    save_dataset(
        df,
        "mutual_fund_investors_curated.csv"
    )

    return df


# --------------------------------------------------
# 5. SCHEME TRANSFORMATION
# --------------------------------------------------

def transform_schemes():

    df = load_dataset(
        "mutual_fund_schemes.csv",
        [
            "scheme_id",
            "scheme_name",
            "fund_house",
            "fund_category",
            "risk_level",
            "benchmark",
            "expense_ratio",
            "launch_date"
        ]
    )

    df = clean_text_columns(
        df,
        [
            "scheme_id",
            "scheme_name",
            "fund_house",
            "fund_category",
            "risk_level",
            "benchmark"
        ]
    )

    df = convert_numeric_columns(
        df,
        ["expense_ratio"]
    )

    df["fund_category"] = df["fund_category"].str.upper()
    df["risk_level"] = df["risk_level"].str.upper()

    df = convert_date_column(
        df,
        "launch_date"
    )

    save_dataset(
        df,
        "mutual_fund_schemes_curated.csv"
    )

    return df


# --------------------------------------------------
# 6. NAV HISTORY TRANSFORMATION
# --------------------------------------------------

def transform_nav_history():

    df = load_dataset(
        "mutual_fund_nav_history.csv",
        [
            "nav_id",
            "scheme_id",
            "nav_date",
            "nav_value"
        ]
    )

    df = clean_text_columns(
        df,
        [
            "nav_id",
            "scheme_id"
        ]
    )

    df = convert_numeric_columns(
        df,
        ["nav_value"]
    )

    df = convert_date_column(
        df,
        "nav_date"
    )

    nav_dates = pd.to_datetime(df["nav_date"])

    df["nav_year"] = nav_dates.dt.year
    df["nav_month"] = nav_dates.dt.month
    df["nav_quarter"] = nav_dates.dt.quarter

    save_dataset(
        df,
        "mutual_fund_nav_history_curated.csv"
    )

    return df


# --------------------------------------------------
# 7. INVESTMENT TRANSACTION TRANSFORMATION
# --------------------------------------------------

def transform_transactions():

    df = load_dataset(
        "mutual_fund_transactions.csv",
        [
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
            "failure_reason"
        ]
    )

    df = clean_text_columns(
        df,
        [
            "investment_id",
            "investor_id",
            "scheme_id",
            "transaction_type",
            "investment_mode",
            "transaction_status"
        ]
    )

    df = convert_numeric_columns(
        df,
        [
            "amount",
            "nav",
            "units"
        ]
    )

    df = convert_date_column(
        df,
        "transaction_date"
    )

    df["transaction_type"] = df["transaction_type"].str.upper()
    df["investment_mode"] = df["investment_mode"].str.upper()
    df["transaction_status"] = df["transaction_status"].str.upper()

    df["failure_reason"] = df["failure_reason"].fillna("")
    df["failure_reason"] = df["failure_reason"].str.strip()

    transaction_dates = pd.to_datetime(
        df["transaction_date"]
    )

    df["transaction_year"] = transaction_dates.dt.year
    df["transaction_month"] = transaction_dates.dt.month
    df["transaction_month_name"] = transaction_dates.dt.month_name()
    df["transaction_quarter"] = transaction_dates.dt.quarter
    df["transaction_day"] = transaction_dates.dt.day
    df["transaction_weekday"] = transaction_dates.dt.day_name()

    save_dataset(
        df,
        "mutual_fund_transactions_curated.csv"
    )

    return df


# --------------------------------------------------
# 8. MAIN TRANSFORMATION PIPELINE
# --------------------------------------------------

def main():

    print("=" * 65)
    print("FINTECH 360 - MUTUAL FUNDS DATA TRANSFORMATION")
    print("=" * 65)

    logging.info("MUTUAL FUNDS TRANSFORMATION STARTED")

    try:

        investors = transform_investors()
        schemes = transform_schemes()
        nav_history = transform_nav_history()
        transactions = transform_transactions()

        print("\n" + "=" * 65)
        print("MUTUAL FUNDS TRANSFORMATION SUMMARY")
        print("=" * 65)

        print(f"Investors: {len(investors):,}")
        print(f"Schemes: {len(schemes):,}")
        print(f"NAV records: {len(nav_history):,}")
        print(f"Transactions: {len(transactions):,}")

        print(f"\nOutput directory: {CURATED_DIR}")

        print("=" * 65)
        print("MUTUAL FUNDS TRANSFORMATION COMPLETED")
        print("=" * 65)

        logging.info(
            "MUTUAL FUNDS TRANSFORMATION COMPLETED SUCCESSFULLY"
        )

    except Exception:

        logging.exception(
            "MUTUAL FUNDS TRANSFORMATION FAILED"
        )

        print("\nMUTUAL FUNDS TRANSFORMATION FAILED!")
        print("Check logs/mutual_fund_transformation.log")

        raise


if __name__ == "__main__":
    main()
