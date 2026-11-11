
import csv
import random
from datetime import date, timedelta
from pathlib import Path


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "mutual_funds"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

TOTAL_INVESTORS = 1000
TOTAL_TRANSACTIONS = 20000

START_DATE = date(2025, 1, 1)
END_DATE = date(2026, 11, 10)

TRANSACTION_SUCCESS_RATE = 0.975


# --------------------------------------------------
# 2. MASTER DATA CONFIGURATION
# --------------------------------------------------

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Rahul",
    "Rohan", "Karan", "Vikram", "Ananya", "Diya",
    "Priya", "Sneha", "Meera", "Isha", "Kavya",
    "Neha", "Amit", "Sanjay", "Pooja", "Riya"
]

LAST_NAMES = [
    "Sharma", "Verma", "Reddy", "Patel", "Kumar",
    "Mehta", "Rao", "Gupta", "Nair", "Singh",
    "Joshi", "Das", "Iyer", "Kapoor", "Mishra"
]

CITIES = [
    "Bengaluru", "Hyderabad", "Mumbai", "Chennai",
    "Delhi", "Pune", "Kolkata", "Ahmedabad",
    "Jaipur", "Kochi"
]

FUND_HOUSES = [
    "Apex Mutual Fund",
    "Horizon Asset Management",
    "Summit Investments",
    "Crest Financial",
    "Pioneer Asset Management"
]

SCHEME_CATEGORIES = {
    "EQUITY": {
        "risk": "HIGH",
        "benchmark": "NIFTY 50",
        "volatility": 0.012,
        "drift": 0.0004
    },
    "DEBT": {
        "risk": "LOW",
        "benchmark": "CRISIL BOND INDEX",
        "volatility": 0.002,
        "drift": 0.00015
    },
    "HYBRID": {
        "risk": "MODERATE",
        "benchmark": "NIFTY HYBRID INDEX",
        "volatility": 0.007,
        "drift": 0.0003
    },
    "INDEX": {
        "risk": "HIGH",
        "benchmark": "NIFTY 50",
        "volatility": 0.010,
        "drift": 0.00035
    }
}


# --------------------------------------------------
# 3. HELPER FUNCTIONS
# --------------------------------------------------

def get_business_dates(start_date, end_date):

    dates = []
    current_date = start_date

    while current_date <= end_date:

        if current_date.weekday() < 5:
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
# 4. GENERATE INVESTORS
# --------------------------------------------------

def generate_investors():

    investors = []

    registration_dates = get_business_dates(
        date(2024, 1, 1),
        date(2025, 12, 31)
    )

    for number in range(1, TOTAL_INVESTORS + 1):

        investor_id = f"INV{number:05d}"

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

        investor_segment = (
            "HNI" if random.random() < 0.15
            else "RETAIL"
        )

        investors.append({
            "investor_id": investor_id,
            "investor_name": (
                f"{random.choice(FIRST_NAMES)} "
                f"{random.choice(LAST_NAMES)}"
            ),
            "age": age,
            "gender": gender,
            "city": city,
            "registration_date": registration_date.isoformat(),
            "investor_segment": investor_segment
        })

    return investors


# --------------------------------------------------
# 5. GENERATE MUTUAL FUND SCHEMES
# --------------------------------------------------

def generate_schemes():

    schemes = []

    categories = list(SCHEME_CATEGORIES.keys())

    for number in range(1, 21):

        category = categories[
            (number - 1) % len(categories)
        ]

        category_config = SCHEME_CATEGORIES[category]

        scheme_id = f"SCM{number:03d}"

        scheme_name = (
            f"{random.choice(FUND_HOUSES)} "
            f"{category.title()} Fund {number:02d}"
        )

        schemes.append({
            "scheme_id": scheme_id,
            "scheme_name": scheme_name,
            "fund_house": random.choice(FUND_HOUSES),
            "fund_category": category,
            "risk_level": category_config["risk"],
            "benchmark": category_config["benchmark"],
            "expense_ratio": round(
                random.uniform(0.25, 2.25), 2
            ),
            "launch_date": "2024-01-01"
        })

    return schemes


# --------------------------------------------------
# 6. GENERATE DAILY NAV HISTORY
# --------------------------------------------------

def generate_nav_history(schemes, business_dates):

    nav_records = []
    nav_lookup = {}

    for scheme in schemes:

        scheme_id = scheme["scheme_id"]

        category = scheme["fund_category"]

        config = SCHEME_CATEGORIES[category]

        current_nav = random.uniform(10, 100)

        for nav_date in business_dates:

            daily_return = random.gauss(
                config["drift"],
                config["volatility"]
            )

            current_nav *= (1 + daily_return)

            current_nav = max(current_nav, 1.0)

            nav_value = round(current_nav, 4)

            nav_lookup[(scheme_id, nav_date)] = nav_value

            nav_records.append({
                "nav_id": (
                    f"NAV{scheme_id[3:]}_"
                    f"{nav_date.strftime('%Y%m%d')}"
                ),
                "scheme_id": scheme_id,
                "nav_date": nav_date.isoformat(),
                "nav_value": nav_value
            })

    return nav_records, nav_lookup


# --------------------------------------------------
# 7. GENERATE INVESTMENT TRANSACTIONS
# --------------------------------------------------

def generate_transactions(
    investors,
    schemes,
    business_dates,
    nav_lookup
):

    transactions = []

    investor_lookup = {
        investor["investor_id"]: investor
        for investor in investors
    }

    scheme_lookup = {
        scheme["scheme_id"]: scheme
        for scheme in schemes
    }

    holdings = {}

    investor_ids = list(investor_lookup.keys())
    scheme_ids = list(scheme_lookup.keys())

    # Generate transaction dates and relationships first.

    events = []

    for _ in range(TOTAL_TRANSACTIONS):

        investor_id = random.choice(investor_ids)

        scheme_id = random.choice(scheme_ids)

        registration_date = date.fromisoformat(
            investor_lookup[investor_id]["registration_date"]
        )

        eligible_dates = [
            transaction_date
            for transaction_date in business_dates
            if transaction_date >= registration_date
        ]

        transaction_date = random.choice(eligible_dates)

        requested_type = (
            "PURCHASE"
            if random.random() < 0.75
            else "REDEMPTION"
        )

        events.append({
            "investor_id": investor_id,
            "scheme_id": scheme_id,
            "transaction_date": transaction_date,
            "requested_type": requested_type
        })

    events.sort(key=lambda event: event["transaction_date"])

    # Process events chronologically to maintain holdings.

    for number, event in enumerate(events, start=1):

        investor_id = event["investor_id"]

        scheme_id = event["scheme_id"]

        transaction_date = event["transaction_date"]

        nav = nav_lookup[(scheme_id, transaction_date)]

        holding_key = (investor_id, scheme_id)

        available_units = holdings.get(holding_key, 0.0)

        transaction_type = event["requested_type"]

        # Never redeem more units than the investor owns.

        if (
            transaction_type == "REDEMPTION"
            and available_units <= 0
        ):
            transaction_type = "PURCHASE"

        if transaction_type == "PURCHASE":

            investment_mode = random.choices(
                ["SIP", "LUMP_SUM"],
                weights=[65, 35]
            )[0]

            if investment_mode == "SIP":
                amount = round(
                    random.uniform(500, 10000), 2
                )
            else:
                amount = round(
                    random.uniform(5000, 100000), 2
                )

            units = round(amount / nav, 6)

        else:

            investment_mode = "NOT_APPLICABLE"

            redemption_percentage = random.uniform(
                0.05, 0.50
            )

            units = round(
                available_units * redemption_percentage,
                6
            )

            amount = round(units * nav, 2)

            units = round(amount / nav, 6)

            if units > available_units:
                units = available_units
                amount = round(units * nav, 2)

        transaction_status = (
            "SUCCESS"
            if random.random() < TRANSACTION_SUCCESS_RATE
            else "FAILED"
        )

        failure_reason = (
            ""
            if transaction_status == "SUCCESS"
            else random.choice([
                "INSUFFICIENT_BALANCE",
                "PAYMENT_FAILED",
                "TRANSACTION_TIMEOUT"
            ])
        )

        # Failed transactions do not change holdings.

        if transaction_status == "SUCCESS":

            if transaction_type == "PURCHASE":
                holdings[holding_key] = (
                    available_units + units
                )

            else:
                holdings[holding_key] = max(
                    0.0,
                    available_units - units
                )

        transactions.append({
            "investment_id": f"INVEST{number:07d}",
            "investor_id": investor_id,
            "scheme_id": scheme_id,
            "transaction_date": transaction_date.isoformat(),
            "transaction_type": transaction_type,
            "investment_mode": investment_mode,
            "amount": amount,
            "nav": nav,
            "units": units,
            "transaction_status": transaction_status,
            "failure_reason": failure_reason
        })

    return transactions


# --------------------------------------------------
# 8. MAIN DATA GENERATION WORKFLOW
# --------------------------------------------------

def main():

    print("=" * 65)
    print("FINTECH 360 - MUTUAL FUNDS DATA GENERATOR")
    print("=" * 65)

    business_dates = get_business_dates(
        START_DATE,
        END_DATE
    )

    investors = generate_investors()

    schemes = generate_schemes()

    nav_records, nav_lookup = generate_nav_history(
        schemes,
        business_dates
    )

    transactions = generate_transactions(
        investors,
        schemes,
        business_dates,
        nav_lookup
    )

    # Save all four datasets.

    write_csv(
        "mutual_fund_investors.csv",
        investors
    )

    write_csv(
        "mutual_fund_schemes.csv",
        schemes
    )

    write_csv(
        "mutual_fund_nav_history.csv",
        nav_records
    )

    write_csv(
        "mutual_fund_transactions.csv",
        transactions
    )

    successful = sum(
        1 for transaction in transactions
        if transaction["transaction_status"] == "SUCCESS"
    )

    failed = len(transactions) - successful

    print("\n" + "=" * 65)
    print("MUTUAL FUNDS DATA GENERATION COMPLETED")
    print("=" * 65)

    print(f"Investors: {len(investors):,}")
    print(f"Schemes: {len(schemes):,}")
    print(f"NAV records: {len(nav_records):,}")
    print(f"Transactions: {len(transactions):,}")
    print(f"Successful transactions: {successful:,}")
    print(f"Failed transactions: {failed:,}")

    print(f"\nOutput directory: {OUTPUT_DIR}")


# --------------------------------------------------
# 9. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()
