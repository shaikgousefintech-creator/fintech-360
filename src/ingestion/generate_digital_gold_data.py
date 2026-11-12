
import csv
import random
from datetime import date, timedelta
from pathlib import Path


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "digital_gold"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

TOTAL_CUSTOMERS = 5000
TOTAL_TRANSACTIONS = 50000

START_DATE = date(2025, 1, 1)
END_DATE = date(2026, 11, 10)

PRICE_HISTORY_START_DATE = date(2024, 12, 11)

TRANSACTION_STATUS_WEIGHTS = [97.5, 2.0, 0.5]


# --------------------------------------------------
# 2. MASTER DATA CONFIGURATION
# --------------------------------------------------

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Arjun",
    "Rahul", "Rohan", "Karan", "Vikram",
    "Ananya", "Diya", "Priya", "Sneha",
    "Meera", "Isha", "Kavya", "Neha",
    "Amit", "Sanjay", "Pooja", "Riya"
]

LAST_NAMES = [
    "Sharma", "Verma", "Reddy", "Patel",
    "Kumar", "Mehta", "Rao", "Gupta",
    "Nair", "Singh", "Joshi", "Das",
    "Iyer", "Kapoor", "Mishra"
]

CITIES = [
    "Bengaluru", "Hyderabad", "Mumbai",
    "Chennai", "Delhi", "Pune",
    "Kolkata", "Ahmedabad", "Jaipur", "Kochi"
]

INVESTMENT_MODES = [
    "UPI",
    "BANK_TRANSFER",
    "CARD",
    "WALLET"
]

TRANSACTION_FAILURE_REASONS = [
    "PAYMENT_FAILED",
    "INSUFFICIENT_BALANCE",
    "TRANSACTION_TIMEOUT",
    "BANK_SERVER_ERROR"
]


# --------------------------------------------------
# 3. HELPER FUNCTIONS
# --------------------------------------------------

def get_calendar_dates(start_date, end_date):

    dates = []
    current_date = start_date

    while current_date <= end_date:

        dates.append(current_date)

        current_date += timedelta(days=1)

    return dates


def write_csv(file_name, records):

    file_path = OUTPUT_DIR / file_name

    if not records:
        raise ValueError(
            f"No records available for {file_name}"
        )

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(records[0].keys())
        )

        writer.writeheader()
        writer.writerows(records)

    print(
        f"Created: {file_name} | "
        f"Records: {len(records):,}"
    )


# --------------------------------------------------
# 4. GENERATE CUSTOMERS
# --------------------------------------------------

def generate_customers():

    customers = []

    registration_dates = get_calendar_dates(
        date(2024, 1, 1),
        date(2025, 12, 31)
    )

    for number in range(1, TOTAL_CUSTOMERS + 1):

        customer_id = f"DGC{number:05d}"

        age = random.randint(21, 65)

        gender = random.choice([
            "MALE",
            "FEMALE",
            "OTHER"
        ])

        city = random.choice(CITIES)

        registration_date = random.choice(
            registration_dates
        )

        customer_segment = (
            "PREMIUM" if random.random() < 0.15
            else "REGULAR"
        )

        customers.append({
            "customer_id": customer_id,
            "customer_name": (
                f"{random.choice(FIRST_NAMES)} "
                f"{random.choice(LAST_NAMES)}"
            ),
            "age": age,
            "gender": gender,
            "city": city,
            "registration_date": registration_date.isoformat(),
            "customer_segment": customer_segment
        })

    return customers


# --------------------------------------------------
# 5. GENERATE DAILY GOLD PRICE HISTORY
# --------------------------------------------------

def generate_price_history():

    price_records = []
    price_lookup = {}

    price_dates = get_calendar_dates(
        PRICE_HISTORY_START_DATE,
        END_DATE
    )

    current_gold_price = 7500.00

    for price_date in price_dates:

        daily_change = random.gauss(
            0.0007,
            0.008
        )

        current_gold_price *= (1 + daily_change)

        current_gold_price = max(
            current_gold_price,
            5000.00
        )

        gold_price = round(current_gold_price, 2)

        buy_price = round(
            gold_price * 1.03,
            2
        )

        sell_price = round(
            gold_price * 0.97,
            2
        )

        price_id = (
            f"DGPRICE_{price_date.strftime('%Y%m%d')}"
        )

        record = {
            "price_id": price_id,
            "price_date": price_date.isoformat(),
            "gold_price_per_gram": gold_price,
            "buy_price_per_gram": buy_price,
            "sell_price_per_gram": sell_price
        }

        price_records.append(record)

        price_lookup[price_date] = record

    return price_records, price_lookup


# --------------------------------------------------
# 6. GENERATE BUY/SELL TRANSACTIONS
# --------------------------------------------------

def generate_transactions(
    customers,
    transaction_dates,
    price_lookup
):

    transactions = []
    wallet_ledger = []

    customer_lookup = {
        customer["customer_id"]: customer
        for customer in customers
    }

    customer_ids = list(customer_lookup.keys())

    # Maintain customer gold holdings.

    holdings = {}

    # Generate transaction events first.

    events = []

    for _ in range(TOTAL_TRANSACTIONS):

        customer_id = random.choice(customer_ids)

        registration_date = date.fromisoformat(
            customer_lookup[customer_id]["registration_date"]
        )

        eligible_dates = [
            transaction_date
            for transaction_date in transaction_dates
            if transaction_date >= registration_date
        ]

        transaction_date = random.choice(eligible_dates)

        requested_type = (
            "BUY" if random.random() < 0.75
            else "SELL"
        )

        events.append({
            "customer_id": customer_id,
            "transaction_date": transaction_date,
            "requested_type": requested_type
        })

    # Process events chronologically.

    events.sort(
        key=lambda event: event["transaction_date"]
    )

    for number, event in enumerate(events, start=1):

        customer_id = event["customer_id"]

        transaction_date = event["transaction_date"]

        price_record = price_lookup[transaction_date]

        holding_key = customer_id

        available_gold = holdings.get(
            holding_key,
            0.0
        )

        transaction_type = event["requested_type"]

        # Do not allow selling more gold than owned.

        if (
            transaction_type == "SELL"
            and available_gold <= 0
        ):
            transaction_type = "BUY"

        if transaction_type == "BUY":

            investment_mode = random.choice(
                INVESTMENT_MODES
            )

            gold_quantity = round(
                random.uniform(0.1, 10.0),
                4
            )

            gold_price = price_record[
                "buy_price_per_gram"
            ]

        else:

            investment_mode = random.choice(
                INVESTMENT_MODES
            )

            sell_percentage = random.uniform(
                0.05,
                0.50
            )

            gold_quantity = round(
                available_gold * sell_percentage,
                4
            )

            gold_quantity = min(
                gold_quantity,
                available_gold
            )

            gold_price = price_record[
                "sell_price_per_gram"
            ]

        amount = round(
            gold_quantity * gold_price,
            2
        )

        transaction_status = random.choices(
            ["SUCCESS", "FAILED", "PENDING"],
            weights=TRANSACTION_STATUS_WEIGHTS
        )[0]

        if transaction_status == "FAILED":

            failure_reason = random.choice(
                TRANSACTION_FAILURE_REASONS
            )

        elif transaction_status == "PENDING":

            failure_reason = "PAYMENT_PENDING"

        else:

            failure_reason = ""

        transaction_id = f"DGTRX{number:07d}"

        # Only successful transactions update holdings.

        if transaction_status == "SUCCESS":

            if transaction_type == "BUY":

                new_balance = (
                    available_gold + gold_quantity
                )

                ledger_type = "CREDIT"

            else:

                new_balance = (
                    available_gold - gold_quantity
                )

                ledger_type = "DEBIT"

            new_balance = round(
                max(new_balance, 0.0),
                4
            )

            holdings[holding_key] = new_balance

            # Create wallet ledger entry.

            wallet_ledger.append({
                "ledger_id": (
                    f"DGLED{len(wallet_ledger) + 1:07d}"
                ),
                "customer_id": customer_id,
                "transaction_id": transaction_id,
                "entry_date": transaction_date.isoformat(),
                "transaction_type": ledger_type,
                "gold_quantity_grams": gold_quantity,
                "balance_after_grams": new_balance
            })

        transactions.append({
            "transaction_id": transaction_id,
            "customer_id": customer_id,
            "transaction_date": transaction_date.isoformat(),
            "transaction_type": transaction_type,
            "investment_mode": investment_mode,
            "gold_quantity_grams": gold_quantity,
            "gold_price_per_gram": gold_price,
            "amount": amount,
            "transaction_status": transaction_status,
            "failure_reason": failure_reason
        })

    return transactions, wallet_ledger


# --------------------------------------------------
# 7. MAIN DATA GENERATION WORKFLOW
# --------------------------------------------------

def main():

    print("=" * 65)
    print("FINTECH 360 - DIGITAL GOLD DATA GENERATOR")
    print("=" * 65)

    transaction_dates = get_calendar_dates(
        START_DATE,
        END_DATE
    )

    customers = generate_customers()

    price_records, price_lookup = generate_price_history()

    transactions, wallet_ledger = generate_transactions(
        customers,
        transaction_dates,
        price_lookup
    )

    # Save all four datasets.

    write_csv(
        "digital_gold_customers.csv",
        customers
    )

    write_csv(
        "digital_gold_price_history.csv",
        price_records
    )

    write_csv(
        "digital_gold_transactions.csv",
        transactions
    )

    write_csv(
        "digital_gold_wallet_ledger.csv",
        wallet_ledger
    )

    successful = sum(
        1 for transaction in transactions
        if transaction["transaction_status"] == "SUCCESS"
    )

    failed = sum(
        1 for transaction in transactions
        if transaction["transaction_status"] == "FAILED"
    )

    pending = sum(
        1 for transaction in transactions
        if transaction["transaction_status"] == "PENDING"
    )

    buy_count = sum(
        1 for transaction in transactions
        if transaction["transaction_type"] == "BUY"
    )

    sell_count = sum(
        1 for transaction in transactions
        if transaction["transaction_type"] == "SELL"
    )

    print("\n" + "=" * 65)
    print("DIGITAL GOLD DATA GENERATION COMPLETED")
    print("=" * 65)

    print(f"Customers: {len(customers):,}")
    print(f"Price history records: {len(price_records):,}")
    print(f"Transactions: {len(transactions):,}")
    print(f"Wallet ledger entries: {len(wallet_ledger):,}")

    print(f"\nSuccessful transactions: {successful:,}")
    print(f"Failed transactions: {failed:,}")
    print(f"Pending transactions: {pending:,}")

    print(f"\nBUY transactions: {buy_count:,}")
    print(f"SELL transactions: {sell_count:,}")

    print(
        "\nLedger reconciliation: "
        f"{'PASSED' if successful == len(wallet_ledger) else 'FAILED'}"
    )

    print(f"\nOutput directory: {OUTPUT_DIR}")


# --------------------------------------------------
# 8. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()
