
-- FINTECH 360
-- MUTUAL FUNDS ANALYTICAL DATA MARTS


-- ==================================================
-- 1. INVESTOR PERFORMANCE MART
-- ==================================================

CREATE VIEW IF NOT EXISTS mart_mf_investor_performance AS

SELECT
    i.investor_id,
    i.investor_name,
    i.investor_segment,
    i.city,

    COUNT(t.investment_id) AS total_transactions,

    SUM(CASE
        WHEN t.transaction_status = 'SUCCESS' THEN 1
        ELSE 0
    END) AS successful_transactions,

    SUM(CASE
        WHEN t.transaction_status = 'FAILED' THEN 1
        ELSE 0
    END) AS failed_transactions,

    ROUND(SUM(CASE
        WHEN t.transaction_status = 'SUCCESS'
         AND t.transaction_type = 'PURCHASE'
        THEN t.amount
        ELSE 0
    END), 2) AS total_purchase_amount,

    ROUND(SUM(CASE
        WHEN t.transaction_status = 'SUCCESS'
         AND t.transaction_type = 'REDEMPTION'
        THEN t.amount
        ELSE 0
    END), 2) AS total_redemption_amount,

    ROUND(
        SUM(CASE
            WHEN t.transaction_status = 'SUCCESS'
             AND t.transaction_type = 'PURCHASE'
            THEN t.amount
            WHEN t.transaction_status = 'SUCCESS'
             AND t.transaction_type = 'REDEMPTION'
            THEN -t.amount
            ELSE 0
        END), 2
    ) AS net_investment_amount

FROM mf_investors i

LEFT JOIN mf_transactions t
    ON i.investor_id = t.investor_id

GROUP BY
    i.investor_id,
    i.investor_name,
    i.investor_segment,
    i.city;


-- ==================================================
-- 2. SCHEME PERFORMANCE MART
-- ==================================================

CREATE VIEW IF NOT EXISTS mart_mf_scheme_performance AS

SELECT
    s.scheme_id,
    s.scheme_name,
    s.fund_house,
    s.fund_category,
    s.risk_level,
    s.expense_ratio,

    COUNT(t.investment_id) AS total_transactions,

    SUM(CASE
        WHEN t.transaction_status = 'SUCCESS' THEN 1
        ELSE 0
    END) AS successful_transactions,

    SUM(CASE
        WHEN t.transaction_status = 'FAILED' THEN 1
        ELSE 0
    END) AS failed_transactions,

    ROUND(SUM(CASE
        WHEN t.transaction_status = 'SUCCESS'
         AND t.transaction_type = 'PURCHASE'
        THEN t.amount
        ELSE 0
    END), 2) AS total_purchase_amount,

    ROUND(SUM(CASE
        WHEN t.transaction_status = 'SUCCESS'
         AND t.transaction_type = 'REDEMPTION'
        THEN t.amount
        ELSE 0
    END), 2) AS total_redemption_amount,

    ROUND(
        100.0 * SUM(CASE
            WHEN t.transaction_status = 'SUCCESS' THEN 1
            ELSE 0
        END) / NULLIF(COUNT(t.investment_id), 0),
        2
    ) AS success_rate_percentage

FROM mf_schemes s

LEFT JOIN mf_transactions t
    ON s.scheme_id = t.scheme_id

GROUP BY
    s.scheme_id,
    s.scheme_name,
    s.fund_house,
    s.fund_category,
    s.risk_level,
    s.expense_ratio;


-- ==================================================
-- 3. DAILY PERFORMANCE MART
-- ==================================================

CREATE VIEW IF NOT EXISTS mart_mf_daily_performance AS

SELECT
    transaction_date,

    COUNT(*) AS total_transactions,

    SUM(CASE
        WHEN transaction_status = 'SUCCESS' THEN 1
        ELSE 0
    END) AS successful_transactions,

    SUM(CASE
        WHEN transaction_status = 'FAILED' THEN 1
        ELSE 0
    END) AS failed_transactions,

    SUM(CASE
        WHEN transaction_type = 'PURCHASE'
         AND transaction_status = 'SUCCESS'
        THEN 1
        ELSE 0
    END) AS successful_purchases,

    SUM(CASE
        WHEN transaction_type = 'REDEMPTION'
         AND transaction_status = 'SUCCESS'
        THEN 1
        ELSE 0
    END) AS successful_redemptions,

    ROUND(SUM(CASE
        WHEN transaction_status = 'SUCCESS'
        THEN amount
        ELSE 0
    END), 2) AS total_successful_transaction_amount,

    ROUND(SUM(CASE
        WHEN transaction_status = 'SUCCESS'
         AND transaction_type = 'PURCHASE'
        THEN amount
        ELSE 0
    END), 2) AS total_purchase_amount,

    ROUND(SUM(CASE
        WHEN transaction_status = 'SUCCESS'
         AND transaction_type = 'REDEMPTION'
        THEN amount
        ELSE 0
    END), 2) AS total_redemption_amount,

    ROUND(
        100.0 * SUM(CASE
            WHEN transaction_status = 'SUCCESS' THEN 1
            ELSE 0
        END) / COUNT(*),
        2
    ) AS success_rate_percentage

FROM mf_transactions

GROUP BY transaction_date;


-- ==================================================
-- 4. FUND CATEGORY PERFORMANCE MART
-- ==================================================

CREATE VIEW IF NOT EXISTS mart_mf_category_performance AS

SELECT
    s.fund_category,

    COUNT(t.investment_id) AS total_transactions,

    SUM(CASE
        WHEN t.transaction_status = 'SUCCESS' THEN 1
        ELSE 0
    END) AS successful_transactions,

    SUM(CASE
        WHEN t.transaction_status = 'FAILED' THEN 1
        ELSE 0
    END) AS failed_transactions,

    ROUND(SUM(CASE
        WHEN t.transaction_status = 'SUCCESS'
         AND t.transaction_type = 'PURCHASE'
        THEN t.amount
        ELSE 0
    END), 2) AS total_purchase_amount,

    ROUND(SUM(CASE
        WHEN t.transaction_status = 'SUCCESS'
         AND t.transaction_type = 'REDEMPTION'
        THEN t.amount
        ELSE 0
    END), 2) AS total_redemption_amount,

    ROUND(
        100.0 * SUM(CASE
            WHEN t.transaction_status = 'SUCCESS' THEN 1
            ELSE 0
        END) / NULLIF(COUNT(t.investment_id), 0),
        2
    ) AS success_rate_percentage

FROM mf_schemes s

LEFT JOIN mf_transactions t
    ON s.scheme_id = t.scheme_id

GROUP BY s.fund_category;
