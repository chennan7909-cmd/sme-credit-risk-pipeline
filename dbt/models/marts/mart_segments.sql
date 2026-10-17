-- Grain: one row per dimension and segment value.
with dimensions as (
    select 'purpose' as dimension, purpose as segment, * from {{ ref('int_lending_club__valid_loans') }}
    union all
    select 'state', addr_state, * from {{ ref('int_lending_club__valid_loans') }}
    union all
    select 'grade', grade, * from {{ ref('int_lending_club__valid_loans') }}
),

aggregated as (
    select
        dimension,
        segment,
        count(*) as accepted_loans,
        sum(is_resolved) as resolved_loans,
        sum(is_default) as defaulted_loans,
        sum(loan_amnt) as original_principal_usd
    from dimensions
    group by dimension, segment
),

baseline as (
    select resolved_default_rate as portfolio_rate
    from {{ ref('mart_portfolio') }}
)

select
    aggregated.*,
    resolved_loans::double / nullif(accepted_loans, 0) as resolved_share,
    defaulted_loans::double / nullif(resolved_loans, 0) as resolved_default_rate,
    100 * (
        defaulted_loans::double / nullif(resolved_loans, 0) - portfolio_rate
    ) as gap_pp,
    defaulted_loans::double
        / nullif(sum(defaulted_loans) over (partition by dimension), 0)
        as default_count_share,
    case when resolved_loans >= 100 then 'reviewable_volume' else 'small_sample' end
        as volume_flag
from aggregated
cross join baseline
