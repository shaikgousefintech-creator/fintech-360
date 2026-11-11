
-- FINTECH 360 - MUTUAL FUNDS SQL DATA VALIDATION

-- 1. Total investment transactions
SELECT
    COUNT(*) AS total_transactions
FROM mf_transactions;


-- 2. Transaction status distribution
SELECT
    transaction_status,
    COUNT(*) AS transaction_count
FROM mf_transactions
GROUP BY transaction_status
ORDER BY transaction_status;


-- 3. Transaction type distribution
SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount
FROM mf_transactions
GROUP BY transaction_type
ORDER BY transaction_type;


-- 4. Duplicate investment IDs
SELECT
    investment_id,
    COUNT(*) AS duplicate_count
FROM mf_transactions
GROUP BY investment_id
HAVING COUNT(*) > 1;


-- 5. Missing required transaction values
SELECT
    COUNT(*) AS invalid_records
FROM mf_transactions
WHERE investment_id IS NULL
   OR investor_id IS NULL
   OR scheme_id IS NULL
   OR transaction_date IS NULL
   OR amount IS NULL
   OR nav IS NULL
   OR units IS NULL;


-- 6. Invalid investor references
SELECT
    COUNT(*) AS invalid_investor_references
FROM mf_transactions t
LEFT JOIN mf_investors i
    ON t.investor_id = i.investor_id
WHERE i.investor_id IS NULL;


-- 7. Invalid scheme references
SELECT
    COUNT(*) AS invalid_scheme_references
FROM mf_transactions t
LEFT JOIN mf_schemes s
    ON t.scheme_id = s.scheme_id
WHERE s.scheme_id IS NULL;


-- 8. Failed transactions without failure reasons
SELECT
    COUNT(*) AS failed_without_reason
FROM mf_transactions
WHERE transaction_status = 'FAILED'
  AND (
      failure_reason IS NULL
      OR TRIM(failure_reason) = ''
  );


-- 9. Successful transactions with failure reasons
SELECT
    COUNT(*) AS successful_with_failure_reason
FROM mf_transactions
WHERE transaction_status = 'SUCCESS'
  AND failure_reason IS NOT NULL;


-- 10. NAV history records with invalid scheme references
SELECT
    COUNT(*) AS invalid_nav_scheme_references
FROM mf_nav_history n
LEFT JOIN mf_schemes s
    ON n.scheme_id = s.scheme_id
WHERE s.scheme_id IS NULL;


-- 11. Duplicate scheme NAV dates
SELECT
    scheme_id,
    nav_date,
    COUNT(*) AS duplicate_count
FROM mf_nav_history
GROUP BY scheme_id, nav_date
HAVING COUNT(*) > 1;


-- 12. Invalid NAV values
SELECT
    COUNT(*) AS invalid_nav_records
FROM mf_nav_history
WHERE nav_value IS NULL
   OR nav_value <= 0;
