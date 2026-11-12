
-- ============================================================
-- FINTECH 360 - CASH LOANS DATABASE SCHEMA
-- ============================================================


-- 1. CUSTOMERS

CREATE TABLE IF NOT EXISTS cl_customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,

    age INTEGER NOT NULL
        CHECK (age BETWEEN 18 AND 100),

    gender TEXT,
    city TEXT,
    registration_date TEXT NOT NULL,

    customer_segment TEXT NOT NULL
        CHECK (
            customer_segment IN (
                'NEW',
                'REGULAR',
                'PREMIUM'
            )
        )
);


-- 2. LOAN PRODUCTS

CREATE TABLE IF NOT EXISTS cl_loan_products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,

    loan_type TEXT NOT NULL
        CHECK (
            loan_type IN (
                'PERSONAL',
                'SALARY',
                'BUSINESS',
                'EMERGENCY'
            )
        ),

    min_loan_amount REAL NOT NULL
        CHECK (min_loan_amount > 0),

    max_loan_amount REAL NOT NULL
        CHECK (max_loan_amount >= min_loan_amount),

    annual_interest_rate REAL NOT NULL
        CHECK (annual_interest_rate >= 0),

    min_tenure_months INTEGER NOT NULL
        CHECK (min_tenure_months > 0),

    max_tenure_months INTEGER NOT NULL
        CHECK (max_tenure_months >= min_tenure_months),

    processing_fee_percentage REAL NOT NULL
        CHECK (processing_fee_percentage >= 0),

    launch_date TEXT NOT NULL
);


-- 3. LOAN APPLICATIONS

CREATE TABLE IF NOT EXISTS cl_loan_applications (
    application_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    application_date TEXT NOT NULL,

    requested_amount REAL NOT NULL
        CHECK (requested_amount > 0),

    approved_amount REAL
        CHECK (
            approved_amount IS NULL
            OR approved_amount > 0
        ),

    credit_score INTEGER
        CHECK (
            credit_score IS NULL
            OR credit_score BETWEEN 300 AND 900
        ),

    employment_type TEXT NOT NULL
        CHECK (
            employment_type IN (
                'SALARIED',
                'SELF_EMPLOYED',
                'BUSINESS_OWNER',
                'STUDENT',
                'UNEMPLOYED'
            )
        ),

    monthly_income REAL
        CHECK (
            monthly_income IS NULL
            OR monthly_income >= 0
        ),

    application_status TEXT NOT NULL
        CHECK (
            application_status IN (
                'DRAFT',
                'SUBMITTED',
                'UNDER_REVIEW',
                'APPROVED',
                'REJECTED',
                'CANCELLED'
            )
        ),

    rejection_reason TEXT,

    FOREIGN KEY (customer_id)
        REFERENCES cl_customers(customer_id),

    FOREIGN KEY (product_id)
        REFERENCES cl_loan_products(product_id),

    CHECK (
        application_status != 'APPROVED'
        OR approved_amount IS NOT NULL
    ),

    CHECK (
        (application_status = 'REJECTED'
            AND rejection_reason IS NOT NULL)
        OR
        (application_status != 'REJECTED'
            AND rejection_reason IS NULL)
    ),

    CHECK (
        approved_amount IS NULL
        OR approved_amount <= requested_amount
    )
);


-- 4. LOAN DISBURSEMENTS

CREATE TABLE IF NOT EXISTS cl_loan_disbursements (
    disbursement_id TEXT PRIMARY KEY,

    application_id TEXT NOT NULL UNIQUE,

    disbursement_date TEXT,

    disbursed_amount REAL NOT NULL
        CHECK (disbursed_amount > 0),

    disbursement_status TEXT NOT NULL
        CHECK (
            disbursement_status IN (
                'SUCCESS',
                'FAILED',
                'PENDING'
            )
        ),

    failure_reason TEXT,

    FOREIGN KEY (application_id)
        REFERENCES cl_loan_applications(application_id),

    CHECK (
        (disbursement_status = 'SUCCESS'
            AND disbursement_date IS NOT NULL
            AND failure_reason IS NULL)
        OR
        (disbursement_status = 'FAILED'
            AND failure_reason IS NOT NULL)
        OR
        (disbursement_status = 'PENDING'
            AND failure_reason IS NULL)
    )
);


-- 5. LOAN REPAYMENTS

CREATE TABLE IF NOT EXISTS cl_loan_repayments (
    repayment_id TEXT PRIMARY KEY,

    disbursement_id TEXT NOT NULL,

    installment_number INTEGER NOT NULL
        CHECK (installment_number > 0),

    due_date TEXT NOT NULL,

    payment_date TEXT,

    principal_amount REAL NOT NULL
        CHECK (principal_amount >= 0),

    interest_amount REAL NOT NULL
        CHECK (interest_amount >= 0),

    total_due_amount REAL NOT NULL
        CHECK (total_due_amount > 0),

    amount_paid REAL NOT NULL DEFAULT 0
        CHECK (amount_paid >= 0),

    repayment_status TEXT NOT NULL
        CHECK (
            repayment_status IN (
                'PAID',
                'PARTIAL',
                'PENDING',
                'OVERDUE',
                'FAILED'
            )
        ),

    late_days INTEGER NOT NULL DEFAULT 0
        CHECK (late_days >= 0),

    FOREIGN KEY (disbursement_id)
        REFERENCES cl_loan_disbursements(disbursement_id),

    UNIQUE (disbursement_id, installment_number),

    CHECK (
        ABS(
            total_due_amount -
            (principal_amount + interest_amount)
        ) < 0.01
    ),

    CHECK (amount_paid <= total_due_amount),

    CHECK (
        (repayment_status = 'PAID'
            AND payment_date IS NOT NULL
            AND ABS(amount_paid - total_due_amount) < 0.01)
        OR
        (repayment_status = 'PARTIAL'
            AND payment_date IS NOT NULL
            AND amount_paid > 0
            AND amount_paid < total_due_amount)
        OR
        (repayment_status IN ('PENDING', 'OVERDUE')
            AND amount_paid = 0
            AND payment_date IS NULL)
        OR
        (repayment_status = 'FAILED'
            AND amount_paid = 0)
    )
);


-- ============================================================
-- INDEXES FOR COMMON ANALYTICAL QUERIES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_cl_applications_customer
ON cl_loan_applications(customer_id);

CREATE INDEX IF NOT EXISTS idx_cl_applications_product
ON cl_loan_applications(product_id);

CREATE INDEX IF NOT EXISTS idx_cl_applications_date
ON cl_loan_applications(application_date);

CREATE INDEX IF NOT EXISTS idx_cl_applications_status
ON cl_loan_applications(application_status);

CREATE INDEX IF NOT EXISTS idx_cl_disbursements_application
ON cl_loan_disbursements(application_id);

CREATE INDEX IF NOT EXISTS idx_cl_disbursements_date
ON cl_loan_disbursements(disbursement_date);

CREATE INDEX IF NOT EXISTS idx_cl_repayments_disbursement
ON cl_loan_repayments(disbursement_id);

CREATE INDEX IF NOT EXISTS idx_cl_repayments_due_date
ON cl_loan_repayments(due_date);

CREATE INDEX IF NOT EXISTS idx_cl_repayments_status
ON cl_loan_repayments(repayment_status);
