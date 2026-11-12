
import sys
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "raw" / "cash_loans"

CUSTOMERS_FILE = DATA_DIR / "cash_loan_customers.csv"
PRODUCTS_FILE = DATA_DIR / "cash_loan_products.csv"
APPLICATIONS_FILE = DATA_DIR / "cash_loan_applications.csv"
DISBURSEMENTS_FILE = DATA_DIR / "cash_loan_disbursements.csv"
REPAYMENTS_FILE = DATA_DIR / "cash_loan_repayments.csv"

END_DATE = pd.Timestamp("2026-11-10")


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

    "products": [
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
    ],

    "applications": [
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
    ],

    "disbursements": [
        "disbursement_id",
        "application_id",
        "disbursement_date",
        "disbursed_amount",
        "disbursement_status",
        "failure_reason"
    ],

    "repayments": [
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
}


# --------------------------------------------------
# 3. VALIDATION REPORT HELPER
# --------------------------------------------------

validation_results = []


def record_check(check_name, passed, details=""):

    status = "PASSED" if passed else "FAILED"

    validation_results.append({
        "check": check_name,
        "passed": bool(passed),
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
        "products": PRODUCTS_FILE,
        "applications": APPLICATIONS_FILE,
        "disbursements": DISBURSEMENTS_FILE,
        "repayments": REPAYMENTS_FILE
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
            keep_default_na=False,
            low_memory=False
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
        "products": "product_id",
        "applications": "application_id",
        "disbursements": "disbursement_id",
        "repayments": "repayment_id"
    }

    for name, column in primary_keys.items():

        df = datasets[name]

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
            "registration_date",
            "customer_segment"
        ],

        "products": [
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
        ],

        "applications": [
            "application_id",
            "customer_id",
            "product_id",
            "application_date",
            "requested_amount",
            "credit_score",
            "employment_type",
            "monthly_income",
            "application_status"
        ],

        "disbursements": [
            "disbursement_id",
            "application_id",
            "disbursed_amount",
            "disbursement_status"
        ],

        "repayments": [
            "repayment_id",
            "disbursement_id",
            "installment_number",
            "due_date",
            "principal_amount",
            "interest_amount",
            "total_due_amount",
            "amount_paid",
            "repayment_status",
            "late_days"
        ]
    }

    for name, columns in required_fields.items():

        df = datasets[name]

        missing_count = 0

        for column in columns:

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
    products = datasets["products"]
    applications = datasets["applications"]
    disbursements = datasets["disbursements"]
    repayments = datasets["repayments"]

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

    # Product financial and tenure fields

    product_numeric = {
        "min_loan_amount": 0,
        "max_loan_amount": 0,
        "annual_interest_rate": 0,
        "min_tenure_months": 1,
        "max_tenure_months": 1,
        "processing_fee_percentage": 0
    }

    for column, minimum in product_numeric.items():

        values = pd.to_numeric(
            products[column],
            errors="coerce"
        )

        record_check(
            f"PRODUCT {column.upper()}",
            values.notna().all()
            and values.ge(minimum).all(),
            f"Values must be numeric and >= {minimum}"
        )

    # Application numeric fields

    for column in [
        "requested_amount",
        "credit_score",
        "monthly_income"
    ]:

        values = pd.to_numeric(
            applications[column],
            errors="coerce"
        )

        if column == "requested_amount":
            valid = values.notna().all() and values.gt(0).all()

        elif column == "credit_score":
            valid = (
                values.notna().all()
                and values.between(300, 900).all()
            )

        else:
            valid = (
                values.notna().all()
                and values.ge(0).all()
            )

        record_check(
            f"APPLICATION {column.upper()}",
            valid,
            f"Invalid values: {(~valid if isinstance(valid, bool) else False)}"
            if not valid else "Numeric validation passed"
        )

    # Approved amount can be NULL for non-approved applications.

    approved_amount = pd.to_numeric(
        applications["approved_amount"].replace("", pd.NA),
        errors="coerce"
    )

    approved_status = applications[
        "application_status"
    ].eq("APPROVED")

    approved_valid = (
        approved_amount[approved_status].notna().all()
        and approved_amount[approved_status].gt(0).all()
        and approved_amount[~approved_status].isna().all()
    )

    record_check(
        "APPLICATION APPROVED AMOUNT",
        approved_valid,
        "Approved applications require positive amounts; other statuses require NULL"
    )

    # Disbursed amount

    disbursed_amount = pd.to_numeric(
        disbursements["disbursed_amount"],
        errors="coerce"
    )

    record_check(
        "DISBURSED AMOUNT",
        disbursed_amount.notna().all()
        and disbursed_amount.gt(0).all(),
        "All disbursed amounts must be positive"
    )

    # Repayment numeric fields

    repayment_numeric = {
        "installment_number": 1,
        "principal_amount": 0,
        "interest_amount": 0,
        "total_due_amount": 0,
        "amount_paid": 0,
        "late_days": 0
    }

    for column, minimum in repayment_numeric.items():

        values = pd.to_numeric(
            repayments[column],
            errors="coerce"
        )

        record_check(
            f"REPAYMENT {column.upper()}",
            values.notna().all()
            and values.ge(minimum).all(),
            f"Values must be numeric and >= {minimum}"
        )


# --------------------------------------------------
# 9. VALIDATE FOREIGN KEYS
# --------------------------------------------------

def validate_foreign_keys(datasets):

    customers = datasets["customers"]
    products = datasets["products"]
    applications = datasets["applications"]
    disbursements = datasets["disbursements"]
    repayments = datasets["repayments"]

    customer_ids = set(customers["customer_id"])
    product_ids = set(products["product_id"])
    application_ids = set(applications["application_id"])
    disbursement_ids = set(disbursements["disbursement_id"])

    invalid_customers = (
        ~applications["customer_id"].isin(customer_ids)
    ).sum()

    invalid_products = (
        ~applications["product_id"].isin(product_ids)
    ).sum()

    invalid_applications = (
        ~disbursements["application_id"].isin(application_ids)
    ).sum()

    invalid_disbursements = (
        ~repayments["disbursement_id"].isin(disbursement_ids)
    ).sum()

    record_check(
        "APPLICATION CUSTOMER REFERENCES",
        invalid_customers == 0,
        f"Invalid references: {invalid_customers}"
    )

    record_check(
        "APPLICATION PRODUCT REFERENCES",
        invalid_products == 0,
        f"Invalid references: {invalid_products}"
    )

    record_check(
        "DISBURSEMENT APPLICATION REFERENCES",
        invalid_applications == 0,
        f"Invalid references: {invalid_applications}"
    )

    record_check(
        "REPAYMENT DISBURSEMENT REFERENCES",
        invalid_disbursements == 0,
        f"Invalid references: {invalid_disbursements}"
    )


# --------------------------------------------------
# 10. VALIDATE CATEGORIES AND STATUSES
# --------------------------------------------------

def validate_business_rules(datasets):

    customers = datasets["customers"]
    products = datasets["products"]
    applications = datasets["applications"]
    disbursements = datasets["disbursements"]
    repayments = datasets["repayments"]

    valid_segments = {
        "NEW", "REGULAR", "PREMIUM"
    }

    valid_loan_types = {
        "PERSONAL", "SALARY", "BUSINESS", "EMERGENCY"
    }

    valid_employment_types = {
        "SALARIED",
        "SELF_EMPLOYED",
        "BUSINESS_OWNER",
        "STUDENT",
        "UNEMPLOYED"
    }

    valid_application_statuses = {
        "DRAFT",
        "SUBMITTED",
        "UNDER_REVIEW",
        "APPROVED",
        "REJECTED",
        "CANCELLED"
    }

    valid_disbursement_statuses = {
        "SUCCESS", "FAILED", "PENDING"
    }

    valid_repayment_statuses = {
        "PAID", "PARTIAL", "PENDING", "OVERDUE", "FAILED"
    }

    checks = [
        (
            "CUSTOMER SEGMENTS",
            customers["customer_segment"].isin(valid_segments).all(),
            "Allowed: NEW, REGULAR, PREMIUM"
        ),
        (
            "LOAN PRODUCT TYPES",
            products["loan_type"].isin(valid_loan_types).all(),
            "Allowed: PERSONAL, SALARY, BUSINESS, EMERGENCY"
        ),
        (
            "EMPLOYMENT TYPES",
            applications["employment_type"].isin(valid_employment_types).all(),
            "Employment type must match the approved list"
        ),
        (
            "APPLICATION STATUSES",
            applications["application_status"].isin(valid_application_statuses).all(),
            "Application status must match the approved list"
        ),
        (
            "DISBURSEMENT STATUSES",
            disbursements["disbursement_status"].isin(valid_disbursement_statuses).all(),
            "Allowed: SUCCESS, FAILED, PENDING"
        ),
        (
            "REPAYMENT STATUSES",
            repayments["repayment_status"].isin(valid_repayment_statuses).all(),
            "Allowed: PAID, PARTIAL, PENDING, OVERDUE, FAILED"
        )
    ]

    for name, passed, details in checks:
        record_check(name, passed, details)

    # Product amount and tenure ranges.

    product_check = products.copy()

    for column in [
        "min_loan_amount",
        "max_loan_amount",
        "min_tenure_months",
        "max_tenure_months"
    ]:
        product_check[column] = pd.to_numeric(
            product_check[column],
            errors="coerce"
        )

    amount_range_valid = (
        product_check["max_loan_amount"]
        >= product_check["min_loan_amount"]
    ).all()

    tenure_range_valid = (
        product_check["max_tenure_months"]
        >= product_check["min_tenure_months"]
    ).all()

    record_check(
        "PRODUCT AMOUNT RANGE",
        amount_range_valid,
        "Maximum loan amount must be >= minimum loan amount"
    )

    record_check(
        "PRODUCT TENURE RANGE",
        tenure_range_valid,
        "Maximum tenure must be >= minimum tenure"
    )

    # Application amount must be within product limits.

    app_product = applications.merge(
        products[
            [
                "product_id",
                "min_loan_amount",
                "max_loan_amount"
            ]
        ],
        on="product_id",
        how="left"
    )

    requested = pd.to_numeric(
        app_product["requested_amount"],
        errors="coerce"
    )

    minimum = pd.to_numeric(
        app_product["min_loan_amount"],
        errors="coerce"
    )

    maximum = pd.to_numeric(
        app_product["max_loan_amount"],
        errors="coerce"
    )

    invalid_amounts = (
        (requested < minimum)
        | (requested > maximum)
    ).sum()

    record_check(
        "APPLICATION PRODUCT AMOUNT LIMITS",
        invalid_amounts == 0,
        f"Applications outside product limits: {invalid_amounts}"
    )

    # Approved amount must not exceed requested amount.

    approved = applications[
        applications["application_status"] == "APPROVED"
    ].copy()

    approved["requested_amount"] = pd.to_numeric(
        approved["requested_amount"],
        errors="coerce"
    )

    approved["approved_amount"] = pd.to_numeric(
        approved["approved_amount"],
        errors="coerce"
    )

    invalid_approved_amounts = (
        approved["approved_amount"]
        > approved["requested_amount"]
    ).sum()

    record_check(
        "APPROVED AMOUNT LIMIT",
        invalid_approved_amounts == 0,
        f"Approved amounts exceeding requested amounts: {invalid_approved_amounts}"
    )

    # Rejected applications must have a rejection reason.

    rejected = applications[
        applications["application_status"] == "REJECTED"
    ]

    other_applications = applications[
        applications["application_status"] != "REJECTED"
    ]

    missing_reasons = rejected[
        "rejection_reason"
    ].str.strip().eq("").sum()

    unexpected_reasons = other_applications[
        "rejection_reason"
    ].str.strip().ne("").sum()

    record_check(
        "APPLICATION REJECTION REASONS",
        missing_reasons == 0 and unexpected_reasons == 0,
        (
            f"Rejected without reason: {missing_reasons}, "
            f"Other applications with reason: {unexpected_reasons}"
        )
    )

    # Disbursement and repayment relationship uniqueness.

    duplicate_application_disbursements = (
        disbursements["application_id"].duplicated().sum()
    )

    duplicate_installments = repayments.duplicated(
        subset=["disbursement_id", "installment_number"]
    ).sum()

    record_check(
        "APPLICATION DISBURSEMENT UNIQUENESS",
        duplicate_application_disbursements == 0,
        f"Duplicate application references: {duplicate_application_disbursements}"
    )

    record_check(
        "DISBURSEMENT INSTALLMENT UNIQUENESS",
        duplicate_installments == 0,
        f"Duplicate installments: {duplicate_installments}"
    )


# --------------------------------------------------
# 11. VALIDATE FAILURE REASONS
# --------------------------------------------------

def validate_failure_reasons(datasets):

    disbursements = datasets["disbursements"]

    failed = disbursements[
        disbursements["disbursement_status"] == "FAILED"
    ]

    other_statuses = disbursements[
        disbursements["disbursement_status"] != "FAILED"
    ]

    missing_reasons = failed[
        "failure_reason"
    ].str.strip().eq("").sum()

    unexpected_reasons = other_statuses[
        "failure_reason"
    ].str.strip().ne("").sum()

    record_check(
        "DISBURSEMENT FAILURE REASONS",
        missing_reasons == 0 and unexpected_reasons == 0,
        (
            f"Failed without reason: {missing_reasons}, "
            f"Other statuses with reason: {unexpected_reasons}"
        )
    )


# --------------------------------------------------
# 12. VALIDATE DATE FIELDS
# --------------------------------------------------

def validate_dates(datasets):

    customers = datasets["customers"]
    products = datasets["products"]
    applications = datasets["applications"]
    disbursements = datasets["disbursements"]
    repayments = datasets["repayments"]

    date_columns = {
        "CUSTOMER REGISTRATION DATES": (
            customers,
            "registration_date",
            False
        ),
        "PRODUCT LAUNCH DATES": (
            products,
            "launch_date",
            False
        ),
        "APPLICATION DATES": (
            applications,
            "application_date",
            False
        ),
        "DISBURSEMENT DATES": (
            disbursements,
            "disbursement_date",
            True
        ),
        "REPAYMENT DUE DATES": (
            repayments,
            "due_date",
            False
        ),
        "REPAYMENT PAYMENT DATES": (
            repayments,
            "payment_date",
            True
        )
    }

    for name, (df, column, nullable) in date_columns.items():

        values = df[column].replace("", pd.NA)

        dates = pd.to_datetime(
            values,
            errors="coerce"
        )

        if nullable:
            passed = (
                dates.notna() | values.isna()
            ).all()
        else:
            passed = dates.notna().all()

        record_check(
            name,
            passed,
            "Date values must be valid"
        )

    # Application must occur after customer registration.

    customer_dates = customers[
        ["customer_id", "registration_date"]
    ].copy()

    customer_dates["registration_date"] = pd.to_datetime(
        customer_dates["registration_date"],
        errors="coerce"
    )

    application_dates = applications[
        ["customer_id", "application_date"]
    ].copy()

    application_dates["application_date"] = pd.to_datetime(
        application_dates["application_date"],
        errors="coerce"
    )

    merged = application_dates.merge(
        customer_dates,
        on="customer_id",
        how="left"
    )

    invalid_registration_dates = (
        merged["application_date"]
        < merged["registration_date"]
    ).sum()

    record_check(
        "APPLICATION AFTER CUSTOMER REGISTRATION",
        invalid_registration_dates == 0,
        f"Invalid applications: {invalid_registration_dates}"
    )

    # Application must occur after product launch.

    product_dates = products[
        ["product_id", "launch_date"]
    ].copy()

    product_dates["launch_date"] = pd.to_datetime(
        product_dates["launch_date"],
        errors="coerce"
    )

    application_products = applications[
        ["product_id", "application_date"]
    ].copy()

    application_products["application_date"] = pd.to_datetime(
        application_products["application_date"],
        errors="coerce"
    )

    merged = application_products.merge(
        product_dates,
        on="product_id",
        how="left"
    )

    invalid_launch_dates = (
        merged["application_date"]
        < merged["launch_date"]
    ).sum()

    record_check(
        "APPLICATION AFTER PRODUCT LAUNCH",
        invalid_launch_dates == 0,
        f"Invalid applications: {invalid_launch_dates}"
    )

    # Disbursement must not precede application.

    app_dates = applications[
        ["application_id", "application_date"]
    ].copy()

    app_dates["application_date"] = pd.to_datetime(
        app_dates["application_date"],
        errors="coerce"
    )

    disb_dates = disbursements[
        [
            "application_id",
            "disbursement_date",
            "disbursement_status"
        ]
    ].copy()

    disb_dates["disbursement_date"] = pd.to_datetime(
        disb_dates["disbursement_date"].replace("", pd.NA),
        errors="coerce"
    )

    merged = disb_dates.merge(
        app_dates,
        on="application_id",
        how="left"
    )

    successful = merged[
        merged["disbursement_status"] == "SUCCESS"
    ]

    invalid_disbursement_dates = (
        successful["disbursement_date"]
        < successful["application_date"]
    ).sum()

    record_check(
        "DISBURSEMENT AFTER APPLICATION",
        invalid_disbursement_dates == 0,
        f"Invalid disbursement dates: {invalid_disbursement_dates}"
    )

    # Payment date must not precede due date or exceed the cutoff.

    repayment_dates = repayments.copy()

    repayment_dates["due_date"] = pd.to_datetime(
        repayment_dates["due_date"],
        errors="coerce"
    )

    repayment_dates["payment_date"] = pd.to_datetime(
        repayment_dates["payment_date"].replace("", pd.NA),
        errors="coerce"
    )

    payment_exists = repayment_dates["payment_date"].notna()

    invalid_payment_dates = (
        payment_exists
        & (
            (repayment_dates["payment_date"] < repayment_dates["due_date"])
            | (repayment_dates["payment_date"] > END_DATE)
        )
    ).sum()

    record_check(
        "REPAYMENT PAYMENT DATE VALIDITY",
        invalid_payment_dates == 0,
        f"Invalid payment dates: {invalid_payment_dates}"
    )

    # All generated repayment due dates must be valid.

    invalid_due_dates = (
        repayment_dates["due_date"] < repayment_dates["due_date"].min()
    ).sum()

    record_check(
        "REPAYMENT DUE DATE CONSISTENCY",
        invalid_due_dates == 0,
        f"Invalid due dates: {invalid_due_dates}"
    )


# --------------------------------------------------
# 13. VALIDATE APPLICATION AND DISBURSEMENT LINKAGE
# --------------------------------------------------

def validate_disbursement_linkage(datasets):

    applications = datasets["applications"]
    disbursements = datasets["disbursements"]

    approved_applications = applications[
        applications["application_status"] == "APPROVED"
    ]

    non_approved_applications = applications[
        applications["application_status"] != "APPROVED"
    ]

    approved_ids = set(
        approved_applications["application_id"]
    )

    disbursed_ids = set(
        disbursements["application_id"]
    )

    invalid_disbursements = (
        ~disbursements["application_id"].isin(approved_ids)
    ).sum()

    missing_disbursements = (
        ~approved_applications["application_id"].isin(disbursed_ids)
    ).sum()

    unexpected_disbursements = (
        non_approved_applications["application_id"].isin(disbursed_ids)
    ).sum()

    record_check(
        "DISBURSEMENT APPROVAL ELIGIBILITY",
        invalid_disbursements == 0,
        f"Disbursements for non-approved applications: {invalid_disbursements}"
    )

    record_check(
        "APPROVED APPLICATION DISBURSEMENT COVERAGE",
        missing_disbursements == 0,
        f"Approved applications without disbursement: {missing_disbursements}"
    )

    record_check(
        "NON-APPROVED APPLICATION DISBURSEMENT",
        unexpected_disbursements == 0,
        f"Unexpected disbursements: {unexpected_disbursements}"
    )

    # Disbursed amount must equal approved amount.

    amount_check = disbursements.merge(
        approved_applications[
            ["application_id", "approved_amount"]
        ],
        on="application_id",
        how="left"
    )

    amount_check["disbursed_amount"] = pd.to_numeric(
        amount_check["disbursed_amount"],
        errors="coerce"
    )

    amount_check["approved_amount"] = pd.to_numeric(
        amount_check["approved_amount"],
        errors="coerce"
    )

    mismatches = (
        (
            amount_check["disbursed_amount"]
            - amount_check["approved_amount"]
        ).abs() > 0.01
    ).sum()

    record_check(
        "DISBURSED AMOUNT APPROVAL MATCH",
        mismatches == 0,
        f"Amount mismatches: {mismatches}"
    )


# --------------------------------------------------
# 14. VALIDATE DISBURSEMENT STATUS RULES
# --------------------------------------------------

def validate_disbursement_status_rules(disbursements):

    successful = disbursements[
        disbursements["disbursement_status"] == "SUCCESS"
    ]

    failed = disbursements[
        disbursements["disbursement_status"] == "FAILED"
    ]

    pending = disbursements[
        disbursements["disbursement_status"] == "PENDING"
    ]

    success_dates_missing = successful[
        "disbursement_date"
    ].str.strip().eq("").sum()

    success_reasons_present = successful[
        "failure_reason"
    ].str.strip().ne("").sum()

    failed_reasons_missing = failed[
        "failure_reason"
    ].str.strip().eq("").sum()

    failed_dates = failed[
        "disbursement_date"
    ].str.strip().ne("").sum()

    pending_dates = pending[
        "disbursement_date"
    ].str.strip().ne("").sum()

    pending_reasons = pending[
        "failure_reason"
    ].str.strip().ne("").sum()

    record_check(
        "SUCCESSFUL DISBURSEMENT STATUS RULES",
        (
            success_dates_missing == 0
            and success_reasons_present == 0
        ),
        (
            f"Missing dates: {success_dates_missing}, "
            f"Unexpected failure reasons: {success_reasons_present}"
        )
    )

    record_check(
        "FAILED DISBURSEMENT STATUS RULES",
        (
            failed_reasons_missing == 0
            and failed_dates == 0
        ),
        (
            f"Missing failure reasons: {failed_reasons_missing}, "
            f"Unexpected dates: {failed_dates}"
        )
    )

    record_check(
        "PENDING DISBURSEMENT STATUS RULES",
        (
            pending_dates == 0
            and pending_reasons == 0
        ),
        (
            f"Unexpected dates: {pending_dates}, "
            f"Unexpected failure reasons: {pending_reasons}"
        )
    )


# --------------------------------------------------
# 15. VALIDATE REPAYMENT STATUS RULES
# --------------------------------------------------

def validate_repayment_status_rules(repayments):

    df = repayments.copy()

    df["amount_paid"] = pd.to_numeric(
        df["amount_paid"],
        errors="coerce"
    )

    df["total_due_amount"] = pd.to_numeric(
        df["total_due_amount"],
        errors="coerce"
    )

    df["payment_date"] = df["payment_date"].replace(
        "",
        pd.NA
    )

    paid = df["repayment_status"] == "PAID"
    partial = df["repayment_status"] == "PARTIAL"
    pending = df["repayment_status"] == "PENDING"
    overdue = df["repayment_status"] == "OVERDUE"
    failed = df["repayment_status"] == "FAILED"

    paid_invalid = (
        paid
        & (
            df["payment_date"].isna()
            | (
                (df["amount_paid"] - df["total_due_amount"]).abs()
                >= 0.01
            )
        )
    ).sum()

    partial_invalid = (
        partial
        & (
            df["payment_date"].isna()
            | (df["amount_paid"] <= 0)
            | (df["amount_paid"] >= df["total_due_amount"])
        )
    ).sum()

    unpaid_invalid = (
        (pending | overdue)
        & (
            df["payment_date"].notna()
            | (df["amount_paid"] != 0)
        )
    ).sum()

    failed_invalid = (
        failed
        & (
            df["amount_paid"] != 0
        )
    ).sum()

    record_check(
        "PAID REPAYMENT STATUS RULES",
        paid_invalid == 0,
        f"Invalid PAID records: {paid_invalid}"
    )

    record_check(
        "PARTIAL REPAYMENT STATUS RULES",
        partial_invalid == 0,
        f"Invalid PARTIAL records: {partial_invalid}"
    )

    record_check(
        "PENDING AND OVERDUE REPAYMENT RULES",
        unpaid_invalid == 0,
        f"Invalid unpaid records: {unpaid_invalid}"
    )

    record_check(
        "FAILED REPAYMENT STATUS RULES",
        failed_invalid == 0,
        f"Invalid FAILED records: {failed_invalid}"
    )


# --------------------------------------------------
# 16. VALIDATE REPAYMENT FINANCIAL CALCULATIONS
# --------------------------------------------------

def validate_repayment_calculations(repayments):

    df = repayments.copy()

    for column in [
        "principal_amount",
        "interest_amount",
        "total_due_amount",
        "amount_paid"
    ]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    calculated_total = (
        df["principal_amount"]
        + df["interest_amount"]
    )

    total_difference = (
        df["total_due_amount"]
        - calculated_total
    ).abs()

    invalid_totals = (
        total_difference >= 0.01
    ).sum()

    record_check(
        "REPAYMENT PRINCIPAL AND INTEREST",
        invalid_totals == 0,
        f"Total due calculation mismatches: {invalid_totals}"
    )

    invalid_paid_amounts = (
        df["amount_paid"]
        > df["total_due_amount"]
    ).sum()

    record_check(
        "REPAYMENT AMOUNT PAID LIMIT",
        invalid_paid_amounts == 0,
        f"Payments exceeding total due: {invalid_paid_amounts}"
    )


# --------------------------------------------------
# 17. VALIDATE REPAYMENT DISBURSEMENT LINKAGE
# --------------------------------------------------

def validate_repayment_linkage(datasets):

    disbursements = datasets["disbursements"]
    repayments = datasets["repayments"]

    successful_disbursements = disbursements[
        disbursements["disbursement_status"] == "SUCCESS"
    ]

    successful_ids = set(
        successful_disbursements["disbursement_id"]
    )

    repayment_ids = set(
        repayments["disbursement_id"]
    )

    invalid_repayments = (
        ~repayments["disbursement_id"].isin(successful_ids)
    ).sum()

    missing_schedules = (
        ~successful_disbursements["disbursement_id"].isin(repayment_ids)
    ).sum()

    record_check(
        "REPAYMENT SUCCESSFUL DISBURSEMENT REFERENCES",
        invalid_repayments == 0,
        f"Repayments linked to unsuccessful disbursements: {invalid_repayments}"
    )

    record_check(
        "SUCCESSFUL DISBURSEMENT REPAYMENT COVERAGE",
        missing_schedules == 0,
        f"Successful disbursements without repayment schedules: {missing_schedules}"
    )

    # Total scheduled principal must equal disbursed amount.

    repayment_principal = repayments.copy()

    repayment_principal["principal_amount"] = pd.to_numeric(
        repayment_principal["principal_amount"],
        errors="coerce"
    )

    principal_totals = (
        repayment_principal
        .groupby("disbursement_id")["principal_amount"]
        .sum()
        .reset_index()
    )

    comparison = successful_disbursements[
        ["disbursement_id", "disbursed_amount"]
    ].merge(
        principal_totals,
        on="disbursement_id",
        how="left"
    )

    comparison["disbursed_amount"] = pd.to_numeric(
        comparison["disbursed_amount"],
        errors="coerce"
    )

    comparison["principal_amount"] = comparison[
        "principal_amount"
    ].fillna(0)

    invalid_principal_totals = (
        (
            comparison["disbursed_amount"]
            - comparison["principal_amount"]
        ).abs() > 0.02
    ).sum()

    record_check(
        "TOTAL REPAYMENT PRINCIPAL MATCH",
        invalid_principal_totals == 0,
        f"Principal total mismatches: {invalid_principal_totals}"
    )


# --------------------------------------------------
# 18. VALIDATE REPAYMENT INSTALLMENT SEQUENCES
# --------------------------------------------------

def validate_installment_sequences(repayments):

    df = repayments.copy()

    df["installment_number"] = pd.to_numeric(
        df["installment_number"],
        errors="coerce"
    )

    invalid_sequences = 0

    for _, group in df.groupby("disbursement_id"):

        installments = sorted(
            group["installment_number"].tolist()
        )

        expected = list(
            range(1, len(installments) + 1)
        )

        if installments != expected:
            invalid_sequences += 1

    record_check(
        "REPAYMENT INSTALLMENT SEQUENCES",
        invalid_sequences == 0,
        f"Disbursements with invalid sequences: {invalid_sequences}"
    )


# --------------------------------------------------
# 19. VALIDATE CUSTOMER AND PRODUCT DATE RELATIONSHIPS
# --------------------------------------------------

def validate_application_dates(datasets):

    applications = datasets["applications"].copy()
    customers = datasets["customers"].copy()

    applications["application_date"] = pd.to_datetime(
        applications["application_date"],
        errors="coerce"
    )

    customers["registration_date"] = pd.to_datetime(
        customers["registration_date"],
        errors="coerce"
    )

    merged = applications.merge(
        customers[
            ["customer_id", "registration_date"]
        ],
        on="customer_id",
        how="left"
    )

    invalid_dates = (
        merged["application_date"]
        < merged["registration_date"]
    ).sum()

    record_check(
        "APPLICATION CUSTOMER DATE CONSISTENCY",
        invalid_dates == 0,
        f"Invalid date relationships: {invalid_dates}"
    )


# --------------------------------------------------
# 20. FINAL VALIDATION SUMMARY
# --------------------------------------------------

def print_summary():

    total_checks = len(validation_results)

    passed_checks = sum(
        result["passed"]
        for result in validation_results
    )

    failed_checks = total_checks - passed_checks

    print("\n" + "=" * 65)
    print("CASH LOANS DATA QUALITY SUMMARY")
    print("=" * 65)

    print(f"Total checks : {total_checks}")
    print(f"Passed       : {passed_checks}")
    print(f"Failed       : {failed_checks}")

    print("=" * 65)

    if failed_checks == 0:

        print(
            "ALL CASH LOANS DATA QUALITY CHECKS PASSED!"
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
# 21. MAIN EXECUTION
# --------------------------------------------------

def main():

    print("=" * 65)
    print("FINTECH 360 - CASH LOANS DATA QUALITY VALIDATION")
    print("=" * 65)

    try:

        datasets = load_datasets()

        print("\nStarting validation...\n")

        validate_schemas(datasets)

        # Stop if any required columns are missing.

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

        validate_failure_reasons(datasets)

        validate_dates(datasets)

        validate_disbursement_linkage(datasets)

        validate_disbursement_status_rules(
            datasets["disbursements"]
        )

        validate_repayment_status_rules(
            datasets["repayments"]
        )

        validate_repayment_calculations(
            datasets["repayments"]
        )

        validate_repayment_linkage(datasets)

        validate_installment_sequences(
            datasets["repayments"]
        )

        validate_application_dates(datasets)

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
# 22. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()
