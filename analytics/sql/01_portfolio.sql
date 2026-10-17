-- All accepted loans are retained for coverage; outcomes use resolved loans only.
SELECT COUNT(*) AS accepted_loans,
       SUM(loan_amnt) AS original_principal_usd,
       SUM(is_resolved) AS resolved_loans,
       SUM(is_default) AS defaulted_loans,
       1.0 * SUM(is_resolved) / NULLIF(COUNT(*), 0) AS resolved_share,
       1.0 * SUM(is_default) / NULLIF(SUM(is_resolved), 0) AS resolved_default_rate
FROM loans;
