
import sys
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "raw" / "mutual_funds"

INVESTORS_FILE = DATA_DIR / "mutual_fund_investors.csv"
SCHEMES_FILE = DATA_DIR / "mutual_fund_schemes.csv"
TRANSACTIONS_FILE = DATA_DIR / "mutual_fund_transactions.csv"
NAV_FILE = DATA_DIR / "mutual_fund_nav_history.csv"


# --------------------------------------------------
# 2. EXPECTED DATASET SCHEMAS
# --------------------------------------------------

EXPECTED_COLUMNS = {
    "investors": [
        "investor_id",
        "investor_name",
        "age",
        "gender",
        "city",
        "registration_date",
        "investor_segment"
    ],
    "schemes": [
        "scheme_id",
        "scheme_name",
        "fund_house",
        "fund_category",
        "risk_level",
        "benchmark",
        "expense_ratio",
        "launch_date"
    ],
    "transactions": [
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
    ],
    "nav": [
        "nav_id",
        "scheme_id",
        "nav_date",
        "nav_value"
    ]
}


# --------------------------------------------------
# 3. VALIDATION REPORT HELPER
# --------------------------------------------------

validation_results = []


def record_check(check_name, passed, details=""):

    status = "PASSED" if passed else "FAILED"

    validation_results.append({
        "check": check_name,
        "passed": passed,
        "details": details
    })

    message = f"{check_name}: {status}"

    if details:
        message += f" | {details}"

    print(message)


# --------------------------------------------------
# 4. LOAD DATASETS
# --------------------------------------------------

def load_datasets():

    files = {
        "investors": INVESTORS_FILE,
        "schemes": SCHEMES_FILE,
        "transactions": TRANSACTIONS_FILE,
        "nav": NAV_FILE
    }

    datasets = {}

    for name, file_path in files.items():

        if not file_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {file_path}"
            )

        datasets[name] = pd.read_csv(
            file_path,
            dtype=str,
            keep_default_na=False
        )

        print(
            f"Loaded {name}: "
            f"{len(datasets[name]):,} records"
        )

    return datasets


# --------------------------------------------------
# 5. VALIDATE REQUIRED COLUMNS
# --------------------------------------------------

def validate_schemas(datasets):

    for name, expected in EXPECTED_COLUMNS.items():

        actual = datasets[name].columns.tolist()

        missing = set(expected) - set(actual)

        record_check(
            f"{name.upper()} REQUIRED COLUMNS",
            len(missing) == 0,
            f"Missing columns: {sorted(missing)}"
        )


# --------------------------------------------------
# 6. VALIDATE PRIMARY KEYS
# --------------------------------------------------

def validate_primary_keys(datasets):

    primary_keys = {
        "investors": "investor_id",
        "schemes": "scheme_id",
        "transactions": "investment_id",
        "nav": "nav_id"
    }

    for name, column in primary_keys.items():

        df = datasets[name]

        if column not in df.columns:
            record_check(
                f"{name.upper()} PRIMARY KEY",
                False,
                f"Column {column} missing"
            )
            continue

        values = df[column].astype(str).str.strip()

        missing_count = values.eq("").sum()
        duplicate_count = values.duplicated().sum()

        passed = (
            missing_count == 0
            and duplicate_count == 0
        )

        record_check(
            f"{name.upper()} PRIMARY KEY",
            passed,
            (
                f"Missing: {missing_count}, "
                f"Duplicates: {duplicate_count}"
            )
        )


# --------------------------------------------------
# 7. VALIDATE REQUIRED FIELD VALUES
# --------------------------------------------------

def validate_required_values(datasets):

    required_fields = {
        "investors": [
            "investor_id",
            "investor_name",
            "age",
            "city",
            "registration_date",
            "investor_segment"
        ],
        "schemes": [
            "scheme_id",
            "scheme_name",
            "fund_house",
            "fund_category",
            "risk_level",
            "launch_date"
        ],
        "transactions": [
            "investment_id",
            "investor_id",
            "scheme_id",
            "transaction_date",
            "transaction_type",
            "investment_mode",
            "amount",
            "nav",
            "units",
            "transaction_status"
        ],
        "nav": [
            "nav_id",
            "scheme_id",
            "nav_date",
            "nav_value"
        ]
    }

    for name, columns in required_fields.items():

        df = datasets[name]

        missing_count = 0

        for column in columns:

            if column not in df.columns:
                missing_count += len(df)
                continue

            missing_count += (
                df[column]
                .astype(str)
                .str.strip()
                .eq("")
                .sum()
            )

        record_check(
            f"{name.upper()} REQUIRED VALUES",
            missing_count == 0,
            f"Missing values: {missing_count}"
        )


# --------------------------------------------------
# 8. VALIDATE NUMERIC FIELDS
# --------------------------------------------------

def validate_numeric_values(datasets):

    investors = datasets["investors"]
    schemes = datasets["schemes"]
    transactions = datasets["transactions"]
    nav = datasets["nav"]

    # Investor age

    age = pd.to_numeric(
        investors["age"],
        errors="coerce"
    )

    record_check(
        "INVESTOR AGE",
        age.notna().all()
        and age.between(18, 100).all(),
        "Age must be between 18 and 100"
    )

    # Scheme expense ratio

    expense_ratio = pd.to_numeric(
        schemes["expense_ratio"],
        errors="coerce"
    )

    record_check(
        "SCHEME EXPENSE RATIO",
        expense_ratio.notna().all()
        and expense_ratio.ge(0).all(),
        "Expense ratio must be numeric and non-negative"
    )

    # Transaction amount

    amount = pd.to_numeric(
        transactions["amount"],
        errors="coerce"
    )

    record_check(
        "TRANSACTION AMOUNT",
        amount.notna().all()
        and amount.gt(0).all(),
        "All amounts must be numeric and positive"
    )

    # Transaction NAV

    transaction_nav = pd.to_numeric(
        transactions["nav"],
        errors="coerce"
    )

    record_check(
        "TRANSACTION NAV",
        transaction_nav.notna().all()
        and transaction_nav.gt(0).all(),
        "All transaction NAV values must be positive"
    )

    # Transaction units

    units = pd.to_numeric(
        transactions["units"],
        errors="coerce"
    )

    record_check(
        "TRANSACTION UNITS",
        units.notna().all()
        and units.gt(0).all(),
        "All transaction units must be positive"
    )

    # Historical NAV

    nav_values = pd.to_numeric(
        nav["nav_value"],
        errors="coerce"
    )

    record_check(
        "HISTORICAL NAV VALUES",
        nav_values.notna().all()
        and nav_values.gt(0).all(),
        "All historical NAV values must be positive"
    )


# --------------------------------------------------
# 9. VALIDATE FOREIGN KEYS
# --------------------------------------------------

def validate_foreign_keys(datasets):

    investors = datasets["investors"]
    schemes = datasets["schemes"]
    transactions = datasets["transactions"]
    nav = datasets["nav"]

    investor_ids = set(investors["investor_id"])
    scheme_ids = set(schemes["scheme_id"])

    invalid_investors = (
        ~transactions["investor_id"].isin(investor_ids)
    ).sum()

    invalid_transaction_schemes = (
        ~transactions["scheme_id"].isin(scheme_ids)
    ).sum()

    invalid_nav_schemes = (
        ~nav["scheme_id"].isin(scheme_ids)
    ).sum()

    record_check(
        "TRANSACTION INVESTOR REFERENCES",
        invalid_investors == 0,
        f"Invalid references: {invalid_investors}"
    )

    record_check(
        "TRANSACTION SCHEME REFERENCES",
        invalid_transaction_schemes == 0,
        f"Invalid references: {invalid_transaction_schemes}"
    )

    record_check(
        "NAV SCHEME REFERENCES",
        invalid_nav_schemes == 0,
        f"Invalid references: {invalid_nav_schemes}"
    )


# --------------------------------------------------
# 10. VALIDATE CATEGORIES AND STATUSES
# --------------------------------------------------

def validate_business_rules(datasets):

    investors = datasets["investors"]
    schemes = datasets["schemes"]
    transactions = datasets["transactions"]

    valid_categories = {
        "EQUITY", "DEBT", "HYBRID", "INDEX"
    }

    valid_risk_levels = {
        "LOW", "MODERATE", "HIGH"
    }

    valid_segments = {
        "RETAIL", "HNI"
    }

    valid_types = {
        "PURCHASE", "REDEMPTION"
    }

    valid_modes = {
        "SIP", "LUMP_SUM", "NOT_APPLICABLE"
    }

    valid_statuses = {
        "SUCCESS", "FAILED"
    }

    category_valid = schemes[
        "fund_category"
    ].isin(valid_categories).all()

    record_check(
        "FUND CATEGORIES",
        category_valid,
        "Allowed: EQUITY, DEBT, HYBRID, INDEX"
    )

    risk_valid = schemes[
        "risk_level"
    ].isin(valid_risk_levels).all()

    record_check(
        "FUND RISK LEVELS",
        risk_valid,
        "Allowed: LOW, MODERATE, HIGH"
    )

    segment_valid = investors[
        "investor_segment"
    ].isin(valid_segments).all()

    record_check(
        "INVESTOR SEGMENTS",
        segment_valid,
        "Allowed: RETAIL, HNI"
    )

    type_valid = transactions[
        "transaction_type"
    ].isin(valid_types).all()

    record_check(
        "TRANSACTION TYPES",
        type_valid,
        "Allowed: PURCHASE, REDEMPTION"
    )

    mode_valid = transactions[
        "investment_mode"
    ].isin(valid_modes).all()

    record_check(
        "INVESTMENT MODES",
        mode_valid,
        "Allowed: SIP, LUMP_SUM, NOT_APPLICABLE"
    )

    status_valid = transactions[
        "transaction_status"
    ].isin(valid_statuses).all()

    record_check(
        "TRANSACTION STATUSES",
        status_valid,
        "Allowed: SUCCESS, FAILED"
    )

    # PURCHASE must have SIP or LUMP_SUM.
    # REDEMPTION must have NOT_APPLICABLE.

    purchase = transactions[
        "transaction_type"
    ].eq("PURCHASE")

    redemption = transactions[
        "transaction_type"
    ].eq("REDEMPTION")

    mode_consistency = (
        transactions.loc[
            purchase, "investment_mode"
        ].isin({"SIP", "LUMP_SUM"}).all()
        and transactions.loc[
            redemption, "investment_mode"
        ].eq("NOT_APPLICABLE").all()
    )

    record_check(
        "TRANSACTION MODE CONSISTENCY",
        mode_consistency,
        "Purchase: SIP/LUMP_SUM; Redemption: NOT_APPLICABLE"
    )


# --------------------------------------------------
# 11. VALIDATE FAILURE REASONS
# --------------------------------------------------

def validate_failure_reasons(transactions):

    failed = transactions[
        transactions["transaction_status"] == "FAILED"
    ]

    successful = transactions[
        transactions["transaction_status"] == "SUCCESS"
    ]

    missing_reasons = failed[
        "failure_reason"
    ].astype(str).str.strip().eq("").sum()

    unexpected_reasons = successful[
        "failure_reason"
    ].astype(str).str.strip().ne("").sum()

    passed = (
        missing_reasons == 0
        and unexpected_reasons == 0
    )

    record_check(
        "FAILURE REASON VALIDATION",
        passed,
        (
            f"Failed without reason: {missing_reasons}, "
            f"Successful with reason: {unexpected_reasons}"
        )
    )


# --------------------------------------------------
# 12. VALIDATE DATE FIELDS
# --------------------------------------------------

def validate_dates(datasets):

    investors = datasets["investors"]
    schemes = datasets["schemes"]
    transactions = datasets["transactions"]
    nav = datasets["nav"]

    registration_dates = pd.to_datetime(
        investors["registration_date"],
        errors="coerce"
    )

    scheme_dates = pd.to_datetime(
        schemes["launch_date"],
        errors="coerce"
    )

    transaction_dates = pd.to_datetime(
        transactions["transaction_date"],
        errors="coerce"
    )

    nav_dates = pd.to_datetime(
        nav["nav_date"],
        errors="coerce"
    )

    record_check(
        "INVESTOR REGISTRATION DATES",
        registration_dates.notna().all(),
        "All registration dates must be valid"
    )

    record_check(
        "SCHEME LAUNCH DATES",
        scheme_dates.notna().all(),
        "All launch dates must be valid"
    )

    record_check(
        "TRANSACTION DATES",
        transaction_dates.notna().all(),
        "All transaction dates must be valid"
    )

    record_check(
        "NAV HISTORY DATES",
        nav_dates.notna().all(),
        "All NAV dates must be valid"
    )

    # Transaction must occur after investor registration.

    investor_registration = investors[
        ["investor_id", "registration_date"]
    ].copy()

    investor_registration["registration_date"] = (
        pd.to_datetime(
            investor_registration["registration_date"],
            errors="coerce"
        )
    )

    transaction_check = transactions[
        ["investor_id", "transaction_date"]
    ].copy()

    transaction_check["transaction_date"] = (
        pd.to_datetime(
            transaction_check["transaction_date"],
            errors="coerce"
        )
    )

    merged = transaction_check.merge(
        investor_registration,
        on="investor_id",
        how="left"
    )

    invalid_registration_dates = (
        merged["transaction_date"]
        < merged["registration_date"]
    ).sum()

    record_check(
        "TRANSACTION AFTER REGISTRATION",
        invalid_registration_dates == 0,
        f"Invalid transactions: {invalid_registration_dates}"
    )

    # Transaction must occur after scheme launch.

    scheme_launch = schemes[
        ["scheme_id", "launch_date"]
    ].copy()

    scheme_launch["launch_date"] = pd.to_datetime(
        scheme_launch["launch_date"],
        errors="coerce"
    )

    scheme_transaction = transactions[
        ["scheme_id", "transaction_date"]
    ].copy()

    scheme_transaction["transaction_date"] = pd.to_datetime(
        scheme_transaction["transaction_date"],
        errors="coerce"
    )

    merged = scheme_transaction.merge(
        scheme_launch,
        on="scheme_id",
        how="left"
    )

    invalid_launch_dates = (
        merged["transaction_date"]
        < merged["launch_date"]
    ).sum()

    record_check(
        "TRANSACTION AFTER SCHEME LAUNCH",
        invalid_launch_dates == 0,
        f"Invalid transactions: {invalid_launch_dates}"
    )


# --------------------------------------------------
# 13. VALIDATE NAV UNIQUENESS
# --------------------------------------------------

def validate_nav_uniqueness(nav):

    duplicate_count = nav.duplicated(
        subset=["scheme_id", "nav_date"]
    ).sum()

    record_check(
        "SCHEME NAV DATE UNIQUENESS",
        duplicate_count == 0,
        f"Duplicate scheme/date combinations: {duplicate_count}"
    )


# --------------------------------------------------
# 14. VALIDATE TRANSACTION NAV MATCHING
# --------------------------------------------------

def validate_transaction_nav(datasets):

    transactions = datasets["transactions"].copy()
    nav = datasets["nav"].copy()

    transactions["transaction_date"] = pd.to_datetime(
        transactions["transaction_date"],
        errors="coerce"
    )

    nav["nav_date"] = pd.to_datetime(
        nav["nav_date"],
        errors="coerce"
    )

    transactions["nav"] = pd.to_numeric(
        transactions["nav"],
        errors="coerce"
    )

    nav["nav_value"] = pd.to_numeric(
        nav["nav_value"],
        errors="coerce"
    )

    merged = transactions.merge(
        nav[
            ["scheme_id", "nav_date", "nav_value"]
        ],
        left_on=["scheme_id", "transaction_date"],
        right_on=["scheme_id", "nav_date"],
        how="left"
    )

    missing_nav = merged["nav_value"].isna().sum()

    mismatch = (
        (merged["nav"] - merged["nav_value"]).abs()
        > 0.00001
    ).sum()

    record_check(
        "TRANSACTION NAV MATCHING",
        missing_nav == 0 and mismatch == 0,
        (
            f"Missing NAV matches: {missing_nav}, "
            f"NAV mismatches: {mismatch}"
        )
    )


# --------------------------------------------------
# 15. VALIDATE FINANCIAL CALCULATIONS
# --------------------------------------------------

def validate_financial_calculations(transactions):

    amount = pd.to_numeric(
        transactions["amount"],
        errors="coerce"
    )

    nav = pd.to_numeric(
        transactions["nav"],
        errors="coerce"
    )

    units = pd.to_numeric(
        transactions["units"],
        errors="coerce"
    )

    calculated_amount = units * nav

    difference = (
        amount - calculated_amount
    ).abs()

    invalid_count = (
        difference > 0.02
    ).sum()

    record_check(
        "AMOUNT NAV UNITS CONSISTENCY",
        invalid_count == 0,
        f"Calculation mismatches: {invalid_count}"
    )


# --------------------------------------------------
# 16. VALIDATE TRANSACTION HOLDINGS
# --------------------------------------------------

def validate_holdings(transactions):

    df = transactions.copy()

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

    df["units"] = pd.to_numeric(
        df["units"],
        errors="coerce"
    )

    df = df.sort_values(
        ["transaction_date", "investment_id"]
    )

    holdings = {}

    invalid_redemptions = 0

    for row in df.itertuples(index=False):

        # Failed transactions do not affect holdings.

        if row.transaction_status != "SUCCESS":
            continue

        key = (
            row.investor_id,
            row.scheme_id
        )

        available_units = holdings.get(key, 0.0)

        if row.transaction_type == "PURCHASE":

            holdings[key] = (
                available_units + row.units
            )

        elif row.transaction_type == "REDEMPTION":

            if row.units > available_units + 0.000001:

                invalid_redemptions += 1

            else:

                holdings[key] = max(
                    0.0,
                    available_units - row.units
                )

    record_check(
        "SUCCESSFUL REDEMPTION HOLDINGS",
        invalid_redemptions == 0,
        f"Invalid redemptions: {invalid_redemptions}"
    )


# --------------------------------------------------
# 17. FINAL VALIDATION SUMMARY
# --------------------------------------------------

def print_summary():

    total_checks = len(validation_results)

    passed_checks = sum(
        result["passed"]
        for result in validation_results
    )

    failed_checks = total_checks - passed_checks

    print("\n" + "=" * 65)
    print("MUTUAL FUNDS DATA QUALITY SUMMARY")
    print("=" * 65)

    print(f"Total checks : {total_checks}")
    print(f"Passed       : {passed_checks}")
    print(f"Failed       : {failed_checks}")

    print("=" * 65)

    if failed_checks == 0:

        print(
            "ALL MUTUAL FUNDS DATA QUALITY CHECKS PASSED!"
        )

    else:

        print("FAILED VALIDATION CHECKS:")

        for result in validation_results:

            if not result["passed"]:
                print(f"- {result['check']}: {result['details']}")


# --------------------------------------------------
# 18. MAIN EXECUTION
# --------------------------------------------------

def main():

    print("=" * 65)
    print("FINTECH 360 - MUTUAL FUNDS DATA QUALITY VALIDATION")
    print("=" * 65)

    try:

        datasets = load_datasets()

        print("\nStarting validation...\n")

        validate_schemas(datasets)

        # Stop further checks if required columns are missing.

        if not all(
            result["passed"]
            for result in validation_results
        ):
            print_summary()
            raise SystemExit(1)

        validate_primary_keys(datasets)

        validate_required_values(datasets)

        validate_numeric_values(datasets)

        validate_foreign_keys(datasets)

        validate_business_rules(datasets)

        validate_failure_reasons(
            datasets["transactions"]
        )

        validate_dates(datasets)

        validate_nav_uniqueness(
            datasets["nav"]
        )

        validate_transaction_nav(datasets)

        validate_financial_calculations(
            datasets["transactions"]
        )

        validate_holdings(
            datasets["transactions"]
        )

        print_summary()

        failed_checks = sum(
            not result["passed"]
            for result in validation_results
        )

        if failed_checks > 0:
            raise SystemExit(1)

    except FileNotFoundError as error:

        print(f"\nDATASET ERROR: {error}")
        raise SystemExit(1)

    except Exception as error:

        print(f"\nVALIDATION ERROR: {error}")
        raise SystemExit(1)


# --------------------------------------------------
# 19. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()
