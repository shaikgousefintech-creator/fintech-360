
import csv
import random
import calendar
from datetime import date, timedelta
from pathlib import Path


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "cash_loans"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

TOTAL_CUSTOMERS = 5000
TOTAL_APPLICATIONS = 15000

START_DATE = date(2025, 1, 1)
END_DATE = date(2026, 11, 10)

CUSTOMER_REGISTRATION_START = date(2024, 1, 1)
CUSTOMER_REGISTRATION_END = date(2026, 10, 31)


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
    "Bengaluru", "Hyderabad", "Mumbai", "Chennai",
    "Delhi", "Pune", "Kolkata", "Ahmedabad",
    "Jaipur", "Kochi"
]

GENDERS = ["MALE", "FEMALE", "OTHER"]

CUSTOMER_SEGMENTS = ["NEW", "REGULAR", "PREMIUM"]

EMPLOYMENT_TYPES = [
    "SALARIED",
    "SELF_EMPLOYED",
    "BUSINESS_OWNER",
    "STUDENT",
    "UNEMPLOYED"
]

REJECTION_REASONS = [
    "LOW_CREDIT_SCORE",
    "INSUFFICIENT_INCOME",
    "HIGH_EXISTING_DEBT",
    "INCOMPLETE_DOCUMENTATION",
    "EMPLOYMENT_VERIFICATION_FAILED"
]

DISBURSEMENT_FAILURE_REASONS = [
    "BANK_ACCOUNT_VALIDATION_FAILED",
    "BANK_TRANSFER_FAILED",
    "PAYMENT_GATEWAY_ERROR",
    "BENEFICIARY_DETAILS_INVALID"
]


LOAN_PRODUCTS = [
    {
        "product_id": "LP001",
        "product_name": "Flexi Personal Loan",
        "loan_type": "PERSONAL",
        "min_loan_amount": 10000,
        "max_loan_amount": 500000,
        "annual_interest_rate": 14.5,
        "min_tenure_months": 6,
        "max_tenure_months": 36,
        "processing_fee_percentage": 2.0
    },
    {
        "product_id": "LP002",
        "product_name": "Quick Salary Advance",
        "loan_type": "SALARY",
        "min_loan_amount": 5000,
        "max_loan_amount": 100000,
        "annual_interest_rate": 12.0,
        "min_tenure_months": 3,
        "max_tenure_months": 12,
        "processing_fee_percentage": 1.5
    },
    {
        "product_id": "LP003",
        "product_name": "Business Growth Loan",
        "loan_type": "BUSINESS",
        "min_loan_amount": 50000,
        "max_loan_amount": 1000000,
        "annual_interest_rate": 16.0,
        "min_tenure_months": 12,
        "max_tenure_months": 48,
        "processing_fee_percentage": 2.5
    },
    {
        "product_id": "LP004",
        "product_name": "Emergency Cash Loan",
        "loan_type": "EMERGENCY",
        "min_loan_amount": 5000,
        "max_loan_amount": 75000,
        "annual_interest_rate": 18.0,
        "min_tenure_months": 3,
        "max_tenure_months": 12,
        "processing_fee_percentage": 1.0
    },
    {
        "product_id": "LP005",
        "product_name": "Premium Personal Loan",
        "loan_type": "PERSONAL",
        "min_loan_amount": 100000,
        "max_loan_amount": 1500000,
        "annual_interest_rate": 11.5,
        "min_tenure_months": 12,
        "max_tenure_months": 60,
        "processing_fee_percentage": 1.5
    },
    {
        "product_id": "LP006",
        "product_name": "Monthly Salary Loan",
        "loan_type": "SALARY",
        "min_loan_amount": 10000,
        "max_loan_amount": 200000,
        "annual_interest_rate": 13.0,
        "min_tenure_months": 6,
        "max_tenure_months": 24,
        "processing_fee_percentage": 1.75
    },
    {
        "product_id": "LP007",
        "product_name": "Small Business Loan",
        "loan_type": "BUSINESS",
        "min_loan_amount": 25000,
        "max_loan_amount": 500000,
        "annual_interest_rate": 15.0,
        "min_tenure_months": 6,
        "max_tenure_months": 36,
        "processing_fee_percentage": 2.0
    },
    {
        "product_id": "LP008",
        "product_name": "Instant Emergency Loan",
        "loan_type": "EMERGENCY",
        "min_loan_amount": 3000,
        "max_loan_amount": 50000,
        "annual_interest_rate": 19.0,
        "min_tenure_months": 3,
        "max_tenure_months": 9,
        "processing_fee_percentage": 1.0
    }
]


APPLICATION_STATUS_WEIGHTS = [
    ("DRAFT", 5),
    ("SUBMITTED", 10),
    ("UNDER_REVIEW", 10),
    ("APPROVED", 55),
    ("REJECTED", 15),
    ("CANCELLED", 5)
]


# --------------------------------------------------
# 3. HELPER FUNCTIONS
# --------------------------------------------------

def get_dates(start_date, end_date):

    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    return dates


def add_months(original_date, months):

    month_index = original_date.month - 1 + months

    year = original_date.year + month_index // 12
    month = month_index % 12 + 1

    last_day = calendar.monthrange(year, month)[1]
    day = min(original_date.day, last_day)

    return date(year, month, day)


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

    registration_dates = get_dates(
        CUSTOMER_REGISTRATION_START,
        CUSTOMER_REGISTRATION_END
    )

    for number in range(1, TOTAL_CUSTOMERS + 1):

        customer_id = f"CLCU{number:05d}"

        age = random.randint(21, 65)

        customer_segment = random.choices(
            CUSTOMER_SEGMENTS,
            weights=[25, 55, 20]
        )[0]

        customers.append({
            "customer_id": customer_id,
            "customer_name": (
                f"{random.choice(FIRST_NAMES)} "
                f"{random.choice(LAST_NAMES)}"
            ),
            "age": age,
            "gender": random.choice(GENDERS),
            "city": random.choice(CITIES),
            "registration_date": random.choice(
                registration_dates
            ).isoformat(),
            "customer_segment": customer_segment
        })

    return customers


# --------------------------------------------------
# 5. GENERATE LOAN PRODUCTS
# --------------------------------------------------

def generate_loan_products():

    products = []

    for product in LOAN_PRODUCTS:

        products.append({
            **product,
            "launch_date": "2024-01-01"
        })

    return products


# --------------------------------------------------
# 6. GENERATE LOAN APPLICATIONS
# --------------------------------------------------

def generate_loan_applications(customers, products):

    applications = []

    customer_lookup = {
        customer["customer_id"]: customer
        for customer in customers
    }

    product_lookup = {
        product["product_id"]: product
        for product in products
    }

    customer_ids = list(customer_lookup.keys())
    product_ids = list(product_lookup.keys())

    application_dates = get_dates(
        START_DATE,
        END_DATE
    )

    for number in range(1, TOTAL_APPLICATIONS + 1):

        customer_id = random.choice(customer_ids)
        product_id = random.choice(product_ids)

        customer = customer_lookup[customer_id]
        product = product_lookup[product_id]

        registration_date = date.fromisoformat(
            customer["registration_date"]
        )

        eligible_dates = [
            application_date
            for application_date in application_dates
            if application_date >= registration_date
        ]

        application_date = random.choice(eligible_dates)

        requested_amount = round(
            random.uniform(
                product["min_loan_amount"],
                product["max_loan_amount"]
            ),
            2
        )

        employment_type = random.choices(
            EMPLOYMENT_TYPES,
            weights=[60, 15, 10, 8, 7]
        )[0]

        if employment_type == "SALARIED":
            monthly_income = round(
                random.uniform(15000, 200000), 2
            )

        elif employment_type == "SELF_EMPLOYED":
            monthly_income = round(
                random.uniform(20000, 250000), 2
            )

        elif employment_type == "BUSINESS_OWNER":
            monthly_income = round(
                random.uniform(30000, 500000), 2
            )

        elif employment_type == "STUDENT":
            monthly_income = round(
                random.uniform(0, 10000), 2
            )

        else:
            monthly_income = 0.0

        credit_score = random.randint(300, 900)

        application_status = random.choices(
            [status for status, _ in APPLICATION_STATUS_WEIGHTS],
            weights=[
                weight
                for _, weight in APPLICATION_STATUS_WEIGHTS
            ]
        )[0]

        approved_amount = None
        rejection_reason = None

        if application_status == "APPROVED":

            approval_percentage = random.uniform(
                0.70, 1.00
            )

            approved_amount = round(
                requested_amount * approval_percentage,
                2
            )

        elif application_status == "REJECTED":

            rejection_reason = random.choice(
                REJECTION_REASONS
            )

        applications.append({
            "application_id": f"CLAPP{number:07d}",
            "customer_id": customer_id,
            "product_id": product_id,
            "application_date": application_date.isoformat(),
            "requested_amount": requested_amount,
            "approved_amount": approved_amount,
            "credit_score": credit_score,
            "employment_type": employment_type,
            "monthly_income": monthly_income,
            "application_status": application_status,
            "rejection_reason": rejection_reason
        })

    applications.sort(
        key=lambda application: application["application_date"]
    )

    return applications


# --------------------------------------------------
# 7. GENERATE LOAN DISBURSEMENTS
# --------------------------------------------------

def generate_loan_disbursements(applications):

    disbursements = []

    approved_applications = [
        application
        for application in applications
        if application["application_status"] == "APPROVED"
    ]

    for number, application in enumerate(
        approved_applications,
        start=1
    ):

        application_date = date.fromisoformat(
            application["application_date"]
        )

        disbursement_status = random.choices(
            ["SUCCESS", "FAILED", "PENDING"],
            weights=[94, 4, 2]
        )[0]

        disbursement_date = None
        failure_reason = None

        if disbursement_status == "SUCCESS":

            days_after_application = random.randint(1, 7)

            disbursement_date = min(
                application_date + timedelta(
                    days=days_after_application
                ),
                END_DATE
            ).isoformat()

        elif disbursement_status == "FAILED":

            failure_reason = random.choice(
                DISBURSEMENT_FAILURE_REASONS
            )

        disbursements.append({
            "disbursement_id": f"CLDIS{number:07d}",
            "application_id": application["application_id"],
            "disbursement_date": disbursement_date,
            "disbursed_amount": application["approved_amount"],
            "disbursement_status": disbursement_status,
            "failure_reason": failure_reason
        })

    return disbursements


# --------------------------------------------------
# 8. GENERATE LOAN REPAYMENTS
# --------------------------------------------------

def generate_loan_repayments(
    applications,
    products,
    disbursements
):

    repayments = []

    application_lookup = {
        application["application_id"]: application
        for application in applications
    }

    product_lookup = {
        product["product_id"]: product
        for product in products
    }

    installment_number = 0

    successful_disbursements = [
        disbursement
        for disbursement in disbursements
        if disbursement["disbursement_status"] == "SUCCESS"
    ]

    for disbursement in successful_disbursements:

        application = application_lookup[
            disbursement["application_id"]
        ]

        product = product_lookup[
            application["product_id"]
        ]

        disbursement_date = date.fromisoformat(
            disbursement["disbursement_date"]
        )

        loan_amount = float(
            disbursement["disbursed_amount"]
        )

        annual_interest_rate = (
            product["annual_interest_rate"] / 100
        )

        monthly_interest_rate = (
            annual_interest_rate / 12
        )

        tenure_months = random.randint(
            product["min_tenure_months"],
            product["max_tenure_months"]
        )

        regular_principal = round(
            loan_amount / tenure_months,
            2
        )

        outstanding_principal = loan_amount

        for installment in range(1, tenure_months + 1):

            installment_number += 1

            due_date = add_months(
                disbursement_date,
                installment
            )

            if installment == tenure_months:

                principal_amount = round(
                    outstanding_principal,
                    2
                )

            else:

                principal_amount = min(
                    regular_principal,
                    outstanding_principal
                )

            interest_amount = round(
                outstanding_principal * monthly_interest_rate,
                2
            )

            total_due_amount = round(
                principal_amount + interest_amount,
                2
            )

            outstanding_principal = round(
                outstanding_principal - principal_amount,
                2
            )

            amount_paid = 0.0
            payment_date = None
            late_days = 0

            if due_date > END_DATE:

                repayment_status = "PENDING"

            else:

                repayment_status = random.choices(
                    ["PAID", "PARTIAL", "FAILED", "OVERDUE"],
                    weights=[78, 8, 4, 10]
                )[0]

                if repayment_status == "PAID":

                    amount_paid = total_due_amount

                    payment_date = min(
                        due_date + timedelta(
                            days=random.randint(0, 15)
                        ),
                        END_DATE
                    )

                    late_days = max(
                        (payment_date - due_date).days,
                        0
                    )

                elif repayment_status == "PARTIAL":

                    payment_percentage = random.uniform(
                        0.20, 0.80
                    )

                    amount_paid = round(
                        total_due_amount * payment_percentage,
                        2
                    )

                    payment_date = min(
                        due_date + timedelta(
                            days=random.randint(0, 20)
                        ),
                        END_DATE
                    )

                    late_days = max(
                        (payment_date - due_date).days,
                        0
                    )

                elif repayment_status == "OVERDUE":

                    late_days = (
                        END_DATE - due_date
                    ).days

            repayments.append({
                "repayment_id": f"CLREP{installment_number:08d}",
                "disbursement_id": disbursement["disbursement_id"],
                "installment_number": installment,
                "due_date": due_date.isoformat(),
                "payment_date": (
                    payment_date.isoformat()
                    if payment_date else None
                ),
                "principal_amount": principal_amount,
                "interest_amount": interest_amount,
                "total_due_amount": total_due_amount,
                "amount_paid": amount_paid,
                "repayment_status": repayment_status,
                "late_days": late_days
            })

    return repayments


# --------------------------------------------------
# 9. MAIN DATA GENERATION WORKFLOW
# --------------------------------------------------

def main():

    print("=" * 65)
    print("FINTECH 360 - CASH LOANS DATA GENERATOR")
    print("=" * 65)

    customers = generate_customers()

    products = generate_loan_products()

    applications = generate_loan_applications(
        customers,
        products
    )

    disbursements = generate_loan_disbursements(
        applications
    )

    repayments = generate_loan_repayments(
        applications,
        products,
        disbursements
    )

    # Save all five datasets.

    write_csv(
        "cash_loan_customers.csv",
        customers
    )

    write_csv(
        "cash_loan_products.csv",
        products
    )

    write_csv(
        "cash_loan_applications.csv",
        applications
    )

    write_csv(
        "cash_loan_disbursements.csv",
        disbursements
    )

    write_csv(
        "cash_loan_repayments.csv",
        repayments
    )

    # Calculate generation statistics.

    approved = sum(
        1 for application in applications
        if application["application_status"] == "APPROVED"
    )

    rejected = sum(
        1 for application in applications
        if application["application_status"] == "REJECTED"
    )

    successful_disbursements = sum(
        1 for disbursement in disbursements
        if disbursement["disbursement_status"] == "SUCCESS"
    )

    failed_disbursements = sum(
        1 for disbursement in disbursements
        if disbursement["disbursement_status"] == "FAILED"
    )

    pending_disbursements = sum(
        1 for disbursement in disbursements
        if disbursement["disbursement_status"] == "PENDING"
    )

    print("\n" + "=" * 65)
    print("CASH LOANS DATA GENERATION COMPLETED")
    print("=" * 65)

    print(f"Customers: {len(customers):,}")
    print(f"Loan products: {len(products):,}")
    print(f"Applications: {len(applications):,}")
    print(f"Approved applications: {approved:,}")
    print(f"Rejected applications: {rejected:,}")
    print(f"Disbursements: {len(disbursements):,}")
    print(f"Successful disbursements: {successful_disbursements:,}")
    print(f"Failed disbursements: {failed_disbursements:,}")
    print(f"Pending disbursements: {pending_disbursements:,}")
    print(f"Repayment records: {len(repayments):,}")

    print(f"\nOutput directory: {OUTPUT_DIR}")


# --------------------------------------------------
# 10. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()
