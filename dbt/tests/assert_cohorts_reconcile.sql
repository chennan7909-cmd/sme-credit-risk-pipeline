with cohort_totals as (
    select
        sum(accepted_loans) as accepted_loans,
        sum(resolved_loans) as resolved_loans,
        sum(defaulted_loans) as defaulted_loans
    from {{ ref('mart_cohorts') }}
),

portfolio as (
    select * from {{ ref('mart_portfolio') }}
)

select cohort_totals.*
from cohort_totals
cross join portfolio
where cohort_totals.accepted_loans <> portfolio.accepted_loans
   or cohort_totals.resolved_loans <> portfolio.resolved_loans
   or cohort_totals.defaulted_loans <> portfolio.defaulted_loans
