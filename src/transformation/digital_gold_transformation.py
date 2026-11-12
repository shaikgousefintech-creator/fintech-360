
import logging
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "digital_gold"
CURATED_DIR = PROJECT_ROOT / "data" / "curated" / "digital_gold"

CURATED_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOGGING CONFIGURATION
# --------------------------------------------------

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "digital_gold_transformation.log"

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
    """Convert a date column into standard YYYY-MM-DD format."""

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
# 4. CUSTOMER TRANSFORMATION
# --------------------------------------------------

def transform_customers():

    df = load_dataset(
        "digital_gold_customers.csv",
        [
            "customer_id",
            "customer_name",
            "age",
            "gender",
            "city",
            "registration_date",
            "customer_segment"
        ]
    )

    df = clean_text_columns(
        df,
        [
            "customer_id",
            "customer_name",
            "gender",
            "city",
            "customer_segment"
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
    df["customer_segment"] = (
        df["customer_segment"].str.upper()
    )

    save_dataset(
        df,
        "digital_gold_customers_curated.csv"
    )

    return df


# --------------------------------------------------
# 5. GOLD PRICE HISTORY TRANSFORMATION
# --------------------------------------------------

def transform_price_history():

    df = load_dataset(
        "digital_gold_price_history.csv",
        [
            "price_id",
            "price_date",
            "gold_price_per_gram",
            "buy_price_per_gram",
            "sell_price_per_gram"
        ]
    )

    df = clean_text_columns(
        df,
        ["price_id"]
    )

    df = convert_numeric_columns(
        df,
        [
            "gold_price_per_gram",
            "buy_price_per_gram",
            "sell_price_per_gram"
        ]
    )

    df = convert_date_column(
        df,
        "price_date"
    )

    price_dates = pd.to_datetime(
        df["price_date"]
    )

    df["price_year"] = price_dates.dt.year
    df["price_month"] = price_dates.dt.month
    df["price_quarter"] = price_dates.dt.quarter

    save_dataset(
        df,
        "digital_gold_price_history_curated.csv"
    )

    return df


# --------------------------------------------------
# 6. DIGITAL GOLD TRANSACTION TRANSFORMATION
# --------------------------------------------------

def transform_transactions():

    df = load_dataset(
        "digital_gold_transactions.csv",
        [
            "transaction_id",
            "customer_id",
            "transaction_date",
            "transaction_type",
            "investment_mode",
            "gold_quantity_grams",
            "gold_price_per_gram",
            "amount",
            "transaction_status",
            "failure_reason"
        ]
    )

    df = clean_text_columns(
        df,
        [
            "transaction_id",
            "customer_id",
            "transaction_type",
            "investment_mode",
            "transaction_status"
        ]
    )

    df = convert_numeric_columns(
        df,
        [
            "gold_quantity_grams",
            "gold_price_per_gram",
            "amount"
        ]
    )

    df = convert_date_column(
        df,
        "transaction_date"
    )

    df["transaction_type"] = (
        df["transaction_type"].str.upper()
    )

    df["investment_mode"] = (
        df["investment_mode"].str.upper()
    )

    df["transaction_status"] = (
        df["transaction_status"].str.upper()
    )

    df["failure_reason"] = (
        df["failure_reason"].fillna("")
    )

    df["failure_reason"] = (
        df["failure_reason"].str.strip()
    )

    transaction_dates = pd.to_datetime(
        df["transaction_date"]
    )

    df["transaction_year"] = transaction_dates.dt.year
    df["transaction_month"] = transaction_dates.dt.month
    df["transaction_month_name"] = (
        transaction_dates.dt.month_name()
    )
    df["transaction_quarter"] = (
        transaction_dates.dt.quarter
    )
    df["transaction_day"] = transaction_dates.dt.day
    df["transaction_weekday"] = (
        transaction_dates.dt.day_name()
    )

    save_dataset(
        df,
        "digital_gold_transactions_curated.csv"
    )

    return df


# --------------------------------------------------
# 7. WALLET LEDGER TRANSFORMATION
# --------------------------------------------------

def transform_wallet_ledger():

    df = load_dataset(
        "digital_gold_wallet_ledger.csv",
        [
            "ledger_id",
            "customer_id",
            "transaction_id",
            "entry_date",
            "transaction_type",
            "gold_quantity_grams",
            "balance_after_grams"
        ]
    )

    df = clean_text_columns(
        df,
        [
            "ledger_id",
            "customer_id",
            "transaction_id",
            "transaction_type"
        ]
    )

    df = convert_numeric_columns(
        df,
        [
            "gold_quantity_grams",
            "balance_after_grams"
        ]
    )

    df = convert_date_column(
        df,
        "entry_date"
    )

    df["transaction_type"] = (
        df["transaction_type"].str.upper()
    )

    save_dataset(
        df,
        "digital_gold_wallet_ledger_curated.csv"
    )

    return df


# --------------------------------------------------
# 8. MAIN TRANSFORMATION PIPELINE
# --------------------------------------------------

def main():

    print("=" * 65)
    print("FINTECH 360 - DIGITAL GOLD DATA TRANSFORMATION")
    print("=" * 65)

    logging.info("DIGITAL GOLD TRANSFORMATION STARTED")

    try:

        customers = transform_customers()

        price_history = transform_price_history()

        transactions = transform_transactions()

        wallet_ledger = transform_wallet_ledger()

        print("\n" + "=" * 65)
        print("DIGITAL GOLD TRANSFORMATION SUMMARY")
        print("=" * 65)

        print(f"Customers: {len(customers):,}")
        print(f"Price history records: {len(price_history):,}")
        print(f"Transactions: {len(transactions):,}")
        print(f"Wallet ledger entries: {len(wallet_ledger):,}")

        print(f"\nOutput directory: {CURATED_DIR}")

        print("=" * 65)
        print("DIGITAL GOLD TRANSFORMATION COMPLETED")
        print("=" * 65)

        logging.info(
            "DIGITAL GOLD TRANSFORMATION COMPLETED SUCCESSFULLY"
        )

    except Exception:

        logging.exception(
            "DIGITAL GOLD TRANSFORMATION FAILED"
        )

        print("\nDIGITAL GOLD TRANSFORMATION FAILED!")
        print("Check logs/digital_gold_transformation.log")

        raise


if __name__ == "__main__":
    main()
