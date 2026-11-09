
"""
FINTECH 360 - UPI Failure Analysis

Analyzes:
1. Failure reason distribution
2. Bank-wise failure performance
3. Payment-app-wise failure performance
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
# 2. LOAD AND VALIDATE DATA
# --------------------------------------------------

def load_data():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "transaction_id",
        "amount",
        "status",
        "failure_reason",
        "payer_bank",
        "payment_app"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["status"] = df["status"].astype("string").str.upper().str.strip()

    if df["amount"].isna().any():
        raise ValueError("Invalid transaction amounts found.")

    failed = df[df["status"] == "FAILED"]

    if failed["failure_reason"].isna().any():
        raise ValueError("Failed transactions have missing failure reasons.")

    if (df["amount"] < 0).any():
        raise ValueError("Negative transaction amounts found.")

    print(f"Records loaded: {len(df)}")
    print(f"Failed transactions: {len(failed)}")

    return df


# --------------------------------------------------
# 3. FAILURE REASON ANALYSIS
# --------------------------------------------------

def generate_failure_reason_analysis(df):

    failed = df[df["status"] == "FAILED"].copy()

    analysis = (
        failed.groupby("failure_reason")
        .agg(
            failed_transactions=("transaction_id", "count"),
            failed_transaction_value=("amount", "sum")
        )
        .reset_index()
    )

    total_failures = len(failed)

    analysis["failure_percentage"] = (
        analysis["failed_transactions"]
        / total_failures * 100
    ).round(2)

    analysis["failed_transaction_value"] = (
        analysis["failed_transaction_value"].round(2)
    )

    return analysis.sort_values(
        "failed_transactions", ascending=False
    )


# --------------------------------------------------
# 4. BANK / APP FAILURE ANALYSIS
# --------------------------------------------------

def generate_dimension_failure_analysis(df, dimension):

    data = df.copy()

    data["failed_transaction"] = (
        data["status"] == "FAILED"
    ).astype(int)

    data["failed_amount"] = data["amount"].where(
        data["status"] == "FAILED", 0
    )

    analysis = (
        data.groupby(dimension, dropna=False)
        .agg(
            total_transactions=("transaction_id", "count"),
            failed_transactions=("failed_transaction", "sum"),
            failed_transaction_value=("failed_amount", "sum")
        )
        .reset_index()
    )

    analysis["failure_rate_percentage"] = (
        analysis["failed_transactions"]
        / analysis["total_transactions"] * 100
    ).round(2)

    analysis["failed_transaction_value"] = (
        analysis["failed_transaction_value"].round(2)
    )

    return analysis.sort_values(
        "failure_rate_percentage", ascending=False
    )


# --------------------------------------------------
# 5. SAVE ANALYTICAL OUTPUTS
# --------------------------------------------------

def save_outputs(outputs):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for file_name, data in outputs.items():

        output_file = OUTPUT_DIR / file_name

        data.to_csv(output_file, index=False)

        print(f"Generated: {output_file}")


# --------------------------------------------------
# 6. EXECUTION
# --------------------------------------------------

def run_failure_analysis():

    print("\n" + "=" * 55)
    print("FINTECH 360 - UPI FAILURE ANALYSIS")
    print("=" * 55)

    df = load_data()

    outputs = {
        "upi_failure_reason_analysis.csv":
            generate_failure_reason_analysis(df),

        "upi_bank_failure_analysis.csv":
            generate_dimension_failure_analysis(
                df, "payer_bank"
            ),

        "upi_app_failure_analysis.csv":
            generate_dimension_failure_analysis(
                df, "payment_app"
            )
    }

    # Reconciliation check
    total_failed = (df["status"] == "FAILED").sum()

    analyzed_failed = outputs[
        "upi_failure_reason_analysis.csv"
    ]["failed_transactions"].sum()

    if total_failed != analyzed_failed:
        raise ValueError("Failure analysis reconciliation failed.")

    save_outputs(outputs)

    print("\nFAILURE REASON ANALYSIS")
    print("-" * 55)
    print(outputs["upi_failure_reason_analysis.csv"].to_string(index=False))

    print("\nBANK FAILURE ANALYSIS")
    print("-" * 55)
    print(outputs["upi_bank_failure_analysis.csv"].to_string(index=False))

    print("\nPAYMENT APP FAILURE ANALYSIS")
    print("-" * 55)
    print(outputs["upi_app_failure_analysis.csv"].to_string(index=False))

    print("\nUPI FAILURE ANALYSIS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    run_failure_analysis()
