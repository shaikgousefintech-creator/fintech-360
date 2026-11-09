
CREATE TABLE IF NOT EXISTS upi_transactions (

    transaction_id TEXT PRIMARY KEY,

    payer_id TEXT NOT NULL,
    payee_id TEXT NOT NULL,

    transaction_type TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,

    transaction_timestamp TEXT NOT NULL,
    transaction_date TEXT NOT NULL,

    status TEXT NOT NULL,

    payer_bank TEXT,
    payee_bank TEXT,
    payment_app TEXT,

    failure_reason TEXT,
    merchant_name TEXT,

    transaction_year INTEGER,
    transaction_month INTEGER,
    transaction_day INTEGER,
    transaction_hour INTEGER,
    transaction_day_of_week TEXT,

    is_successful INTEGER,
    is_failed INTEGER,
    is_pending INTEGER
);
