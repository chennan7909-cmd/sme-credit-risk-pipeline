with segment_totals as (
    select
        dimension,
        sum(accepted_loans) as accepted_loans,
        sum(resolved_loans) as resolved_loans,
        sum(defaulted_loans) as defaulted_loans,
        sum(default_count_share) as default_count_share
    from {{ ref('mart_segments') }}
    group by dimension
),

portfolio as (
    select * from {{ ref('mart_portfolio') }}
)

select segment_totals.*
from segment_totals
cross join portfolio
where segment_totals.accepted_loans <> portfolio.accepted_loans
   or segment_totals.resolved_loans <> portfolio.resolved_loans
   or segment_totals.defaulted_loans <> portfolio.defaulted_loans
   or abs(segment_totals.default_count_share - 1.0) > 1e-12
