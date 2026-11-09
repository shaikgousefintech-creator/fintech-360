
"""
FINTECH 360 - UPI Time Analysis

Analyzes transaction patterns by:
1. Hour of day
2. Day of week
"""

from pathlib import Path
import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "curated"
    / "upi"
    / "upi_transactions_curated.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "warehouse" / "upi"


# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

def load_data():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"File not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "transaction_id",
        "transaction_hour",
        "transaction_day_of_week",
        "status",
        "amount"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df["transaction_hour"] = pd.to_numeric(
        df["transaction_hour"], errors="coerce"
    )

    df["amount"] = pd.to_numeric(
        df["amount"], errors="coerce"
    )

    df["status"] = (
        df["status"].astype("string").str.upper().str.strip()
    )

    if df[["transaction_hour", "amount"]].isna().any().any():
        raise ValueError("Invalid hour or transaction amount found.")

    if not df["transaction_hour"].between(0, 23).all():
        raise ValueError("Transaction hour must be between 0 and 23.")

    return df


# --------------------------------------------------
# 3. HOURLY ANALYSIS
# --------------------------------------------------

def generate_hourly_analysis(df):

    data = df.copy()

    data["successful_transactions"] = (
        data["status"] == "SUCCESS"
    ).astype(int)

    data["failed_transactions"] = (
        data["status"] == "FAILED"
    ).astype(int)

    data["pending_transactions"] = (
        data["status"] == "PENDING"
    ).astype(int)

    hourly = (
        data.groupby("transaction_hour")
        .agg(
            total_transactions=("transaction_id", "count"),
            successful_transactions=("successful_transactions", "sum"),
            failed_transactions=("failed_transactions", "sum"),
            pending_transactions=("pending_transactions", "sum"),
            total_transaction_value=("amount", "sum")
        )
        .reset_index()
    )

    hourly["failure_rate_percentage"] = (
        hourly["failed_transactions"]
        / hourly["total_transactions"] * 100
    ).round(2)

    hourly["success_rate_percentage"] = (
        hourly["successful_transactions"]
        / hourly["total_transactions"] * 100
    ).round(2)

    hourly["total_transaction_value"] = (
        hourly["total_transaction_value"].round(2)
    )

    return hourly.sort_values("transaction_hour")


# --------------------------------------------------
# 4. DAY-OF-WEEK ANALYSIS
# --------------------------------------------------

def generate_weekday_analysis(df):

    data = df.copy()

    data["successful_transactions"] = (
        data["status"] == "SUCCESS"
    ).astype(int)

    data["failed_transactions"] = (
        data["status"] == "FAILED"
    ).astype(int)

    data["pending_transactions"] = (
        data["status"] == "PENDING"
    ).astype(int)

    weekday = (
        data.groupby("transaction_day_of_week")
        .agg(
            total_transactions=("transaction_id", "count"),
            successful_transactions=("successful_transactions", "sum"),
            failed_transactions=("failed_transactions", "sum"),
            pending_transactions=("pending_transactions", "sum"),
            total_transaction_value=("amount", "sum")
        )
        .reset_index()
    )

    weekday["failure_rate_percentage"] = (
        weekday["failed_transactions"]
        / weekday["total_transactions"] * 100
    ).round(2)

    weekday["success_rate_percentage"] = (
        weekday["successful_transactions"]
        / weekday["total_transactions"] * 100
    ).round(2)

    weekday["total_transaction_value"] = (
        weekday["total_transaction_value"].round(2)
    )

    day_order = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]

    weekday["transaction_day_of_week"] = pd.Categorical(
        weekday["transaction_day_of_week"],
        categories=day_order,
        ordered=True
    )

    return weekday.sort_values("transaction_day_of_week")


# --------------------------------------------------
# 5. SAVE OUTPUTS
# --------------------------------------------------

def save_outputs(outputs):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for filename, data in outputs.items():

        output_file = OUTPUT_DIR / filename

        data.to_csv(output_file, index=False)

        print(f"Generated: {output_file}")


# --------------------------------------------------
# 6. EXECUTION
# --------------------------------------------------

def run_time_analysis():

    print("\n" + "=" * 55)
    print("FINTECH 360 - UPI TIME ANALYSIS")
    print("=" * 55)

    df = load_data()

    outputs = {
        "upi_hourly_analysis.csv":
            generate_hourly_analysis(df),

        "upi_weekday_analysis.csv":
            generate_weekday_analysis(df)
    }

    # Reconcile analytical totals with source data
    for filename, result in outputs.items():

        if result["total_transactions"].sum() != len(df):
            raise ValueError(
                f"Transaction count reconciliation failed: {filename}"
            )

    save_outputs(outputs)

    print("\nHOURLY TRANSACTION ANALYSIS")
    print("-" * 55)
    print(outputs["upi_hourly_analysis.csv"].to_string(index=False))

    print("\nDAY-OF-WEEK ANALYSIS")
    print("-" * 55)
    print(outputs["upi_weekday_analysis.csv"].to_string(index=False))

    print("\nUPI TIME ANALYSIS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    run_time_analysis()
