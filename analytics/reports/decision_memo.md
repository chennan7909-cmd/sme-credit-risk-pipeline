# Portfolio review: where should an analyst investigate first?

**Decision supported:** prioritize follow-up portfolio analysis, not approve or
reject applicants. **Audience:** risk/product analyst and business stakeholders.
**Evidence:** stored notebook outputs, not a new run of the source dataset.

## Findings and proposed actions

| Historical observation | Business interpretation | Proposed next step |
|---|---|---|
| Small-business-purpose loans: 29.71% resolved default rate, 15,416 loans | Elevated descriptive rate, but purpose is not an industry classification | Compare against other purposes within grade, term and vintage before changing policy |
| Debt consolidation: 780,342 resolved loans at 21.15%; small business: 15,416 at 29.71% | Rate alone misses scale; debt consolidation has about 50.6× the resolved-loan volume | Review debt consolidation alongside high-rate niches; calculate exact default counts from raw data |
| Mississippi: 1,718 defaults / 6,588 resolved loans = 26.08%; New York: 24,220 / 109,849 = 22.05% | Mississippi has the higher rate; New York has about 14.1× the observed default count | Combine count and rate when allocating investigation effort; control for mix before interpreting geography |
| Grade B, 2015 vs 2016: 13.03% → 16.11%, +3.08 percentage points | Candidate vintage signal conditional on resolution | Check unresolved share and like-for-like observation windows before calling it deterioration |

Rounded rates are copied as displayed. Do not multiply them by loan counts and
label the result an exact observed default count. New York and Mississippi counts
are directly present in the saved state table. Ratios above are descriptive arithmetic.

## What changes in a business conversation?

A risk-only ranking would start with the highest default rate. A portfolio analyst
also considers the number of affected loans, data coverage and comparability.
The resulting recommendation is to investigate large-volume segments alongside
high-rate niches, with grade/term/vintage checks before any pricing or underwriting
change. These are proposed actions; no stakeholder adoption or savings are claimed.

## Evidence trail

- Source: `Individual_Project_Chen.ipynb`, zero-based cell 11 saved text outputs.
- Machine-readable extracts: [purposes](historical/purposes.csv),
  [states](historical/states.csv), [cohorts](historical/cohorts.csv).
- Integrity/source coverage: [manifest](historical/manifest.json).
- The state table contains only the top 15 rows; cohort output contains the first
  30 rows. Purpose output contains all 14 displayed categories. No missing rows
  have been reconstructed.
- [Analytical review](../../docs/analytical_review.md) explains selection bias and
  model issues. The new SQL has been validated on synthetic fixtures only; the
  raw Lending Club CSV is not included in the repository.
