
-- FINTECH 360
-- UPI Daily Performance Analytics Mart

CREATE VIEW IF NOT EXISTS mart_upi_daily_performance AS

SELECT
    transaction_date,

    COUNT(*) AS total_transactions,

    SUM(CASE
        WHEN status = 'SUCCESS' THEN 1
        ELSE 0
    END) AS successful_transactions,

    SUM(CASE
        WHEN status = 'FAILED' THEN 1
        ELSE 0
    END) AS failed_transactions,

    SUM(CASE
        WHEN status = 'PENDING' THEN 1
        ELSE 0
    END) AS pending_transactions,

    ROUND(SUM(amount), 2) AS total_transaction_value,

    ROUND(
        SUM(CASE
            WHEN status = 'SUCCESS' THEN amount
            ELSE 0
        END), 2
    ) AS successful_transaction_value,

    ROUND(
        100.0 * SUM(is_successful) / COUNT(*), 2
    ) AS success_rate_percentage

FROM upi_transactions

GROUP BY transaction_date

ORDER BY transaction_date;
