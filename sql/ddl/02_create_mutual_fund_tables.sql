
-- FINTECH 360 - MUTUAL FUNDS DATABASE SCHEMA

-- 1. INVESTORS
CREATE TABLE IF NOT EXISTS mf_investors (
    investor_id TEXT PRIMARY KEY,
    investor_name TEXT NOT NULL,
    age INTEGER NOT NULL CHECK (age BETWEEN 18 AND 100),
    gender TEXT,
    city TEXT,
    registration_date TEXT NOT NULL,
    investor_segment TEXT NOT NULL
        CHECK (investor_segment IN ('RETAIL', 'HNI'))
);

-- 2. MUTUAL FUND SCHEMES
CREATE TABLE IF NOT EXISTS mf_schemes (
    scheme_id TEXT PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    fund_category TEXT NOT NULL
        CHECK (fund_category IN ('EQUITY', 'DEBT', 'HYBRID', 'INDEX')),
    risk_level TEXT NOT NULL
        CHECK (risk_level IN ('LOW', 'MODERATE', 'HIGH')),
    benchmark TEXT,
    expense_ratio REAL NOT NULL CHECK (expense_ratio >= 0),
    launch_date TEXT NOT NULL
);

-- 3. HISTORICAL NAV
CREATE TABLE IF NOT EXISTS mf_nav_history (
    nav_id TEXT PRIMARY KEY,
    scheme_id TEXT NOT NULL,
    nav_date TEXT NOT NULL,
    nav_value REAL NOT NULL CHECK (nav_value > 0),

    FOREIGN KEY (scheme_id)
        REFERENCES mf_schemes(scheme_id),

    UNIQUE (scheme_id, nav_date)
);

-- 4. INVESTMENT TRANSACTIONS
CREATE TABLE IF NOT EXISTS mf_transactions (
    investment_id TEXT PRIMARY KEY,
    investor_id TEXT NOT NULL,
    scheme_id TEXT NOT NULL,
    transaction_date TEXT NOT NULL,

    transaction_type TEXT NOT NULL
        CHECK (transaction_type IN ('PURCHASE', 'REDEMPTION')),

    investment_mode TEXT NOT NULL
        CHECK (investment_mode IN ('SIP', 'LUMP_SUM', 'NOT_APPLICABLE')),

    amount REAL NOT NULL CHECK (amount > 0),
    nav REAL NOT NULL CHECK (nav > 0),
    units REAL NOT NULL CHECK (units > 0),

    transaction_status TEXT NOT NULL
        CHECK (transaction_status IN ('SUCCESS', 'FAILED')),

    failure_reason TEXT,

    FOREIGN KEY (investor_id)
        REFERENCES mf_investors(investor_id),

    FOREIGN KEY (scheme_id)
        REFERENCES mf_schemes(scheme_id),

    CHECK (
        (transaction_type = 'PURCHASE'
            AND investment_mode IN ('SIP', 'LUMP_SUM'))
        OR
        (transaction_type = 'REDEMPTION'
            AND investment_mode = 'NOT_APPLICABLE')
    ),

    CHECK (
        (transaction_status = 'FAILED'
            AND failure_reason IS NOT NULL)
        OR
        (transaction_status = 'SUCCESS'
            AND failure_reason IS NULL)
    )
);

-- INDEXES FOR COMMON ANALYTICAL QUERIES

CREATE INDEX IF NOT EXISTS idx_mf_transactions_investor
ON mf_transactions(investor_id);

CREATE INDEX IF NOT EXISTS idx_mf_transactions_scheme
ON mf_transactions(scheme_id);

CREATE INDEX IF NOT EXISTS idx_mf_transactions_date
ON mf_transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_mf_nav_scheme_date
ON mf_nav_history(scheme_id, nav_date);
