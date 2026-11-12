
-- =========================================================
-- FINTECH 360°
-- DIGITAL GOLD MODULE
-- DATABASE TABLE CREATION
-- =========================================================

PRAGMA foreign_keys = ON;

-- =========================================================
-- 1. DIGITAL GOLD CUSTOMERS
-- =========================================================

CREATE TABLE IF NOT EXISTS dg_customers (

    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    city TEXT,
    registration_date TEXT,
    customer_segment TEXT

);

-- =========================================================
-- 2. DIGITAL GOLD PRICE HISTORY
-- =========================================================

CREATE TABLE IF NOT EXISTS dg_price_history (

    price_id TEXT PRIMARY KEY,
    price_date TEXT NOT NULL,
    gold_price_per_gram REAL NOT NULL,
    buy_price_per_gram REAL NOT NULL,
    sell_price_per_gram REAL NOT NULL

);

-- =========================================================
-- 3. DIGITAL GOLD TRANSACTIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS dg_transactions (

    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    investment_mode TEXT,
    gold_quantity_grams REAL NOT NULL,
    gold_price_per_gram REAL NOT NULL,
    amount REAL NOT NULL,
    transaction_status TEXT NOT NULL,
    failure_reason TEXT,

    FOREIGN KEY (customer_id)
        REFERENCES dg_customers(customer_id),

    CHECK (
        transaction_type IN ('BUY', 'SELL')
    ),

    CHECK (
        transaction_status IN (
            'SUCCESS',
            'FAILED',
            'PENDING'
        )
    ),

    CHECK (gold_quantity_grams > 0),
    CHECK (gold_price_per_gram > 0),
    CHECK (amount > 0)

);

-- =========================================================
-- 4. DIGITAL GOLD WALLET LEDGER
-- =========================================================

CREATE TABLE IF NOT EXISTS dg_wallet_ledger (

    ledger_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    transaction_id TEXT NOT NULL UNIQUE,
    entry_date TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    gold_quantity_grams REAL NOT NULL,
    balance_after_grams REAL NOT NULL,

    FOREIGN KEY (customer_id)
        REFERENCES dg_customers(customer_id),

    FOREIGN KEY (transaction_id)
        REFERENCES dg_transactions(transaction_id),

    CHECK (
        transaction_type IN ('CREDIT', 'DEBIT')
    ),

    CHECK (gold_quantity_grams > 0),
    CHECK (balance_after_grams >= 0)

);

-- =========================================================
-- 5. INDEX CREATION
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_dg_transactions_customer
ON dg_transactions(customer_id);

CREATE INDEX IF NOT EXISTS idx_dg_transactions_date
ON dg_transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_dg_transactions_type
ON dg_transactions(transaction_type);

CREATE INDEX IF NOT EXISTS idx_dg_transactions_status
ON dg_transactions(transaction_status);

CREATE INDEX IF NOT EXISTS idx_dg_price_date
ON dg_price_history(price_date);

CREATE INDEX IF NOT EXISTS idx_dg_ledger_customer
ON dg_wallet_ledger(customer_id);

CREATE INDEX IF NOT EXISTS idx_dg_ledger_date
ON dg_wallet_ledger(entry_date);

-- =========================================================
-- END OF DIGITAL GOLD SCHEMA
-- =========================================================
