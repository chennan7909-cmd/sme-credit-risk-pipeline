with compared as (
    select
        coalesce(dbt.grade, legacy.grade) as grade,
        coalesce(dbt.issue_year, legacy.issue_year) as issue_year,
        dbt.accepted_loans as dbt_accepted,
        legacy.accepted_loans as legacy_accepted,
        dbt.resolved_loans as dbt_resolved,
        legacy.resolved_loans as legacy_resolved,
        dbt.defaulted_loans as dbt_defaulted,
        legacy.defaulted_loans as legacy_defaulted,
        dbt.resolved_default_rate as dbt_rate,
        legacy.resolved_default_rate as legacy_rate,
        dbt.previous_year as dbt_previous_year,
        legacy.previous_year as legacy_previous_year,
        dbt.previous_rate as dbt_previous_rate,
        legacy.previous_rate as legacy_previous_rate,
        dbt.resolved_share as dbt_resolved_share,
        legacy.resolved_share as legacy_resolved_share,
        dbt.yoy_change_pp as dbt_yoy,
        legacy.yoy_change_pp as legacy_yoy
    from {{ ref('mart_cohorts') }} as dbt
    full outer join {{ source('legacy_sql', 'cohorts') }} as legacy
      on dbt.grade = legacy.grade and dbt.issue_year = legacy.issue_year
)

select *
from compared
where dbt_accepted is distinct from legacy_accepted
   or dbt_resolved is distinct from legacy_resolved
   or dbt_defaulted is distinct from legacy_defaulted
   or (dbt_rate is null) <> (legacy_rate is null)
   or coalesce(abs(dbt_rate - legacy_rate), 0) > 1e-12
   or dbt_previous_year is distinct from legacy_previous_year
   or (dbt_previous_rate is null) <> (legacy_previous_rate is null)
   or coalesce(abs(dbt_previous_rate - legacy_previous_rate), 0) > 1e-12
   or (dbt_resolved_share is null) <> (legacy_resolved_share is null)
   or coalesce(abs(dbt_resolved_share - legacy_resolved_share), 0) > 1e-12
   or (dbt_yoy is null) <> (legacy_yoy is null)
   or coalesce(abs(dbt_yoy - legacy_yoy), 0) > 1e-10
