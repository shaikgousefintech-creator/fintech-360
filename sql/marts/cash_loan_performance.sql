
-- ============================================================
-- FINTECH 360
-- CASH LOANS ANALYTICAL DATA MARTS
-- ============================================================


-- ============================================================
-- 1. CUSTOMER PERFORMANCE MART
-- ============================================================

CREATE VIEW IF NOT EXISTS mart_cl_customer_performance AS

WITH application_metrics AS (

    SELECT
        customer_id,

        COUNT(*) AS total_applications,

        SUM(CASE
            WHEN application_status = 'APPROVED' THEN 1
            ELSE 0
        END) AS approved_applications,

        SUM(CASE
            WHEN application_status = 'REJECTED' THEN 1
            ELSE 0
        END) AS rejected_applications,

        SUM(CASE
            WHEN application_status = 'CANCELLED' THEN 1
            ELSE 0
        END) AS cancelled_applications,

        ROUND(SUM(requested_amount), 2)
            AS total_requested_amount,

        ROUND(SUM(COALESCE(approved_amount, 0)), 2)
            AS total_approved_amount

    FROM cl_loan_applications
    GROUP BY customer_id
),

disbursement_metrics AS (

    SELECT
        a.customer_id,

        COUNT(d.disbursement_id)
            AS total_disbursement_attempts,

        SUM(CASE
            WHEN d.disbursement_status = 'SUCCESS' THEN 1
            ELSE 0
        END) AS successful_disbursements,

        SUM(CASE
            WHEN d.disbursement_status = 'FAILED' THEN 1
            ELSE 0
        END) AS failed_disbursements,

        SUM(CASE
            WHEN d.disbursement_status = 'PENDING' THEN 1
            ELSE 0
        END) AS pending_disbursements,

        ROUND(SUM(CASE
            WHEN d.disbursement_status = 'SUCCESS'
            THEN d.disbursed_amount
            ELSE 0
        END), 2) AS total_disbursed_amount

    FROM cl_loan_applications a

    INNER JOIN cl_loan_disbursements d
        ON a.application_id = d.application_id

    GROUP BY a.customer_id
),

repayment_metrics AS (

    SELECT
        a.customer_id,

        COUNT(r.repayment_id)
            AS total_installments,

        SUM(CASE
            WHEN r.repayment_status = 'PAID' THEN 1
            ELSE 0
        END) AS paid_installments,

        SUM(CASE
            WHEN r.repayment_status = 'PARTIAL' THEN 1
            ELSE 0
        END) AS partial_installments,

        SUM(CASE
            WHEN r.repayment_status = 'PENDING' THEN 1
            ELSE 0
        END) AS pending_installments,

        SUM(CASE
            WHEN r.repayment_status = 'OVERDUE' THEN 1
            ELSE 0
        END) AS overdue_installments,

        SUM(CASE
            WHEN r.repayment_status = 'FAILED' THEN 1
            ELSE 0
        END) AS failed_installments,

        ROUND(SUM(r.total_due_amount), 2)
            AS total_repayment_due,

        ROUND(SUM(r.amount_paid), 2)
            AS total_amount_collected,

        ROUND(
            SUM(r.total_due_amount - r.amount_paid),
            2
        ) AS total_outstanding_amount,

        ROUND(SUM(CASE
            WHEN r.repayment_status = 'OVERDUE'
            THEN r.total_due_amount - r.amount_paid
            ELSE 0
        END), 2) AS overdue_outstanding_amount

    FROM cl_loan_applications a

    INNER JOIN cl_loan_disbursements d
        ON a.application_id = d.application_id

    INNER JOIN cl_loan_repayments r
        ON d.disbursement_id = r.disbursement_id

    GROUP BY a.customer_id
)

SELECT
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.city,
    c.age,

    COALESCE(am.total_applications, 0)
        AS total_applications,

    COALESCE(am.approved_applications, 0)
        AS approved_applications,

    COALESCE(am.rejected_applications, 0)
        AS rejected_applications,

    COALESCE(am.cancelled_applications, 0)
        AS cancelled_applications,

    COALESCE(am.total_requested_amount, 0)
        AS total_requested_amount,

    COALESCE(am.total_approved_amount, 0)
        AS total_approved_amount,

    COALESCE(dm.total_disbursement_attempts, 0)
        AS total_disbursement_attempts,

    COALESCE(dm.successful_disbursements, 0)
        AS successful_disbursements,

    COALESCE(dm.failed_disbursements, 0)
        AS failed_disbursements,

    COALESCE(dm.pending_disbursements, 0)
        AS pending_disbursements,

    COALESCE(dm.total_disbursed_amount, 0)
        AS total_disbursed_amount,

    COALESCE(rm.total_installments, 0)
        AS total_installments,

    COALESCE(rm.paid_installments, 0)
        AS paid_installments,

    COALESCE(rm.partial_installments, 0)
        AS partial_installments,

    COALESCE(rm.pending_installments, 0)
        AS pending_installments,

    COALESCE(rm.overdue_installments, 0)
        AS overdue_installments,

    COALESCE(rm.failed_installments, 0)
        AS failed_installments,

    COALESCE(rm.total_repayment_due, 0)
        AS total_repayment_due,

    COALESCE(rm.total_amount_collected, 0)
        AS total_amount_collected,

    COALESCE(rm.total_outstanding_amount, 0)
        AS total_outstanding_amount,

    COALESCE(rm.overdue_outstanding_amount, 0)
        AS overdue_outstanding_amount

FROM cl_customers c

LEFT JOIN application_metrics am
    ON c.customer_id = am.customer_id

LEFT JOIN disbursement_metrics dm
    ON c.customer_id = dm.customer_id

LEFT JOIN repayment_metrics rm
    ON c.customer_id = rm.customer_id;


-- ============================================================
-- 2. LOAN PRODUCT PERFORMANCE MART
-- ============================================================

CREATE VIEW IF NOT EXISTS mart_cl_product_performance AS

WITH application_metrics AS (

    SELECT
        product_id,

        COUNT(*) AS total_applications,

        SUM(CASE
            WHEN application_status = 'APPROVED' THEN 1
            ELSE 0
        END) AS approved_applications,

        SUM(CASE
            WHEN application_status = 'REJECTED' THEN 1
            ELSE 0
        END) AS rejected_applications,

        SUM(CASE
            WHEN application_status = 'CANCELLED' THEN 1
            ELSE 0
        END) AS cancelled_applications,

        ROUND(SUM(requested_amount), 2)
            AS total_requested_amount,

        ROUND(SUM(COALESCE(approved_amount, 0)), 2)
            AS total_approved_amount

    FROM cl_loan_applications
    GROUP BY product_id
),

disbursement_metrics AS (

    SELECT
        a.product_id,

        COUNT(d.disbursement_id)
            AS total_disbursement_attempts,

        SUM(CASE
            WHEN d.disbursement_status = 'SUCCESS' THEN 1
            ELSE 0
        END) AS successful_disbursements,

        SUM(CASE
            WHEN d.disbursement_status = 'FAILED' THEN 1
            ELSE 0
        END) AS failed_disbursements,

        SUM(CASE
            WHEN d.disbursement_status = 'PENDING' THEN 1
            ELSE 0
        END) AS pending_disbursements,

        ROUND(SUM(CASE
            WHEN d.disbursement_status = 'SUCCESS'
            THEN d.disbursed_amount
            ELSE 0
        END), 2) AS total_disbursed_amount

    FROM cl_loan_applications a

    INNER JOIN cl_loan_disbursements d
        ON a.application_id = d.application_id

    GROUP BY a.product_id
),

repayment_metrics AS (

    SELECT
        a.product_id,

        COUNT(r.repayment_id)
            AS total_installments,

        ROUND(SUM(r.total_due_amount), 2)
            AS total_repayment_due,

        ROUND(SUM(r.amount_paid), 2)
            AS total_amount_collected,

        ROUND(
            SUM(r.total_due_amount - r.amount_paid),
            2
        ) AS total_outstanding_amount,

        ROUND(SUM(CASE
            WHEN r.repayment_status = 'OVERDUE'
            THEN r.total_due_amount - r.amount_paid
            ELSE 0
        END), 2) AS overdue_outstanding_amount

    FROM cl_loan_applications a

    INNER JOIN cl_loan_disbursements d
        ON a.application_id = d.application_id

    INNER JOIN cl_loan_repayments r
        ON d.disbursement_id = r.disbursement_id

    GROUP BY a.product_id
)

SELECT
    p.product_id,
    p.product_name,
    p.loan_type,
    p.min_loan_amount,
    p.max_loan_amount,
    p.annual_interest_rate,
    p.min_tenure_months,
    p.max_tenure_months,
    p.processing_fee_percentage,

    COALESCE(am.total_applications, 0)
        AS total_applications,

    COALESCE(am.approved_applications, 0)
        AS approved_applications,

    COALESCE(am.rejected_applications, 0)
        AS rejected_applications,

    COALESCE(am.cancelled_applications, 0)
        AS cancelled_applications,

    COALESCE(am.total_requested_amount, 0)
        AS total_requested_amount,

    COALESCE(am.total_approved_amount, 0)
        AS total_approved_amount,

    ROUND(
        100.0 * COALESCE(am.approved_applications, 0)
        / NULLIF(am.total_applications, 0),
        2
    ) AS approval_rate_percentage,

    COALESCE(dm.total_disbursement_attempts, 0)
        AS total_disbursement_attempts,

    COALESCE(dm.successful_disbursements, 0)
        AS successful_disbursements,

    COALESCE(dm.failed_disbursements, 0)
        AS failed_disbursements,

    COALESCE(dm.pending_disbursements, 0)
        AS pending_disbursements,

    COALESCE(dm.total_disbursed_amount, 0)
        AS total_disbursed_amount,

    COALESCE(rm.total_installments, 0)
        AS total_installments,

    COALESCE(rm.total_repayment_due, 0)
        AS total_repayment_due,

    COALESCE(rm.total_amount_collected, 0)
        AS total_amount_collected,

    COALESCE(rm.total_outstanding_amount, 0)
        AS total_outstanding_amount,

    COALESCE(rm.overdue_outstanding_amount, 0)
        AS overdue_outstanding_amount

FROM cl_loan_products p

LEFT JOIN application_metrics am
    ON p.product_id = am.product_id

LEFT JOIN disbursement_metrics dm
    ON p.product_id = dm.product_id

LEFT JOIN repayment_metrics rm
    ON p.product_id = rm.product_id;


-- ============================================================
-- 3. DAILY APPLICATION PERFORMANCE MART
-- ============================================================

CREATE VIEW IF NOT EXISTS mart_cl_application_performance AS

SELECT
    application_date,

    COUNT(*) AS total_applications,

    SUM(CASE
        WHEN application_status = 'APPROVED' THEN 1
        ELSE 0
    END) AS approved_applications,

    SUM(CASE
        WHEN application_status = 'REJECTED' THEN 1
        ELSE 0
    END) AS rejected_applications,

    SUM(CASE
        WHEN application_status = 'DRAFT' THEN 1
        ELSE 0
    END) AS draft_applications,

    SUM(CASE
        WHEN application_status = 'SUBMITTED' THEN 1
        ELSE 0
    END) AS submitted_applications,

    SUM(CASE
        WHEN application_status = 'UNDER_REVIEW' THEN 1
        ELSE 0
    END) AS under_review_applications,

    SUM(CASE
        WHEN application_status = 'CANCELLED' THEN 1
        ELSE 0
    END) AS cancelled_applications,

    ROUND(SUM(requested_amount), 2)
        AS total_requested_amount,

    ROUND(SUM(COALESCE(approved_amount, 0)), 2)
        AS total_approved_amount,

    ROUND(
        100.0 * SUM(CASE
            WHEN application_status = 'APPROVED' THEN 1
            ELSE 0
        END) / COUNT(*),
        2
    ) AS approval_rate_percentage

FROM cl_loan_applications

GROUP BY application_date;


-- ============================================================
-- 4. DISBURSEMENT PERFORMANCE MART
-- ============================================================

CREATE VIEW IF NOT EXISTS mart_cl_disbursement_performance AS

SELECT
    disbursement_date,

    COUNT(*) AS total_disbursement_attempts,

    SUM(CASE
        WHEN disbursement_status = 'SUCCESS' THEN 1
        ELSE 0
    END) AS successful_disbursements,

    SUM(CASE
        WHEN disbursement_status = 'FAILED' THEN 1
        ELSE 0
    END) AS failed_disbursements,

    SUM(CASE
        WHEN disbursement_status = 'PENDING' THEN 1
        ELSE 0
    END) AS pending_disbursements,

    ROUND(SUM(CASE
        WHEN disbursement_status = 'SUCCESS'
        THEN disbursed_amount
        ELSE 0
    END), 2) AS total_disbursed_amount,

    ROUND(
        100.0 * SUM(CASE
            WHEN disbursement_status = 'SUCCESS' THEN 1
            ELSE 0
        END) / COUNT(*),
        2
    ) AS disbursement_success_rate_percentage

FROM cl_loan_disbursements

GROUP BY disbursement_date;


-- ============================================================
-- 5. REPAYMENT PERFORMANCE MART
-- ============================================================

CREATE VIEW IF NOT EXISTS mart_cl_repayment_performance AS

SELECT
    due_date,

    COUNT(*) AS total_installments,

    SUM(CASE
        WHEN repayment_status = 'PAID' THEN 1
        ELSE 0
    END) AS paid_installments,

    SUM(CASE
        WHEN repayment_status = 'PARTIAL' THEN 1
        ELSE 0
    END) AS partial_installments,

    SUM(CASE
        WHEN repayment_status = 'PENDING' THEN 1
        ELSE 0
    END) AS pending_installments,

    SUM(CASE
        WHEN repayment_status = 'OVERDUE' THEN 1
        ELSE 0
    END) AS overdue_installments,

    SUM(CASE
        WHEN repayment_status = 'FAILED' THEN 1
        ELSE 0
    END) AS failed_installments,

    ROUND(SUM(total_due_amount), 2)
        AS total_due_amount,

    ROUND(SUM(amount_paid), 2)
        AS total_amount_collected,

    ROUND(
        SUM(total_due_amount - amount_paid),
        2
    ) AS total_outstanding_amount,

    ROUND(SUM(CASE
        WHEN repayment_status = 'OVERDUE'
        THEN total_due_amount - amount_paid
        ELSE 0
    END), 2) AS overdue_outstanding_amount,

    ROUND(
        100.0 * SUM(CASE
            WHEN repayment_status = 'PAID' THEN 1
            ELSE 0
        END) / COUNT(*),
        2
    ) AS paid_installment_rate_percentage,

    ROUND(AVG(late_days), 2)
        AS average_late_days

FROM cl_loan_repayments

GROUP BY due_date;
