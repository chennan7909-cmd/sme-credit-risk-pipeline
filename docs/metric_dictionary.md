# Metric definitions and data contract

## Data grain and field meanings

One row per accepted Lending Club US consumer loan, identified by `id`. No application
rejections, user events, Canadian SMEs, employer counts, or company revenue are present.
The new analytics module reads original column names, independently of legacy aliases.

| Raw field | Correct meaning | Legacy notebook alias to avoid |
|---|---|---|
| `addr_state` | US borrower state | province |
| `annual_inc` | Borrower annual income | annual_revenue |
| `emp_length` | Borrower employment length | years_in_business |
| `num_actv_bc_tl` | Number of active bankcard accounts | num_employees |
| `purpose` | Loan purpose | industry |
| `fico_range_low` | Lower bound of FICO range | exact credit score |

## Measures

| Metric | Numerator / denominator or rule | Interpretation |
|---|---|---|
| Accepted loans | Count of valid, distinct loaded loan IDs | Dataset coverage, not all applications |
| Original principal USD | Sum of `loan_amnt` across accepted loans | Original amount, not current exposure or revenue |
| Resolved loans | Fully Paid + Charged Off + Default | Includes Default for consistency with legacy label |
| Defaulted loans | Charged Off + Default | Status-based composite, not a fixed-time default event |
| Resolved default rate | Defaulted / resolved loans | Loan-weighted; unresolved loans excluded |
| Resolved share | Resolved / accepted loans | Coverage diagnostic, not maturity correction |
| Segment gap pp | 100 × (segment rate − portfolio rate) | Percentage points, not percentage growth |
| Default-count share | Segment defaults / defaults within dimension | Prioritization by volume; not dollar loss share |
| YoY change pp | 100 × (current − prior calendar-year rate), within grade | Null if preceding calendar year absent |
| Pricing-review candidate | Top 10% FICO rank in grade AND rate above grade average | Exploration only, no fair-lending determination |

Ratios return NULL when the denominator is zero. Segment rates with fewer than
100 resolved loans are marked `small_sample`; 100 is a demonstration review
threshold, not a statistical significance rule. `PERCENT_RANK` handles tied scores
with shared ranks, so a top-decile condition need not select exactly 10% of loans.
Interest rate is stored in percent units (12 means 12%); differences are pp.

## Quality and exclusions

Required headers are checked. Blank IDs, nonpositive/nonfinite amounts, missing or
unparseable issue dates, invalid terms (not 36/60 months), blank statuses, impossible
interest rates and out-of-range FICO values reject the row. First valid occurrence
of an ID wins; later duplicates are rejected and counted. Missing rate/FICO remain
NULL; missing segment labels become `Unknown`. No median imputation is used in the
SQL layer. Unknown nonblank statuses remain unresolved and appear in status coverage.
Rejections are counted in the manifest: reconcile source = loaded + rejected before
using results, and investigate quality loss rather than silently accepting it.
A missing ID column fails explicitly; no fabricated loan identifiers are assigned.

The fixture is hand-authored synthetic data for code validation only. The full
accepted-loan CSV must be supplied separately; its filename, columns and size can
vary by distribution. Published historical results came from the original notebook,
whose missing-value and row filtering rules differ from this new contract.
