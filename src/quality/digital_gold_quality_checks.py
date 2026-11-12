
import sys
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "raw" / "digital_gold"

CUSTOMERS_FILE = DATA_DIR / "digital_gold_customers.csv"
PRICE_FILE = DATA_DIR / "digital_gold_price_history.csv"
TRANSACTIONS_FILE = DATA_DIR / "digital_gold_transactions.csv"
LEDGER_FILE = DATA_DIR / "digital_gold_wallet_ledger.csv"


# --------------------------------------------------
# 2. EXPECTED DATASET SCHEMAS
# --------------------------------------------------

EXPECTED_COLUMNS = {
    "customers": [
        "customer_id",
        "customer_name",
        "age",
        "gender",
        "city",
        "registration_date",
        "customer_segment"
    ],
    "price_history": [
        "price_id",
        "price_date",
        "gold_price_per_gram",
        "buy_price_per_gram",
        "sell_price_per_gram"
    ],
    "transactions": [
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
    ],
    "wallet_ledger": [
        "ledger_id",
        "customer_id",
        "transaction_id",
        "entry_date",
        "transaction_type",
        "gold_quantity_grams",
        "balance_after_grams"
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
        "customers": CUSTOMERS_FILE,
        "price_history": PRICE_FILE,
        "transactions": TRANSACTIONS_FILE,
        "wallet_ledger": LEDGER_FILE
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
        "customers": "customer_id",
        "price_history": "price_id",
        "transactions": "transaction_id",
        "wallet_ledger": "ledger_id"
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
        "customers": [
            "customer_id",
            "customer_name",
            "age",
            "city",
            "registration_date",
            "customer_segment"
        ],
        "price_history": [
            "price_id",
            "price_date",
            "gold_price_per_gram",
            "buy_price_per_gram",
            "sell_price_per_gram"
        ],
        "transactions": [
            "transaction_id",
            "customer_id",
            "transaction_date",
            "transaction_type",
            "investment_mode",
            "gold_quantity_grams",
            "gold_price_per_gram",
            "amount",
            "transaction_status"
        ],
        "wallet_ledger": [
            "ledger_id",
            "customer_id",
            "transaction_id",
            "entry_date",
            "transaction_type",
            "gold_quantity_grams",
            "balance_after_grams"
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

    customers = datasets["customers"]
    prices = datasets["price_history"]
    transactions = datasets["transactions"]
    ledger = datasets["wallet_ledger"]

    # Customer age

    age = pd.to_numeric(
        customers["age"],
        errors="coerce"
    )

    record_check(
        "CUSTOMER AGE",
        age.notna().all()
        and age.between(18, 100).all(),
        "Age must be numeric and between 18 and 100"
    )

    # Gold price values

    for column in [
        "gold_price_per_gram",
        "buy_price_per_gram",
        "sell_price_per_gram"
    ]:

        values = pd.to_numeric(
            prices[column],
            errors="coerce"
        )

        record_check(
            f"GOLD PRICE - {column.upper()}",
            values.notna().all()
            and values.gt(0).all(),
            "All gold prices must be numeric and positive"
        )

    # Transaction numeric fields

    for column in [
        "gold_quantity_grams",
        "gold_price_per_gram",
        "amount"
    ]:

        values = pd.to_numeric(
            transactions[column],
            errors="coerce"
        )

        record_check(
            f"TRANSACTION - {column.upper()}",
            values.notna().all()
            and values.gt(0).all(),
            "All values must be numeric and positive"
        )

    # Wallet ledger numeric fields

    for column in [
        "gold_quantity_grams",
        "balance_after_grams"
    ]:

        values = pd.to_numeric(
            ledger[column],
            errors="coerce"
        )

        record_check(
            f"WALLET LEDGER - {column.upper()}",
            values.notna().all()
            and values.gt(0).all(),
            "All values must be numeric and positive"
        )


# --------------------------------------------------
# 9. VALIDATE FOREIGN KEYS
# --------------------------------------------------

def validate_foreign_keys(datasets):

    customers = datasets["customers"]
    transactions = datasets["transactions"]
    ledger = datasets["wallet_ledger"]

    customer_ids = set(customers["customer_id"])

    transaction_ids = set(
        transactions["transaction_id"]
    )

    invalid_transaction_customers = (
        ~transactions["customer_id"].isin(customer_ids)
    ).sum()

    invalid_ledger_customers = (
        ~ledger["customer_id"].isin(customer_ids)
    ).sum()

    invalid_ledger_transactions = (
        ~ledger["transaction_id"].isin(transaction_ids)
    ).sum()

    record_check(
        "TRANSACTION CUSTOMER REFERENCES",
        invalid_transaction_customers == 0,
        f"Invalid references: {invalid_transaction_customers}"
    )

    record_check(
        "LEDGER CUSTOMER REFERENCES",
        invalid_ledger_customers == 0,
        f"Invalid references: {invalid_ledger_customers}"
    )

    record_check(
        "LEDGER TRANSACTION REFERENCES",
        invalid_ledger_transactions == 0,
        f"Invalid references: {invalid_ledger_transactions}"
    )


# --------------------------------------------------
# 10. VALIDATE BUSINESS RULES
# --------------------------------------------------

def validate_business_rules(datasets):

    customers = datasets["customers"]
    transactions = datasets["transactions"]
    ledger = datasets["wallet_ledger"]

    valid_genders = {
        "MALE", "FEMALE", "OTHER"
    }

    valid_segments = {
        "REGULAR", "PREMIUM"
    }

    valid_transaction_types = {
        "BUY", "SELL"
    }

    valid_modes = {
        "UPI",
        "BANK_TRANSFER",
        "CARD",
        "WALLET"
    }

    valid_statuses = {
        "SUCCESS", "FAILED", "PENDING"
    }

    valid_ledger_types = {
        "CREDIT", "DEBIT"
    }

    record_check(
        "CUSTOMER GENDERS",
        customers["gender"].isin(valid_genders).all(),
        "Allowed: MALE, FEMALE, OTHER"
    )

    record_check(
        "CUSTOMER SEGMENTS",
        customers["customer_segment"].isin(valid_segments).all(),
        "Allowed: REGULAR, PREMIUM"
    )

    record_check(
        "TRANSACTION TYPES",
        transactions["transaction_type"].isin(
            valid_transaction_types
        ).all(),
        "Allowed: BUY, SELL"
    )

    record_check(
        "INVESTMENT MODES",
        transactions["investment_mode"].isin(
            valid_modes
        ).all(),
        "Allowed: UPI, BANK_TRANSFER, CARD, WALLET"
    )

    record_check(
        "TRANSACTION STATUSES",
        transactions["transaction_status"].isin(
            valid_statuses
        ).all(),
        "Allowed: SUCCESS, FAILED, PENDING"
    )

    record_check(
        "WALLET LEDGER TYPES",
        ledger["transaction_type"].isin(
            valid_ledger_types
        ).all(),
        "Allowed: CREDIT, DEBIT"
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

    pending = transactions[
        transactions["transaction_status"] == "PENDING"
    ]

    missing_reasons = (
        failed["failure_reason"]
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

    unexpected_reasons = (
        successful["failure_reason"]
        .astype(str)
        .str.strip()
        .ne("")
        .sum()
    )

    invalid_pending_reasons = (
        pending["failure_reason"]
        .astype(str)
        .str.strip()
        .ne("PAYMENT_PENDING")
        .sum()
    )

    passed = (
        missing_reasons == 0
        and unexpected_reasons == 0
        and invalid_pending_reasons == 0
    )

    record_check(
        "FAILURE REASON VALIDATION",
        passed,
        (
            f"Failed without reason: {missing_reasons}, "
            f"Successful with reason: {unexpected_reasons}, "
            f"Invalid pending reasons: {invalid_pending_reasons}"
        )
    )


# --------------------------------------------------
# 12. VALIDATE DATE FIELDS
# --------------------------------------------------

def validate_dates(datasets):

    customers = datasets["customers"]
    prices = datasets["price_history"]
    transactions = datasets["transactions"]
    ledger = datasets["wallet_ledger"]

    registration_dates = pd.to_datetime(
        customers["registration_date"],
        errors="coerce"
    )

    price_dates = pd.to_datetime(
        prices["price_date"],
        errors="coerce"
    )

    transaction_dates = pd.to_datetime(
        transactions["transaction_date"],
        errors="coerce"
    )

    ledger_dates = pd.to_datetime(
        ledger["entry_date"],
        errors="coerce"
    )

    record_check(
        "CUSTOMER REGISTRATION DATES",
        registration_dates.notna().all(),
        "All registration dates must be valid"
    )

    record_check(
        "GOLD PRICE HISTORY DATES",
        price_dates.notna().all(),
        "All price history dates must be valid"
    )

    record_check(
        "TRANSACTION DATES",
        transaction_dates.notna().all(),
        "All transaction dates must be valid"
    )

    record_check(
        "WALLET LEDGER DATES",
        ledger_dates.notna().all(),
        "All ledger dates must be valid"
    )

    # Transactions must occur after customer registration.

    customer_registration = customers[
        ["customer_id", "registration_date"]
    ].copy()

    customer_registration["registration_date"] = (
        pd.to_datetime(
            customer_registration["registration_date"],
            errors="coerce"
        )
    )

    transaction_check = transactions[
        ["customer_id", "transaction_date"]
    ].copy()

    transaction_check["transaction_date"] = (
        pd.to_datetime(
            transaction_check["transaction_date"],
            errors="coerce"
        )
    )

    merged = transaction_check.merge(
        customer_registration,
        on="customer_id",
        how="left"
    )

    invalid_registration_dates = (
        merged["transaction_date"]
        < merged["registration_date"]
    ).sum()

    record_check(
        "TRANSACTION AFTER CUSTOMER REGISTRATION",
        invalid_registration_dates == 0,
        f"Invalid transactions: {invalid_registration_dates}"
    )

    # Ledger date must match its transaction date.

    transaction_dates_lookup = transactions[
        ["transaction_id", "transaction_date"]
    ].copy()

    ledger_date_check = ledger[
        ["transaction_id", "entry_date"]
    ].merge(
        transaction_dates_lookup,
        on="transaction_id",
        how="left"
    )

    invalid_ledger_dates = (
        pd.to_datetime(
            ledger_date_check["entry_date"],
            errors="coerce"
        )
        != pd.to_datetime(
            ledger_date_check["transaction_date"],
            errors="coerce"
        )
    ).sum()

    record_check(
        "WALLET LEDGER TRANSACTION DATES",
        invalid_ledger_dates == 0,
        f"Date mismatches: {invalid_ledger_dates}"
    )


# --------------------------------------------------
# 13. VALIDATE PRICE HISTORY UNIQUENESS
# --------------------------------------------------

def validate_price_uniqueness(price_history):

    duplicate_count = price_history.duplicated(
        subset=["price_date"]
    ).sum()

    record_check(
        "GOLD PRICE DATE UNIQUENESS",
        duplicate_count == 0,
        f"Duplicate price dates: {duplicate_count}"
    )


# --------------------------------------------------
# 14. VALIDATE TRANSACTION GOLD PRICE MATCHING
# --------------------------------------------------

def validate_transaction_prices(datasets):

    transactions = datasets["transactions"].copy()
    prices = datasets["price_history"].copy()

    transactions["transaction_date"] = pd.to_datetime(
        transactions["transaction_date"],
        errors="coerce"
    )

    prices["price_date"] = pd.to_datetime(
        prices["price_date"],
        errors="coerce"
    )

    for column in [
        "gold_price_per_gram",
        "buy_price_per_gram",
        "sell_price_per_gram"
    ]:
        prices[column] = pd.to_numeric(
            prices[column],
            errors="coerce"
        )

    transactions["gold_price_per_gram"] = pd.to_numeric(
        transactions["gold_price_per_gram"],
        errors="coerce"
    )

    merged = transactions.merge(
        prices[
            [
                "price_date",
                "buy_price_per_gram",
                "sell_price_per_gram"
            ]
        ],
        left_on="transaction_date",
        right_on="price_date",
        how="left"
    )

    expected_price = merged["buy_price_per_gram"].where(
        merged["transaction_type"] == "BUY",
        merged["sell_price_per_gram"]
    )

    missing_prices = merged["price_date"].isna().sum()

    mismatches = (
        (
            merged["gold_price_per_gram"]
            - expected_price
        ).abs() > 0.00001
    ).sum()

    record_check(
        "TRANSACTION GOLD PRICE MATCHING",
        missing_prices == 0 and mismatches == 0,
        (
            f"Missing price matches: {missing_prices}, "
            f"Price mismatches: {mismatches}"
        )
    )


# --------------------------------------------------
# 15. VALIDATE FINANCIAL CALCULATIONS
# --------------------------------------------------

def validate_financial_calculations(transactions):

    quantity = pd.to_numeric(
        transactions["gold_quantity_grams"],
        errors="coerce"
    )

    price = pd.to_numeric(
        transactions["gold_price_per_gram"],
        errors="coerce"
    )

    amount = pd.to_numeric(
        transactions["amount"],
        errors="coerce"
    )

    calculated_amount = (
        quantity * price
    ).round(2)

    difference = (
        amount - calculated_amount
    ).abs()

    invalid_count = (
        difference > 0.02
    ).sum()

    record_check(
        "GOLD TRANSACTION AMOUNT CONSISTENCY",
        invalid_count == 0,
        f"Calculation mismatches: {invalid_count}"
    )


# --------------------------------------------------
# 16. VALIDATE WALLET LEDGER RELATIONSHIPS
# --------------------------------------------------


def validate_wallet_ledger(datasets):

    transactions = datasets["transactions"].copy()
    ledger = datasets["wallet_ledger"].copy()

    transactions["gold_quantity_grams"] = pd.to_numeric(
        transactions["gold_quantity_grams"],
        errors="coerce"
    )

    ledger["gold_quantity_grams"] = pd.to_numeric(
        ledger["gold_quantity_grams"],
        errors="coerce"
    )

    # Successful transactions must have exactly one ledger entry.

    successful = transactions[
        transactions["transaction_status"] == "SUCCESS"
    ]

    ledger_counts = ledger.groupby(
        "transaction_id"
    ).size()

    missing_entries = (
        ~successful["transaction_id"].isin(ledger_counts.index)
    ).sum()

    duplicate_entries = (
        ledger_counts > 1
    ).sum()

    record_check(
        "SUCCESSFUL TRANSACTION LEDGER COVERAGE",
        missing_entries == 0 and duplicate_entries == 0,
        (
            f"Missing entries: {missing_entries}, "
            f"Duplicate ledger transactions: {duplicate_entries}"
        )
    )

    # Failed and pending transactions must not have ledger entries.

    non_successful = transactions[
        transactions["transaction_status"] != "SUCCESS"
    ]

    unexpected_entries = (
        non_successful["transaction_id"]
        .isin(ledger["transaction_id"])
    ).sum()

    record_check(
        "NON-SUCCESSFUL TRANSACTION LEDGER EXCLUSION",
        unexpected_entries == 0,
        f"Unexpected ledger entries: {unexpected_entries}"
    )

    # Compare ledger and transaction records.

    merged = ledger.merge(
        transactions[
            [
                "transaction_id",
                "customer_id",
                "transaction_type",
                "gold_quantity_grams",
                "transaction_status"
            ]
        ],
        on="transaction_id",
        how="left",
        suffixes=("_ledger", "_transaction")
    )

    customer_mismatches = (
        merged["customer_id_ledger"]
        != merged["customer_id_transaction"]
    ).sum()

    quantity_mismatches = (
        (
            merged["gold_quantity_grams_ledger"]
            - merged["gold_quantity_grams_transaction"]
        ).abs() > 0.000001
    ).sum()

    expected_ledger_type = merged[
        "transaction_type_transaction"
    ].map({
        "BUY": "CREDIT",
        "SELL": "DEBIT"
    })

    type_mismatches = (
        merged["transaction_type_ledger"]
        != expected_ledger_type
    ).sum()

    record_check(
        "WALLET LEDGER TRANSACTION CONSISTENCY",
        (
            customer_mismatches == 0
            and quantity_mismatches == 0
            and type_mismatches == 0
        ),
        (
            f"Customer mismatches: {customer_mismatches}, "
            f"Quantity mismatches: {quantity_mismatches}, "
            f"Type mismatches: {type_mismatches}"
        )
    )


# --------------------------------------------------
# 17. VALIDATE CUSTOMER GOLD HOLDINGS
# --------------------------------------------------

def validate_holdings(transactions):

    df = transactions.copy()

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

    df["gold_quantity_grams"] = pd.to_numeric(
        df["gold_quantity_grams"],
        errors="coerce"
    )

    df = df.sort_values(
        ["transaction_date", "transaction_id"]
    )

    holdings = {}

    invalid_sales = 0

    for row in df.itertuples(index=False):

        # Failed and pending transactions do not affect holdings.

        if row.transaction_status != "SUCCESS":
            continue

        customer_id = row.customer_id

        available_gold = holdings.get(
            customer_id,
            0.0
        )

        if row.transaction_type == "BUY":

            holdings[customer_id] = (
                available_gold + row.gold_quantity_grams
            )

        elif row.transaction_type == "SELL":

            if (
                row.gold_quantity_grams
                > available_gold + 0.000001
            ):

                invalid_sales += 1

            else:

                holdings[customer_id] = max(
                    0.0,
                    available_gold - row.gold_quantity_grams
                )

    record_check(
        "SUCCESSFUL SELL HOLDINGS",
        invalid_sales == 0,
        f"Invalid sell transactions: {invalid_sales}"
    )


# --------------------------------------------------
# 18. VALIDATE WALLET BALANCE RECONCILIATION
# --------------------------------------------------

def validate_wallet_balances(datasets):

    transactions = datasets["transactions"].copy()
    ledger = datasets["wallet_ledger"].copy()

    transactions = transactions[
        transactions["transaction_status"] == "SUCCESS"
    ].copy()

    transactions["transaction_date"] = pd.to_datetime(
        transactions["transaction_date"],
        errors="coerce"
    )

    transactions["gold_quantity_grams"] = pd.to_numeric(
        transactions["gold_quantity_grams"],
        errors="coerce"
    )

    ledger["balance_after_grams"] = pd.to_numeric(
        ledger["balance_after_grams"],
        errors="coerce"
    )

    ledger_lookup = ledger.set_index(
        "transaction_id"
    )["balance_after_grams"].to_dict()

    holdings = {}

    mismatches = 0

    transactions = transactions.sort_values(
        ["transaction_date", "transaction_id"]
    )

    for row in transactions.itertuples(index=False):

        customer_id = row.customer_id

        available_gold = holdings.get(
            customer_id,
            0.0
        )

        if row.transaction_type == "BUY":

            expected_balance = (
                available_gold + row.gold_quantity_grams
            )

        else:

            expected_balance = (
                available_gold - row.gold_quantity_grams
            )

        expected_balance = round(
            max(expected_balance, 0.0),
            4
        )

        actual_balance = ledger_lookup.get(
            row.transaction_id
        )

        if (
            actual_balance is None
            or abs(actual_balance - expected_balance) > 0.0001
        ):

            mismatches += 1

        holdings[customer_id] = expected_balance

    record_check(
        "WALLET BALANCE RECONCILIATION",
        mismatches == 0,
        f"Balance mismatches: {mismatches}"
    )


# --------------------------------------------------
# 19. FINAL VALIDATION SUMMARY
# --------------------------------------------------

def print_summary():

    total_checks = len(validation_results)

    passed_checks = sum(
        result["passed"]
        for result in validation_results
    )

    failed_checks = total_checks - passed_checks

    print("\n" + "=" * 65)
    print("DIGITAL GOLD DATA QUALITY SUMMARY")
    print("=" * 65)

    print(f"Total checks : {total_checks}")
    print(f"Passed       : {passed_checks}")
    print(f"Failed       : {failed_checks}")

    print("=" * 65)

    if failed_checks == 0:

        print(
            "ALL DIGITAL GOLD DATA QUALITY CHECKS PASSED!"
        )

    else:

        print("FAILED VALIDATION CHECKS:")

        for result in validation_results:

            if not result["passed"]:
                print(
                    f"- {result['check']}: "
                    f"{result['details']}"
                )


# --------------------------------------------------
# 20. MAIN EXECUTION
# --------------------------------------------------

def main():

    print("=" * 65)
    print("FINTECH 360 - DIGITAL GOLD DATA QUALITY VALIDATION")
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

        validate_price_uniqueness(
            datasets["price_history"]
        )

        validate_transaction_prices(datasets)

        validate_financial_calculations(
            datasets["transactions"]
        )

        validate_wallet_ledger(datasets)

        validate_holdings(
            datasets["transactions"]
        )

        validate_wallet_balances(datasets)

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
# 21. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()
