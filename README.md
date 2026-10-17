# Lending Club Portfolio Analytics & Credit Risk Pipeline

**dbt + DuckDB analytics engineering · SQL business analysis · Portfolio review**

An analyst-facing review of US consumer-loan performance: which segments deserve
investigation, how do volume and rate change prioritization, and when do incomplete
outcomes make vintage comparisons misleading?

> **Scope:** Public Lending Club US personal loans, not Canadian SME data. The
> original coursework notebook uses simulated streaming and contains methodological
> limitations. The SQL layer has now been verified against the complete accepted-loan
> CSV; raw and loan-level data remain local and are not stored in the repository.

## Start here

- [Business findings and proposed decisions](analytics/reports/decision_memo.md)
- [Metric dictionary and data-quality rules](docs/metric_dictionary.md)
- [Verified dbt workflow, models and tests](docs/dbt_workflow.md)
- [Executable SQL](analytics/sql) and [runner](analytics/run.py)
- [Analytical review: population, leakage, coverage and deployment limits](docs/analytical_review.md)

## Findings: rate is only one part of prioritization

| Question | Verified full-data evidence | Proposed decision |
|---|---|---|
| Which loan purposes need review? | Small business: 29.71%, 4,580 defaults; debt consolidation: 21.15%, 165,035 defaults | Investigate large-volume segments alongside high-rate niches |
| Does the highest-rate state create the most defaults? | MS: 26.08%, 1,718 defaults; CA: 19.61%, 38,541 defaults | Consider counts and segment mix, not rate alone |
| Did grade B vintages change? | 2015: 13.03% at 90.91% resolved; 2016: 16.11% at 66.17% resolved | Check resolution coverage and observation windows first |

![Full-data loan-purpose rates and volumes](analytics/reports/full/portfolio_review.svg)

These are descriptive associations and proposed follow-up actions, not causal
findings or implemented policy. Rates are conditional on resolved status.
[Trace the results to aggregate full-run outputs](analytics/reports/full/manifest.json).

## Reproduce the verified dbt workflow

The full-data workflow is implemented with dbt Core and DuckDB. DuckDB reads the
local CSV directly as an external source; no Pandas load or committed raw table is
required. The exact tested dependencies are pinned in `requirements-dbt.txt`.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dbt.lock.txt
export LENDING_CLUB_CSV="/absolute/path/to/accepted_loans.csv"

cd dbt
mkdir -p target/duckdb_temp
../.venv/bin/dbt build --profiles-dir .
../.venv/bin/dbt docs generate --profiles-dir .
cd ..

.venv/bin/python scripts/reconcile_dbt.py
```

The verified full run created eight models and passed all 39 data tests: primary-key
and contract checks, portfolio bounds, dimensional reconciliations, and regression
tests against the existing SQL aggregates. The independent reconciliation also
verified the raw-file digest and all requested exact counts. Generated databases,
logs, docs artifacts and loan-level relations remain gitignored.

### dbt model layers

| Layer | Models | Grain and responsibility |
|---|---|---|
| Source | `lending_club.accepted_loans_csv` | One physical CSV record, configured by `LENDING_CLUB_CSV` |
| Staging | `stg_lending_club__accepted_loans` | Typed source projection plus contract and non-loan-summary flags |
| Intermediate | `int_lending_club__loan_records`, `int_lending_club__valid_loans` | Status mapping, first-valid-ID deduplication and one row per valid loan |
| Marts | portfolio, segments, cohorts, data quality, status coverage | Aggregate evidence for business review; no public loan IDs |

Model descriptions, metric denominators and column tests are in the dbt YAML files;
the complete design and validation record is in the [dbt workflow guide](docs/dbt_workflow.md).

## Run the SQL analysis locally

Python 3.10+ with SQLite 3.25+; no third-party packages or cloud credentials needed.
Run from the repository root:

```bash
python analytics/run.py --csv analytics/data/demo_loans.csv --out analytics/reports/demo --source synthetic-demo
python -m unittest discover -s tests -v
```

The ten demo records are **hand-authored synthetic fixtures**, not a sample of the
2.26M source loans. Their generated results demonstrate query behavior only.

For a real-data run, separately obtain the
[Lending Club accepted-loan CSV](https://www.kaggle.com/datasets/wordsforthewise/lending-club),
review its use terms, keep it local, and supply its path:

```bash
python analytics/run.py --csv /path/to/accepted_2007_to_2018Q4.csv --out analytics/local_outputs --source lending-club
```

The runner retains unresolved statuses to report coverage. It produces portfolio,
segment, cohort, pricing-review and status-coverage CSVs plus a quality/source
manifest. The complete 2.26M-record CSV run has been verified locally; 2,260,668
loans loaded and 33 embedded non-loan summary rows were rejected. It requires local
memory for SQLite and window queries. This is a batch analysis, not a production
serving system.

### SQL examples and business questions

| File | Question and methods |
|---|---|
| `01_portfolio.sql` | What is the population and resolved-outcome coverage? Conditional aggregates, NULL-safe ratios |
| `02_segments.sql` | Where are rate and default-count concentrations? CTEs, CROSS JOIN to portfolio baseline, window totals |
| `03_cohorts.sql` | How do grade vintages compare? LAG, explicit calendar gaps and resolution coverage |
| `04_pricing_review.sql` | Which high-FICO loans have above-grade-average rates? PERCENT_RANK and partition averages |

These queries demonstrate analysis, not complex multi-source joins. The data is
one accepted-loan table; no invented customer, application or payment tables are used.

## Original engineering and ML coursework

[Notebook](Individual_Project_Chen.ipynb) · [Original report](Individual%20Project%20Report_Chen.pdf)

The saved run ingested 2,260,701 rows and retained 1,345,350 resolved loans. It
reported AUC 0.7009 and simulated scoring of 500 historical records using a Python
queue and mongomock. These are historical notebook results, not new verification
or production performance. WoE preprocessing uses holdout labels and the test set
is reused for model/threshold selection; the [review](docs/analytical_review.md)
explains why retraining is needed before relying on model performance.

The notebook and PDF are preserved unchanged for provenance. Their Canadian SME
field aliases, production/regulatory wording and model conclusions should be read
with the current metric dictionary and analytical review. Saved figures are legacy
artifacts and may contain those original labels.

## Repository guide

| Path | Purpose |
|---|---|
| `analytics/run.py` | Streaming CSV ingestion to in-memory SQLite and CSV exports |
| `analytics/sql/` | Readable SQL analysis |
| `analytics/data/demo_loans.csv` | Synthetic validation fixture |
| `analytics/reports/demo/` | Generated synthetic outputs and source manifest |
| `analytics/reports/full/` | Aggregate-only evidence from the verified full-data run |
| `analytics/reports/historical/` | Partial tables extracted from notebook text, with provenance |
| `analytics/reports/decision_memo.md` | Findings, interpretation, proposed actions and boundaries |
| `dbt/` | Layered dbt project, source definitions, model docs and data tests |
| `docs/` | Metric definitions, analytical review and resume evidence |
| `tests/` | Denominator, reconciliation, missing-data and window-function checks |
| `scripts/reconcile_dbt.py` | Source-digest and exact-count reconciliation between dbt and existing SQL |
| `scripts/extract_notebook_evidence.py` | Recreate historical extracts without rerunning the notebook |

To regenerate the historical extracts:

```bash
python scripts/extract_notebook_evidence.py
```

This project demonstrates independent analytical work. It does not claim employer
adoption, A/B test outcomes, production deployment, financial savings or dbt tenure.

*Nan Chen · Ontario Tech University · MBAI big-data coursework with a business-analysis extension*
