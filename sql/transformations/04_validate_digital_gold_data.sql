
-- FINTECH 360 - DIGITAL GOLD SQL DATA VALIDATION


-- 1. Total Digital Gold transactions
SELECT
    COUNT(*) AS total_transactions
FROM dg_transactions;


-- 2. Transaction status distribution
SELECT
    transaction_status,
    COUNT(*) AS transaction_count
FROM dg_transactions
GROUP BY transaction_status
ORDER BY transaction_status;


-- 3. Transaction type distribution
SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount
FROM dg_transactions
GROUP BY transaction_type
ORDER BY transaction_type;


-- 4. Duplicate transaction IDs
SELECT
    transaction_id,
    COUNT(*) AS duplicate_count
FROM dg_transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;


-- 5. Missing required transaction values
SELECT
    COUNT(*) AS invalid_records
FROM dg_transactions
WHERE transaction_id IS NULL
   OR customer_id IS NULL
   OR transaction_date IS NULL
   OR transaction_type IS NULL
   OR gold_quantity_grams IS NULL
   OR gold_price_per_gram IS NULL
   OR amount IS NULL
   OR transaction_status IS NULL;


-- 6. Invalid customer references
SELECT
    COUNT(*) AS invalid_customer_references
FROM dg_transactions t
LEFT JOIN dg_customers c
    ON t.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


-- 7. Failed transactions without failure reasons
SELECT
    COUNT(*) AS failed_without_reason
FROM dg_transactions
WHERE transaction_status = 'FAILED'
  AND (
      failure_reason IS NULL
      OR TRIM(failure_reason) = ''
  );


-- 8. Successful transactions with failure reasons
SELECT
    COUNT(*) AS successful_with_failure_reason
FROM dg_transactions
WHERE transaction_status = 'SUCCESS'
  AND failure_reason IS NOT NULL
  AND TRIM(failure_reason) <> '';


-- 9. Duplicate gold price history dates
SELECT
    price_date,
    COUNT(*) AS duplicate_count
FROM dg_price_history
GROUP BY price_date
HAVING COUNT(*) > 1;


-- 10. Invalid gold price records
SELECT
    COUNT(*) AS invalid_price_records
FROM dg_price_history
WHERE gold_price_per_gram IS NULL
   OR buy_price_per_gram IS NULL
   OR sell_price_per_gram IS NULL
   OR gold_price_per_gram <= 0
   OR buy_price_per_gram <= 0
   OR sell_price_per_gram <= 0
   OR buy_price_per_gram <= gold_price_per_gram
   OR sell_price_per_gram >= gold_price_per_gram;


-- 11. Successful transactions without wallet ledger entries
SELECT
    COUNT(*) AS missing_ledger_entries
FROM dg_transactions t
LEFT JOIN dg_wallet_ledger l
    ON t.transaction_id = l.transaction_id
WHERE t.transaction_status = 'SUCCESS'
  AND l.transaction_id IS NULL;


-- 12. Invalid wallet ledger transaction relationships
SELECT
    COUNT(*) AS invalid_ledger_records
FROM dg_wallet_ledger l
LEFT JOIN dg_transactions t
    ON l.transaction_id = t.transaction_id
WHERE t.transaction_id IS NULL
   OR t.transaction_status <> 'SUCCESS'
   OR l.customer_id <> t.customer_id
   OR l.gold_quantity_grams <> t.gold_quantity_grams
   OR (
       t.transaction_type = 'BUY'
       AND l.transaction_type <> 'CREDIT'
   )
   OR (
       t.transaction_type = 'SELL'
       AND l.transaction_type <> 'DEBIT'
   );
