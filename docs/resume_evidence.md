# Resume evidence map

Use only claims you can explain and reproduce. These bullets describe the current
portfolio extension and do not imply employer use or analysis in production.

**Lending Club Portfolio Analytics & Credit Risk Pipeline**

- Built a reproducible SQL reporting layer with CTEs, window functions and segment-to-portfolio comparisons to analyze loan performance, outcome coverage and vintage changes.
- Reviewed saved analyses of 1.35M resolved US consumer loans and proposed investigation priorities that balance segment default rates with default counts and loan volume.
- Defined metric denominators and automated checks for duplicate IDs, invalid records and unresolved outcomes; documented selection bias and limitations of historical model results.

| Claim | Repository evidence | Boundary |
|---|---|---|
| Executable SQL | analytics/sql; analytics/run.py | Validated on synthetic demo; full CSV run pending |
| 1.35M resolved loans | Original notebook cell 9 saved output | Historical output, not a new SQL run |
| Analysis and proposals | analytics/reports/decision_memo.md | Recommendations, no measured business impact |
| Quality checks | tests/test_analytics.py; metric dictionary | Demonstrated implementation, not production use |

Do not claim two years of dbt, A/B testing, Canadian SME validation, revenue gains,
real Kafka deployment or regulatory-grade performance from this repository.
