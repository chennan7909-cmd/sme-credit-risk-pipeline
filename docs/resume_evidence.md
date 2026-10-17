# Resume evidence map

Use only claims you can explain and reproduce. These bullets describe the current
portfolio extension and do not imply employer use or analysis in production.

**Lending Club Portfolio Analytics & Credit Risk Pipeline**

- Built a reproducible SQL reporting layer with CTEs, window functions and segment-to-portfolio comparisons to analyze loan performance, outcome coverage and vintage changes.
- Verified the SQL analysis on 2.26M source records (2,260,668 valid loans;
  1,345,350 resolved) and proposed investigation priorities that distinguish
  segment loan volume from observed default counts.
- Defined metric denominators and automated checks for duplicate IDs, invalid
  records and unresolved outcomes; reconciled 33 embedded non-loan summary records
  and documented selection bias and historical model limitations.

| Claim | Repository evidence | Boundary |
|---|---|---|
| Executable SQL | analytics/sql; analytics/run.py; analytics/reports/full/manifest.json | Unit-tested and verified on the complete accepted-loan CSV; batch analysis, not production serving |
| 2.26M source records / 1.35M resolved loans | analytics/reports/full/01_portfolio.csv; manifest.json | 2,260,668 valid loans from 2,260,701 source records; resolved status is not a fixed observation horizon |
| Analysis and proposals | analytics/reports/decision_memo.md | Recommendations, no measured business impact |
| Quality checks | tests/test_analytics.py; docs/metric_dictionary.md; full manifest | 33 rejected source records are embedded summaries; demonstrated implementation, not production use |

Do not claim two years of dbt, A/B testing, Canadian SME validation, revenue gains,
real Kafka deployment or regulatory-grade performance from this repository.
