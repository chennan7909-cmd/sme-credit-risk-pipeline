-- FICO lower bound is a score proxy. An outlier is not proof of unfair pricing.
WITH scored AS (
    SELECT *, PERCENT_RANK() OVER (PARTITION BY grade ORDER BY fico_range_low) AS fico_percentile,
           AVG(int_rate) OVER (PARTITION BY grade) AS grade_avg_interest_rate
    FROM loans WHERE fico_range_low IS NOT NULL AND int_rate IS NOT NULL
      AND grade <> 'Unknown'
)
SELECT id, grade, term_months, issue_month, fico_range_low, fico_percentile,
       int_rate, grade_avg_interest_rate,
       int_rate - grade_avg_interest_rate AS interest_gap_pp
FROM scored
WHERE fico_percentile >= 0.9 AND int_rate > grade_avg_interest_rate
ORDER BY interest_gap_pp DESC, id;
