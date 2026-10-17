# Verified dbt + DuckDB workflow

## Scope and status

This workflow models the public Lending Club US accepted personal-loan dataset. It
is not Canadian SME data. It has been run on the complete local CSV and reconciled
to the existing `analytics/run.py` results. The original notebook, Python/SQLite
runner and aggregate evidence remain unchanged as regression references.

Status: **implemented and full-data verified**, not a plan. The workflow is local
batch analytics, not a production deployment or evidence of employer adoption.

## Reproducible environment

The tested environment uses Python 3.12.14 and exact direct pins from
`requirements-dbt.txt`; `requirements-dbt.lock.txt` records the complete resolved
environment:

| Dependency | Verified version | Reason |
|---|---:|---|
| dbt Core | 1.12.6 | DAG compilation, documentation and data-test execution |
| dbt-duckdb | 1.11.0 | DuckDB adapter and external-source support |
| DuckDB | 1.5.6 | Vectorized CSV scanning and local analytical storage |

The versions satisfy the packages' published Python 3.10+ requirements and were
resolved together in the project-local `.venv`. References: [dbt installation and
version guidance](https://docs.getdbt.com/docs/local/install-dbt), [dbt `ref()`
dependency behavior](https://docs.getdbt.com/reference/dbt-jinja-functions/ref),
[dbt data tests](https://docs.getdbt.com/docs/build/data-tests), and the
[dbt-duckdb external-source documentation](https://github.com/duckdb/dbt-duckdb#reading-and-writing-external-files).

The raw path is supplied only through `LENDING_CLUB_CSV`. `.env.example` contains a
generic placeholder; the actual path, `.venv`, DuckDB files, logs and generated dbt
artifacts are ignored by Git.

## Model DAG and grains

| Node | Materialization | Grain | Responsibility |
|---|---|---|---|
| `source('lending_club', 'accepted_loans_csv')` | External CSV scan | One physical record | Read all fields as text so quality decisions precede casting |
| `stg_lending_club__accepted_loans` | View | One physical record | Preserve source meanings, type required fields and set quality flags |
| `int_lending_club__loan_records` | Table | One physical record | Rank valid ID occurrences and map exact resolved/default statuses |
| `int_lending_club__valid_loans` | View | One valid distinct loan | Retain the first valid occurrence of each loan ID |
| `mart_portfolio` | Table | One portfolio row | Portfolio volume, principal, coverage and resolved default rate |
| `mart_segments` | Table | Dimension × segment | Purpose/state/grade counts, rates, gaps and default-count shares |
| `mart_cohorts` | Table | Grade × issue year | Vintage rates, resolution coverage and calendar-contiguous changes |
| `mart_data_quality` | Table | One quality row | Reconcile source, non-loan summaries, invalids, duplicates and accepted loans |
| `mart_status_coverage` | Table | Loan status | Preserve unresolved-status visibility |

All downstream dependencies use `ref()`. Raw and legacy regression inputs use
`source()`. The intermediate table is persisted once, which avoids repeatedly
scanning the 1.6 GB CSV; DuckDB is capped at 4 GB memory and may spill to the ignored
`target/duckdb_temp` directory.

## Contract and metric behavior

The dbt models implement the existing metric dictionary rather than a second set of
rules. Required IDs, positive finite amounts, parseable issue months, 36/60-month
terms, nonblank status, 0–100 interest rate and 300–850 FICO range are enforced.
Missing rate/FICO values remain NULL, while missing grade/purpose/state become
`Unknown`.

The 33 embedded source summaries are explicitly classified as non-loan records.
They are not described as anomalous or rejected loans. Valid later occurrences of
an ID are counted as duplicates; the first valid occurrence wins.

Resolved means `Fully Paid`, `Charged Off` or `Default`; defaulted means `Charged
Off` or `Default`. All rates are NULL-safe. Cohort rates remain conditional on
resolution and are not fixed-horizon default estimates; `resolved_share` must be
considered when comparing vintages.

## Tests and reconciliation

The verified build ran eight models and 39 tests (47 resources total), covering:

- unique/non-null loan keys and source row numbers;
- valid amount, term, interest-rate, FICO and exact status flags;
- `defaulted <= resolved <= accepted` and rates constrained to `[0, 1]`;
- source-record reconciliation, with non-loan summaries separate from invalid loans;
- purpose/state/grade and grade-year counts reconciling to the portfolio;
- default-count shares summing to one within each dimension;
- exact count and tolerant floating-point regression against the existing full SQL
  portfolio, segment and cohort outputs.

`scripts/reconcile_dbt.py` independently verifies that the configured raw CSV has
the same SHA-256 as the legacy full-run manifest before comparing results. The
verified run produced:

| Check | Result |
|---|---:|
| Source records | 2,260,701 |
| Valid loans | 2,260,668 |
| Non-loan summary records | 33 |
| Resolved loans | 1,345,350 |
| Defaulted loans | 268,599 |
| Debt-consolidation defaults | 165,035 |
| Small-business defaults | 4,580 |
| California resolved / defaulted | 196,529 / 38,541 |

These values are validation evidence, not constants in model calculations.

## Commands

From the repository root:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dbt.lock.txt
export LENDING_CLUB_CSV="/absolute/path/to/accepted_loans.csv"
cd dbt
mkdir -p target/duckdb_temp
../.venv/bin/dbt debug --profiles-dir .
../.venv/bin/dbt build --profiles-dir .
../.venv/bin/dbt docs generate --profiles-dir .
cd ..
.venv/bin/python scripts/reconcile_dbt.py
```

`dbt docs serve --profiles-dir .` may be run from `dbt/` to inspect the generated
lineage and catalog locally. The generated site is intentionally not committed.

The loan-level pricing-review query remains in the original SQL workflow only. Its
output is local and ignored; no per-loan pricing candidates are published as dbt
aggregate evidence.
