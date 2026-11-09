
from pathlib import Path
import logging
import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "upi"
    / "upi_transactions_processed.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "curated"
    / "upi"
)

OUTPUT_FILE = OUTPUT_DIR / "upi_transactions_curated.csv"

LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "upi_transformation.log"


# --------------------------------------------------
# 2. LOGGING CONFIGURATION
# --------------------------------------------------

def setup_logging():

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        force=True
    )

    logging.info("UPI transformation pipeline started.")


# --------------------------------------------------
# 3. READ PROCESSED DATA
# --------------------------------------------------

def read_processed_data():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Processed input file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        dtype={
            "transaction_id": "string",
            "payer_id": "string",
            "payee_id": "string"
        }
    )

    logging.info(f"Input records loaded: {len(df)}")

    return df


# --------------------------------------------------
# 4. STANDARDIZE DATA
# --------------------------------------------------

def standardize_data(df):

    df = df.copy()

    # Remove unnecessary spaces from text columns
    for col in df.select_dtypes(
        include=["object", "string"]
    ).columns:

        df[col] = df[col].astype("string").str.strip()

    # Standardize categorical columns
    categorical_columns = [
        "transaction_type",
        "status",
        "currency"
    ]

    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].str.upper()

    # Standardize payment application names
    if "payment_app" in df.columns:
        df["payment_app"] = df["payment_app"].str.upper()

    # Convert transaction amount to numeric
    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="raise"
    ).round(2)

    # Convert transaction timestamp
    df["transaction_timestamp"] = pd.to_datetime(
        df["transaction_timestamp"],
        errors="raise"
    )

    logging.info("Data standardization completed.")

    return df


# --------------------------------------------------
# 5. CREATE DERIVED COLUMNS
# --------------------------------------------------

def create_derived_columns(df):

    df = df.copy()

    timestamp = df["transaction_timestamp"]

    # Extract transaction date
    df["transaction_date"] = timestamp.dt.date

    # Extract year
    df["transaction_year"] = timestamp.dt.year

    # Extract month
    df["transaction_month"] = timestamp.dt.month

    # Extract day
    df["transaction_day"] = timestamp.dt.day

    # Extract hour
    df["transaction_hour"] = timestamp.dt.hour

    # Extract weekday
    df["transaction_day_of_week"] = (
        timestamp.dt.day_name()
    )

    # Create transaction status indicators
    df["is_successful"] = df["status"].eq("SUCCESS")

    df["is_failed"] = df["status"].eq("FAILED")

    df["is_pending"] = df["status"].eq("PENDING")

    logging.info("Derived columns created successfully.")

    return df


# --------------------------------------------------
# 6. SAVE CURATED DATA
# --------------------------------------------------

def save_curated_data(df):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    logging.info(
        f"Curated data saved: {OUTPUT_FILE}"
    )


# --------------------------------------------------
# 7. MAIN TRANSFORMATION PIPELINE
# --------------------------------------------------

def run_transformation():

    setup_logging()

    try:

        # Read processed data
        df = read_processed_data()

        input_count = len(df)

        # Standardize data
        df = standardize_data(df)

        # Create analytical columns
        df = create_derived_columns(df)

        # Basic transformation checks
        if df["transaction_timestamp"].isna().any():
            raise ValueError(
                "Invalid timestamps found after transformation."
            )

        if df["amount"].isna().any() or (df["amount"] <= 0).any():
            raise ValueError(
                "Invalid transaction amounts found."
            )

        if len(df) != input_count:
            raise ValueError(
                "Record count changed during transformation."
            )

        # Save curated data
        save_curated_data(df)

        logging.info(
            "UPI transformation pipeline completed successfully."
        )

        # Display transformation report
        print("\n" + "=" * 45)
        print("UPI DATA TRANSFORMATION REPORT")
        print("=" * 45)

        print(f"Input records       : {input_count}")
        print(f"Curated records     : {len(df)}")
        print(f"Total columns       : {len(df.columns)}")

        print(f"\nOutput file: {OUTPUT_FILE}")

        print("\nTransaction status distribution:")
        print(df["status"].value_counts())

        print("\nCurated data sample:")
        print(
            df[
                [
                    "transaction_id",
                    "amount",
                    "status",
                    "transaction_date",
                    "transaction_hour",
                    "is_successful"
                ]
            ].head()
        )

        print("\nUPI TRANSFORMATION COMPLETED SUCCESSFULLY!")

    except Exception as error:

        logging.exception(
            f"UPI transformation failed: {error}"
        )

        print(f"\nTRANSFORMATION FAILED: {error}")

        raise


# --------------------------------------------------
# 8. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_transformation()
