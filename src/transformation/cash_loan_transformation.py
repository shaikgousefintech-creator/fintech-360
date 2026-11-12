
import logging
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "cash_loans"
CURATED_DIR = PROJECT_ROOT / "data" / "curated" / "cash_loans"

CURATED_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOGGING CONFIGURATION
# --------------------------------------------------

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "cash_loan_transformation.log"

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

    df = pd.read_csv(
            file_path,
            low_memory=False
        )

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
    """Convert a date column into YYYY-MM-DD format."""

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
        "cash_loan_customers.csv",
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
    df["customer_segment"] = df["customer_segment"].str.upper()

    save_dataset(
        df,
        "cash_loan_customers_curated.csv"
    )

    return df


# --------------------------------------------------
# 5. LOAN PRODUCT TRANSFORMATION
# --------------------------------------------------

def transform_loan_products():

    df = load_dataset(
        "cash_loan_products.csv",
        [
            "product_id",
            "product_name",
            "loan_type",
            "min_loan_amount",
            "max_loan_amount",
            "annual_interest_rate",
            "min_tenure_months",
            "max_tenure_months",
            "processing_fee_percentage",
            "launch_date"
        ]
    )

    df = clean_text_columns(
        df,
        [
            "product_id",
            "product_name",
            "loan_type"
        ]
    )

    df = convert_numeric_columns(
        df,
        [
            "min_loan_amount",
            "max_loan_amount",
            "annual_interest_rate",
            "min_tenure_months",
            "max_tenure_months",
            "processing_fee_percentage"
        ]
    )

    df["min_tenure_months"] = (
        df["min_tenure_months"].astype("int64")
    )

    df["max_tenure_months"] = (
        df["max_tenure_months"].astype("int64")
    )

    df["loan_type"] = df["loan_type"].str.upper()

    df = convert_date_column(
        df,
        "launch_date"
    )

    save_dataset(
        df,
        "cash_loan_products_curated.csv"
    )

    return df


# --------------------------------------------------
# 6. LOAN APPLICATION TRANSFORMATION
# --------------------------------------------------

def transform_loan_applications():

    df = load_dataset(
        "cash_loan_applications.csv",
        [
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
            "rejection_reason"
        ]
    )

    df = clean_text_columns(
        df,
        [
            "application_id",
            "customer_id",
            "product_id",
            "employment_type",
            "application_status"
        ]
    )

    df = convert_numeric_columns(
        df,
        [
            "requested_amount",
            "approved_amount",
            "credit_score",
            "monthly_income"
        ]
    )

    df["credit_score"] = df["credit_score"].astype("Int64")

    df = convert_date_column(
        df,
        "application_date"
    )

    df["employment_type"] = df["employment_type"].str.upper()

    df["application_status"] = (
        df["application_status"].str.upper()
    )

    # Preserve NULL rejection reasons for non-rejected applications.
    # Do not replace missing values with empty strings.

    if "rejection_reason" in df.columns:
        df["rejection_reason"] = (
            df["rejection_reason"]
            .str.strip()
            .str.upper()
        )

    application_dates = pd.to_datetime(
        df["application_date"]
    )

    df["application_year"] = application_dates.dt.year
    df["application_month"] = application_dates.dt.month
    df["application_month_name"] = (
        application_dates.dt.month_name()
    )
    df["application_quarter"] = application_dates.dt.quarter
    df["application_day"] = application_dates.dt.day
    df["application_weekday"] = application_dates.dt.day_name()

    save_dataset(
        df,
        "cash_loan_applications_curated.csv"
    )

    return df


# --------------------------------------------------
# 7. LOAN DISBURSEMENT TRANSFORMATION
# --------------------------------------------------

def transform_loan_disbursements():

    df = load_dataset(
        "cash_loan_disbursements.csv",
        [
            "disbursement_id",
            "application_id",
            "disbursement_date",
            "disbursed_amount",
            "disbursement_status",
            "failure_reason"
        ]
    )

    df = clean_text_columns(
        df,
        [
            "disbursement_id",
            "application_id",
            "disbursement_status"
        ]
    )

    df = convert_numeric_columns(
        df,
        ["disbursed_amount"]
    )

    df["disbursement_status"] = (
        df["disbursement_status"].str.upper()
    )

    df = convert_date_column(
        df,
        "disbursement_date"
    )

    # Preserve NULL failure reasons for successful and pending records.

    df["failure_reason"] = (
        df["failure_reason"]
        .str.strip()
        .str.upper()
    )

    disbursement_dates = pd.to_datetime(
        df["disbursement_date"]
    )

    df["disbursement_year"] = (
        disbursement_dates.dt.year
    )

    df["disbursement_month"] = (
        disbursement_dates.dt.month
    )

    df["disbursement_month_name"] = (
        disbursement_dates.dt.month_name()
    )

    df["disbursement_quarter"] = (
        disbursement_dates.dt.quarter
    )

    save_dataset(
        df,
        "cash_loan_disbursements_curated.csv"
    )

    return df


# --------------------------------------------------
# 8. LOAN REPAYMENT TRANSFORMATION
# --------------------------------------------------

def transform_loan_repayments():

    df = load_dataset(
        "cash_loan_repayments.csv",
        [
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
            "late_days"
        ]
    )

    df = clean_text_columns(
        df,
        [
            "repayment_id",
            "disbursement_id",
            "repayment_status"
        ]
    )

    df = convert_numeric_columns(
        df,
        [
            "installment_number",
            "principal_amount",
            "interest_amount",
            "total_due_amount",
            "amount_paid",
            "late_days"
        ]
    )

    df["installment_number"] = (
        df["installment_number"].astype("int64")
    )

    df["late_days"] = (
        df["late_days"].astype("int64")
    )

    df["repayment_status"] = (
        df["repayment_status"].str.upper()
    )

    df = convert_date_column(
        df,
        "due_date"
    )

    df = convert_date_column(
        df,
        "payment_date"
    )

    due_dates = pd.to_datetime(df["due_date"])

    df["due_year"] = due_dates.dt.year
    df["due_month"] = due_dates.dt.month
    df["due_month_name"] = due_dates.dt.month_name()
    df["due_quarter"] = due_dates.dt.quarter

    save_dataset(
        df,
        "cash_loan_repayments_curated.csv"
    )

    return df


# --------------------------------------------------
# 9. MAIN TRANSFORMATION PIPELINE
# --------------------------------------------------

def main():

    print("=" * 65)
    print("FINTECH 360 - CASH LOANS DATA TRANSFORMATION")
    print("=" * 65)

    logging.info("CASH LOANS TRANSFORMATION STARTED")

    try:

        customers = transform_customers()

        products = transform_loan_products()

        applications = transform_loan_applications()

        disbursements = transform_loan_disbursements()

        repayments = transform_loan_repayments()

        print("\n" + "=" * 65)
        print("CASH LOANS TRANSFORMATION SUMMARY")
        print("=" * 65)

        print(f"Customers: {len(customers):,}")
        print(f"Loan products: {len(products):,}")
        print(f"Applications: {len(applications):,}")
        print(f"Disbursements: {len(disbursements):,}")
        print(f"Repayments: {len(repayments):,}")

        print(f"\nOutput directory: {CURATED_DIR}")

        print("=" * 65)
        print("CASH LOANS TRANSFORMATION COMPLETED")
        print("=" * 65)

        logging.info(
            "CASH LOANS TRANSFORMATION COMPLETED SUCCESSFULLY"
        )

    except Exception:

        logging.exception(
            "CASH LOANS TRANSFORMATION FAILED"
        )

        print("\nCASH LOANS TRANSFORMATION FAILED!")
        print("Check logs/cash_loan_transformation.log")

        raise


if __name__ == "__main__":
    main()
