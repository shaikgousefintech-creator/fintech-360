
"""
FINTECH 360 - UPI Analytics Pipeline

Reads curated UPI transaction data and generates:
1. Overall business KPIs
2. Daily transaction trends
3. Payment app performance
4. Payer bank performance
"""

from pathlib import Path
import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "data" / "curated" / "upi"
OUTPUT_DIR = PROJECT_ROOT / "data" / "warehouse" / "upi"


# --------------------------------------------------
# 2. LOAD CURATED DATA
# --------------------------------------------------

def load_curated_data():

    files = sorted(INPUT_DIR.glob("*.csv"))

    if not files:
        raise FileNotFoundError(
            f"No curated UPI CSV files found in {INPUT_DIR}"
        )

    input_file = files[-1]

    df = pd.read_csv(input_file)

    print(f"Input file: {input_file}")
    print(f"Records loaded: {len(df)}")

    required_columns = [
        "transaction_id",
        "amount",
        "status",
        "transaction_date",
        "payment_app",
        "payer_bank"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    df["amount"] = pd.to_numeric(
        df["amount"], errors="coerce"
    )

    df["status"] = (
        df["status"].astype("string").str.upper().str.strip()
    )

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], errors="coerce"
    ).dt.date

    if df["amount"].isna().any():
        raise ValueError("Invalid or missing transaction amounts found.")

    if df["transaction_date"].isna().any():
        raise ValueError("Invalid transaction dates found.")

    return df


# --------------------------------------------------
# 3. GENERATE OVERALL BUSINESS KPIs
# --------------------------------------------------

def generate_overall_kpis(df):

    total_transactions = len(df)

    successful = (df["status"] == "SUCCESS").sum()
    failed = (df["status"] == "FAILED").sum()
    pending = (df["status"] == "PENDING").sum()

    total_value = df["amount"].sum()

    successful_value = df.loc[
        df["status"] == "SUCCESS", "amount"
    ].sum()

    average_amount = df["amount"].mean()

    success_rate = (
        successful / total_transactions * 100
        if total_transactions else 0
    )

    failure_rate = (
        failed / total_transactions * 100
        if total_transactions else 0
    )

    pending_rate = (
        pending / total_transactions * 100
        if total_transactions else 0
    )

    kpis = {
        "total_transactions": total_transactions,
        "successful_transactions": successful,
        "failed_transactions": failed,
        "pending_transactions": pending,
        "total_transaction_value": round(total_value, 2),
        "successful_transaction_value": round(successful_value, 2),
        "average_transaction_amount": round(average_amount, 2),
        "success_rate_percentage": round(success_rate, 2),
        "failure_rate_percentage": round(failure_rate, 2),
        "pending_rate_percentage": round(pending_rate, 2)
    }

    return pd.DataFrame(
        list(kpis.items()),
        columns=["metric", "value"]
    )


# --------------------------------------------------
# 4. GENERATE DAILY TRANSACTION TRENDS
# --------------------------------------------------

def generate_daily_trends(df):

    daily = (
        df.groupby("transaction_date")
        .agg(
            total_transactions=("transaction_id", "count"),
            successful_transactions=(
                "status", lambda x: (x == "SUCCESS").sum()
            ),
            failed_transactions=(
                "status", lambda x: (x == "FAILED").sum()
            ),
            pending_transactions=(
                "status", lambda x: (x == "PENDING").sum()
            ),
            total_transaction_value=("amount", "sum")
        )
        .reset_index()
    )

    daily["success_rate_percentage"] = (
        daily["successful_transactions"]
        / daily["total_transactions"] * 100
    ).round(2)

    daily["total_transaction_value"] = (
        daily["total_transaction_value"].round(2)
    )

    return daily.sort_values("transaction_date")


# --------------------------------------------------
# 5. GENERATE DIMENSION PERFORMANCE
# --------------------------------------------------

def generate_dimension_performance(df, dimension):

    data = df.copy()

    data["successful_amount"] = data["amount"].where(
        data["status"] == "SUCCESS", 0
    )

    performance = (
        data.groupby(dimension, dropna=False)
        .agg(
            total_transactions=("transaction_id", "count"),
            successful_transactions=(
                "status", lambda x: (x == "SUCCESS").sum()
            ),
            failed_transactions=(
                "status", lambda x: (x == "FAILED").sum()
            ),
            pending_transactions=(
                "status", lambda x: (x == "PENDING").sum()
            ),
            total_transaction_value=("amount", "sum"),
            successful_transaction_value=(
                "successful_amount", "sum"
            )
        )
        .reset_index()
    )

    performance["success_rate_percentage"] = (
        performance["successful_transactions"]
        / performance["total_transactions"] * 100
    ).round(2)

    performance["total_transaction_value"] = (
        performance["total_transaction_value"].round(2)
    )

    performance["successful_transaction_value"] = (
        performance["successful_transaction_value"].round(2)
    )

    return performance.sort_values(
        "total_transactions", ascending=False
    )


# --------------------------------------------------
# 6. SAVE ANALYTICAL OUTPUTS
# --------------------------------------------------

def save_analytics(outputs):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for file_name, data in outputs.items():

        output_file = OUTPUT_DIR / file_name

        data.to_csv(output_file, index=False)

        print(f"Generated: {output_file}")


# --------------------------------------------------
# 7. EXECUTION ENTRY POINT
# --------------------------------------------------

def run_analytics():

    print("\n" + "=" * 50)
    print("FINTECH 360 - UPI ANALYTICS PIPELINE")
    print("=" * 50)

    df = load_curated_data()

    outputs = {
        "upi_overall_kpis.csv":
            generate_overall_kpis(df),

        "upi_daily_trends.csv":
            generate_daily_trends(df),

        "upi_payment_app_performance.csv":
            generate_dimension_performance(
                df, "payment_app"
            ),

        "upi_payer_bank_performance.csv":
            generate_dimension_performance(
                df, "payer_bank"
            )
    }

    save_analytics(outputs)

    print("\nOVERALL UPI KPIs")
    print("-" * 50)

    print(outputs["upi_overall_kpis.csv"].to_string(index=False))

    print("\nTOP PAYMENT APPS")
    print("-" * 50)

    print(
        outputs["upi_payment_app_performance.csv"]
        .head(5).to_string(index=False)
    )

    print("\nUPI ANALYTICS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    run_analytics()
