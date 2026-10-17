-- Grain: one row per grade and issue year. Rates are conditional on resolved status,
-- not fixed-horizon default estimates; compare years only with resolution coverage.
with cohorts as (
    select
        grade,
        year(issue_month) as issue_year,
        count(*) as accepted_loans,
        sum(is_resolved) as resolved_loans,
        sum(is_default) as defaulted_loans,
        sum(is_default)::double / nullif(sum(is_resolved), 0) as resolved_default_rate
    from {{ ref('int_lending_club__valid_loans') }}
    group by grade, issue_year
),

previous as (
    select
        *,
        lag(issue_year) over cohort_window as previous_year,
        lag(resolved_default_rate) over cohort_window as previous_rate
    from cohorts
    window cohort_window as (partition by grade order by issue_year)
)

select
    *,
    resolved_loans::double / nullif(accepted_loans, 0) as resolved_share,
    case
        when issue_year = previous_year + 1
            then 100 * (resolved_default_rate - previous_rate)
    end as yoy_change_pp
from previous
