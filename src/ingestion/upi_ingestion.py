
from pathlib import Path
import logging
import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "upi" / "upi_transactions.csv"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "upi"
REJECTED_DIR = PROJECT_ROOT / "data" / "rejected" / "upi"
LOG_DIR = PROJECT_ROOT / "logs"

PROCESSED_FILE = PROCESSED_DIR / "upi_transactions_processed.csv"
REJECTED_FILE = REJECTED_DIR / "upi_transactions_rejected.csv"
LOG_FILE = LOG_DIR / "upi_ingestion.log"


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

    logging.info("UPI ingestion pipeline started.")


# --------------------------------------------------
# 3. DATA VALIDATION
# --------------------------------------------------

def validate_data(df):

    required_columns = [
        "transaction_id",
        "payer_id",
        "payee_id",
        "transaction_type",
        "amount",
        "currency",
        "transaction_timestamp",
        "status"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    df = df.copy()

    # Normalize string columns
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype("string").str.strip()

    for col in ["status", "transaction_type", "currency"]:
        df[col] = df[col].str.upper()

    # Convert numeric and timestamp fields
    df["amount"] = pd.to_numeric(
        df["amount"], errors="coerce"
    )

    df["transaction_timestamp"] = pd.to_datetime(
        df["transaction_timestamp"],
        format="%Y-%m-%d %H:%M:%S.%f",
        errors="coerce"
    )

    # Store rejection reasons
    errors = pd.Series("", index=df.index, dtype="string")

    def add_error(condition, message):
        nonlocal errors

        errors.loc[condition] = (
            errors.loc[condition]
            + message
            + "; "
        )

    # Required field validation
    for col in required_columns:
        invalid = (
            df[col].isna()
            | df[col].astype("string").str.strip().eq("").fillna(True)
        )

        add_error(invalid, f"Missing {col}")

    # Amount validation
    add_error(
        df["amount"].isna() | (df["amount"] <= 0),
        "Invalid transaction amount"
    )

    # Timestamp validation
    add_error(
        df["transaction_timestamp"].isna(),
        "Invalid transaction timestamp"
    )

    # Transaction status validation
    valid_statuses = ["SUCCESS", "FAILED", "PENDING"]

    add_error(
        ~df["status"].isin(valid_statuses),
        "Invalid transaction status"
    )

    # Failed transactions must have a failure reason
    if "failure_reason" in df.columns:
        failed_without_reason = (
            df["status"].eq("FAILED")
            & (
                df["failure_reason"].isna()
                | df["failure_reason"].eq("")
            )
        )

        add_error(
            failed_without_reason,
            "Missing failure reason"
        )

    # P2M transactions must have merchant names
    if "merchant_name" in df.columns:
        p2m_without_merchant = (
            df["transaction_type"].eq("P2M")
            & (
                df["merchant_name"].isna()
                | df["merchant_name"].eq("")
            )
        )

        add_error(
            p2m_without_merchant,
            "Missing merchant name"
        )

    # Duplicate transaction ID validation
    duplicate_ids = (
        df["transaction_id"].notna()
        & df["transaction_id"].ne("")
        & df["transaction_id"].duplicated(keep=False)
    )

    add_error(
        duplicate_ids,
        "Duplicate transaction ID"
    )

    # Separate valid and rejected records
    valid_mask = errors.eq("")

    valid_df = df.loc[valid_mask].copy()
    rejected_df = df.loc[~valid_mask].copy()

    rejected_df["rejection_reason"] = errors.loc[
        ~valid_mask
    ].str.rstrip("; ")

    return valid_df, rejected_df


# --------------------------------------------------
# 4. MAIN INGESTION PIPELINE
# --------------------------------------------------

def run_ingestion():

    setup_logging()

    try:

        # Create output directories
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        REJECTED_DIR.mkdir(parents=True, exist_ok=True)

        # Check input file
        if not INPUT_FILE.exists():
            raise FileNotFoundError(
                f"Input file not found: {INPUT_FILE}"
            )

        # Read raw data
        logging.info("Reading raw UPI transaction data.")

        df = pd.read_csv(INPUT_FILE)

        total_records = len(df)

        logging.info(f"Total input records: {total_records}")

        # Validate and separate records
        valid_df, rejected_df = validate_data(df)

        # Save processed records
        valid_df.to_csv(
            PROCESSED_FILE,
            index=False
        )

        # Save rejected records
        rejected_df.to_csv(
            REJECTED_FILE,
            index=False
        )

        # Log results
        logging.info(
            f"Valid records: {len(valid_df)}"
        )

        logging.info(
            f"Rejected records: {len(rejected_df)}"
        )

        logging.info("UPI ingestion pipeline completed.")

        # Display execution report
        print("\n" + "=" * 45)
        print("UPI DATA INGESTION REPORT")
        print("=" * 45)

        print(f"Total records    : {total_records}")
        print(f"Processed records: {len(valid_df)}")
        print(f"Rejected records : {len(rejected_df)}")

        print(f"\nProcessed file: {PROCESSED_FILE}")
        print(f"Rejected file : {REJECTED_FILE}")
        print(f"Log file      : {LOG_FILE}")

        print("\nUPI INGESTION COMPLETED SUCCESSFULLY!")

    except Exception as error:

        logging.exception(
            f"UPI ingestion pipeline failed: {error}"
        )

        print(f"\nINGESTION FAILED: {error}")

        raise


# --------------------------------------------------
# 5. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_ingestion()
