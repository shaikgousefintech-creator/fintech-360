
-- FINTECH 360
-- DIGITAL GOLD ANALYTICAL DATA MARTS


-- ==================================================
-- 1. CUSTOMER PERFORMANCE MART
-- ==================================================

CREATE VIEW IF NOT EXISTS mart_dg_customer_performance AS

SELECT
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.city,

    COUNT(t.transaction_id) AS total_transactions,

    SUM(CASE
        WHEN t.transaction_status = 'SUCCESS' THEN 1
        ELSE 0
    END) AS successful_transactions,

    SUM(CASE
        WHEN t.transaction_status = 'FAILED' THEN 1
        ELSE 0
    END) AS failed_transactions,

    SUM(CASE
        WHEN t.transaction_status = 'PENDING' THEN 1
        ELSE 0
    END) AS pending_transactions,

    ROUND(SUM(CASE
        WHEN t.transaction_status = 'SUCCESS'
         AND t.transaction_type = 'BUY'
        THEN t.amount
        ELSE 0
    END), 2) AS total_buy_amount,

    ROUND(SUM(CASE
        WHEN t.transaction_status = 'SUCCESS'
         AND t.transaction_type = 'SELL'
        THEN t.amount
        ELSE 0
    END), 2) AS total_sell_amount,

    ROUND(SUM(CASE
        WHEN t.transaction_status = 'SUCCESS'
         AND t.transaction_type = 'BUY'
        THEN t.gold_quantity_grams
        ELSE 0
    END), 6) AS total_gold_bought_grams,

    ROUND(SUM(CASE
        WHEN t.transaction_status = 'SUCCESS'
         AND t.transaction_type = 'SELL'
        THEN t.gold_quantity_grams
        ELSE 0
    END), 6) AS total_gold_sold_grams

FROM dg_customers c

LEFT JOIN dg_transactions t
    ON c.customer_id = t.customer_id

GROUP BY
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.city;


-- ==================================================
-- 2. CUSTOMER SEGMENT PERFORMANCE MART
-- ==================================================

CREATE VIEW IF NOT EXISTS mart_dg_customer_segment_performance AS

SELECT
    c.customer_segment,

    COUNT(DISTINCT c.customer_id) AS total_customers,

    COUNT(t.transaction_id) AS total_transactions,

    SUM(CASE
        WHEN t.transaction_status = 'SUCCESS' THEN 1
        ELSE 0
    END) AS successful_transactions,

    SUM(CASE
        WHEN t.transaction_status = 'FAILED' THEN 1
        ELSE 0
    END) AS failed_transactions,

    SUM(CASE
        WHEN t.transaction_status = 'PENDING' THEN 1
        ELSE 0
    END) AS pending_transactions,

    ROUND(SUM(CASE
        WHEN t.transaction_status = 'SUCCESS'
         AND t.transaction_type = 'BUY'
        THEN t.amount
        ELSE 0
    END), 2) AS total_buy_amount,

    ROUND(SUM(CASE
        WHEN t.transaction_status = 'SUCCESS'
         AND t.transaction_type = 'SELL'
        THEN t.amount
        ELSE 0
    END), 2) AS total_sell_amount,

    ROUND(
        100.0 * SUM(CASE
            WHEN t.transaction_status = 'SUCCESS' THEN 1
            ELSE 0
        END) / NULLIF(COUNT(t.transaction_id), 0),
        2
    ) AS success_rate_percentage

FROM dg_customers c

LEFT JOIN dg_transactions t
    ON c.customer_id = t.customer_id

GROUP BY
    c.customer_segment;


-- ==================================================
-- 3. DAILY PERFORMANCE MART
-- ==================================================

CREATE VIEW IF NOT EXISTS mart_dg_daily_performance AS

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
        WHEN transaction_status = 'PENDING' THEN 1
        ELSE 0
    END) AS pending_transactions,

    SUM(CASE
        WHEN transaction_type = 'BUY'
         AND transaction_status = 'SUCCESS'
        THEN 1
        ELSE 0
    END) AS successful_buy_transactions,

    SUM(CASE
        WHEN transaction_type = 'SELL'
         AND transaction_status = 'SUCCESS'
        THEN 1
        ELSE 0
    END) AS successful_sell_transactions,

    ROUND(SUM(CASE
        WHEN transaction_status = 'SUCCESS'
        THEN amount
        ELSE 0
    END), 2) AS total_successful_transaction_amount,

    ROUND(SUM(CASE
        WHEN transaction_type = 'BUY'
         AND transaction_status = 'SUCCESS'
        THEN amount
        ELSE 0
    END), 2) AS total_buy_amount,

    ROUND(SUM(CASE
        WHEN transaction_type = 'SELL'
         AND transaction_status = 'SUCCESS'
        THEN amount
        ELSE 0
    END), 2) AS total_sell_amount,

    ROUND(
        100.0 * SUM(CASE
            WHEN transaction_status = 'SUCCESS' THEN 1
            ELSE 0
        END) / COUNT(*),
        2
    ) AS success_rate_percentage

FROM dg_transactions

GROUP BY
    transaction_date;


-- ==================================================
-- 4. TRANSACTION TYPE PERFORMANCE MART
-- ==================================================

CREATE VIEW IF NOT EXISTS mart_dg_transaction_type_performance AS

SELECT
    transaction_type,

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
        WHEN transaction_status = 'PENDING' THEN 1
        ELSE 0
    END) AS pending_transactions,

    ROUND(SUM(CASE
        WHEN transaction_status = 'SUCCESS'
        THEN amount
        ELSE 0
    END), 2) AS total_successful_amount,

    ROUND(SUM(CASE
        WHEN transaction_status = 'SUCCESS'
        THEN gold_quantity_grams
        ELSE 0
    END), 6) AS total_successful_gold_quantity_grams,

    ROUND(
        100.0 * SUM(CASE
            WHEN transaction_status = 'SUCCESS' THEN 1
            ELSE 0
        END) / NULLIF(COUNT(*), 0),
        2
    ) AS success_rate_percentage

FROM dg_transactions

GROUP BY
    transaction_type;
