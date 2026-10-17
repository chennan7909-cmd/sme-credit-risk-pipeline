-- Vintage comparisons are conditional on resolution, NOT fixed-horizon default estimates.
WITH cohorts AS (
    SELECT grade, CAST(SUBSTR(issue_month, 1, 4) AS INTEGER) AS issue_year,
           COUNT(*) AS accepted_loans, SUM(is_resolved) AS resolved_loans,
           SUM(is_default) AS defaulted_loans,
           1.0 * SUM(is_default) / NULLIF(SUM(is_resolved), 0) AS resolved_default_rate
    FROM loans GROUP BY grade, issue_year
), previous AS (
    SELECT *, LAG(issue_year) OVER w AS previous_year,
           LAG(resolved_default_rate) OVER w AS previous_rate
    FROM cohorts WINDOW w AS (PARTITION BY grade ORDER BY issue_year)
)
SELECT *, 1.0 * resolved_loans / accepted_loans AS resolved_share,
       CASE WHEN issue_year = previous_year + 1
            THEN 100.0 * (resolved_default_rate - previous_rate) END AS yoy_change_pp
FROM previous ORDER BY grade, issue_year;
