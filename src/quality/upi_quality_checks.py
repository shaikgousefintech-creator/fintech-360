
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "upi"
    / "upi_transactions.csv"
)


def validate_upi_data(df):

    checks = {}

    # 1. Required columns
    required_columns = [
        "transaction_id",
        "payer_id",
        "payee_id",
        "transaction_type",
        "amount",
        "currency",
        "transaction_timestamp",
        "status",
        "failure_reason",
        "merchant_name",
    ]

    checks["Required columns present"] = all(
        col in df.columns for col in required_columns
    )

    if not checks["Required columns present"]:
        return checks

    # 2. Transaction ID uniqueness
    checks["Unique transaction IDs"] = (
        df["transaction_id"].notna().all()
        and df["transaction_id"].is_unique
    )

    # 3. Positive transaction amounts
    amounts = pd.to_numeric(df["amount"], errors="coerce")

    checks["Valid transaction amounts"] = (
        amounts.notna().all() and (amounts > 0).all()
    )

    # 4. Valid timestamps
    timestamps = pd.to_datetime(
        df["transaction_timestamp"],
        format="%Y-%m-%d %H:%M:%S.%f",
        errors="coerce"
    )

    checks["Valid timestamps"] = timestamps.notna().all()

    # 5. Valid transaction statuses
    valid_statuses = {"SUCCESS", "FAILED", "PENDING"}

    checks["Valid transaction statuses"] = (
        df["status"].isin(valid_statuses).all()
    )

    # 6. Failed transactions must have a reason
    failed = df["status"] == "FAILED"

    checks["Failed transactions have reasons"] = (
    df.loc[failed, "failure_reason"]
    .astype("string")
    .str.strip()
    .ne("")
    .fillna(False)
    .all()
   )

    # 7. P2M transactions must have merchant names
    p2m = df["transaction_type"] == "P2M"

    checks["P2M transactions have merchant names"] = (
    df.loc[p2m, "merchant_name"].notna().all()
    and df.loc[p2m, "merchant_name"].astype("string").str.strip().ne("").all()
   )

    # 8. Valid transaction types
    valid_types = {"P2P", "P2M"}

    checks["Valid transaction types"] = (
        df["transaction_type"].isin(valid_types).all()
    )

    # 9. Required identifiers
    checks["No missing transaction identifiers"] = (
    df[["transaction_id", "payer_id", "payee_id"]]
    .astype("string")
    .apply(lambda col: col.str.strip().ne(""))
    .fillna(False)
    .all()
    .all()
)

    # 10. Valid currency
    checks["Valid currency"] = (
        df["currency"].eq("INR").all()
    )

    return checks


def main():

    print("Starting UPI data quality validation...\n")

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    results = validate_upi_data(df)

    passed = sum(results.values())
    total = len(results)

    for check_name, result in results.items():

        status = "PASS" if result else "FAIL"

        print(f"[{status}] {check_name}")

    print("\nData Quality Report")
    print("-------------------")
    print(f"Total records: {len(df)}")
    print(f"Passed checks: {passed}")
    print(f"Failed checks: {total - passed}")

    if passed == total:
        print("\nUPI DATA QUALITY VALIDATION SUCCESSFUL!")
    else:
        print("\nUPI DATA QUALITY VALIDATION FAILED!")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
