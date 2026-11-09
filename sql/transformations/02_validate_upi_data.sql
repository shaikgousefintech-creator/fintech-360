
-- 1. Total transaction count
SELECT COUNT(*) AS total_transactions
FROM upi_transactions;


-- 2. Transaction status distribution
SELECT
    status,
    COUNT(*) AS transaction_count
FROM upi_transactions
GROUP BY status;


-- 3. Total transaction value
SELECT
    ROUND(SUM(amount), 2) AS total_transaction_value
FROM upi_transactions;


-- 4. Check duplicate transaction IDs
SELECT
    transaction_id,
    COUNT(*) AS duplicate_count
FROM upi_transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;


-- 5. Check missing transaction identifiers
SELECT COUNT(*) AS missing_identifiers
FROM upi_transactions
WHERE transaction_id IS NULL
   OR payer_id IS NULL
   OR payee_id IS NULL;


-- 6. Successful transaction rate
SELECT
    ROUND(
        100.0 * SUM(is_successful) / COUNT(*),
        2
    ) AS success_rate_percentage
FROM upi_transactions;
