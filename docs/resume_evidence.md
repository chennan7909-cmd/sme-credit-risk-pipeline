# Resume evidence map

Use only claims you can explain and reproduce. These bullets describe the current
portfolio extension and do not imply employer use or analysis in production.

**Lending Club Portfolio Analytics & Credit Risk Pipeline**

- Built and full-data validated a dbt Core + DuckDB analytics workflow with eight
  layered models across staging, intermediate and marts, using `source()`/`ref()`
  lineage and a project-local pinned environment.
- Implemented 39 data and regression tests for primary keys, lending-data contracts,
  status flags, dimensional reconciliation and parity with an independent SQL
  baseline across 2.26M source records.
- Modeled portfolio, purpose/state/grade and grade-year cohort metrics for 2,260,668
  valid US personal loans, preserving unresolved-status coverage and separating 33
  embedded non-loan summaries from invalid loan records.
- Translated verified results into investigation priorities that distinguish segment
  loan volume, observed default counts and resolved-only rates.

| Claim | Repository evidence | Boundary |
|---|---|---|
| dbt model layering and lineage | dbt/models; dbt/dbt_project.yml; docs/dbt_workflow.md | Eight models run locally with DuckDB; not a production warehouse deployment |
| 39 dbt tests | dbt/tests; model YAML; dbt workflow guide | Full-data build passed; no claim of enterprise CI/CD or production ownership |
| Executable SQL baseline | analytics/sql; analytics/run.py; analytics/reports/full/manifest.json | Preserved as an independent regression reference |
| 2.26M source records / 1.35M resolved loans | analytics/reports/full/01_portfolio.csv; manifest.json | 2,260,668 valid loans from 2,260,701 source records; resolved status is not a fixed observation horizon |
| Analysis and proposals | analytics/reports/decision_memo.md | Recommendations, no measured business impact |
| Quality checks | dbt/tests; tests/test_analytics.py; docs/metric_dictionary.md | 33 source records are classified as non-loan summaries, not anomalous loans |

Do not claim two years of dbt, production dbt deployment, A/B testing, Canadian SME
validation, revenue gains, real Kafka deployment or regulatory-grade performance
from this repository.
