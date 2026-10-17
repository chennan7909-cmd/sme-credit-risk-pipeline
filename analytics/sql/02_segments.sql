-- Compare rate AND volume. These are descriptive review candidates, not policy rules.
WITH dimensions AS (
    SELECT 'purpose' AS dimension, purpose AS segment, * FROM loans
    UNION ALL
    SELECT 'state', addr_state, * FROM loans
    UNION ALL
    SELECT 'grade', grade, * FROM loans
), aggregated AS (
    SELECT dimension, segment, COUNT(*) AS accepted_loans,
           SUM(is_resolved) AS resolved_loans, SUM(is_default) AS defaulted_loans,
           SUM(loan_amnt) AS original_principal_usd
    FROM dimensions GROUP BY dimension, segment
), baseline AS (
    SELECT 1.0 * SUM(is_default) / NULLIF(SUM(is_resolved), 0) AS portfolio_rate FROM loans
)
SELECT a.*,
       1.0 * resolved_loans / accepted_loans AS resolved_share,
       1.0 * defaulted_loans / NULLIF(resolved_loans, 0) AS resolved_default_rate,
       100.0 * (1.0 * defaulted_loans / NULLIF(resolved_loans, 0) - portfolio_rate) AS gap_pp,
       1.0 * defaulted_loans / NULLIF(SUM(defaulted_loans) OVER (PARTITION BY dimension), 0) AS default_count_share,
       CASE WHEN resolved_loans >= 100 THEN 'reviewable_volume' ELSE 'small_sample' END AS volume_flag
FROM aggregated a CROSS JOIN baseline
ORDER BY dimension, defaulted_loans DESC, segment;
