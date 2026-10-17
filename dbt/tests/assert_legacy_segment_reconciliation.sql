with compared as (
    select
        coalesce(dbt.dimension, legacy.dimension) as dimension,
        coalesce(dbt.segment, legacy.segment) as segment,
        dbt.accepted_loans as dbt_accepted,
        legacy.accepted_loans as legacy_accepted,
        dbt.resolved_loans as dbt_resolved,
        legacy.resolved_loans as legacy_resolved,
        dbt.defaulted_loans as dbt_defaulted,
        legacy.defaulted_loans as legacy_defaulted,
        dbt.original_principal_usd as dbt_principal,
        legacy.original_principal_usd as legacy_principal,
        dbt.resolved_share as dbt_resolved_share,
        legacy.resolved_share as legacy_resolved_share,
        dbt.resolved_default_rate as dbt_rate,
        legacy.resolved_default_rate as legacy_rate,
        dbt.gap_pp as dbt_gap_pp,
        legacy.gap_pp as legacy_gap_pp,
        dbt.default_count_share as dbt_default_share,
        legacy.default_count_share as legacy_default_share,
        dbt.volume_flag as dbt_volume_flag,
        legacy.volume_flag as legacy_volume_flag
    from {{ ref('mart_segments') }} as dbt
    full outer join {{ source('legacy_sql', 'segments') }} as legacy
      on dbt.dimension = legacy.dimension and dbt.segment = legacy.segment
)

select *
from compared
where dbt_accepted is distinct from legacy_accepted
   or dbt_resolved is distinct from legacy_resolved
   or dbt_defaulted is distinct from legacy_defaulted
   or dbt_principal is distinct from legacy_principal
   or abs(dbt_resolved_share - legacy_resolved_share) > 1e-12
   or abs(dbt_rate - legacy_rate) > 1e-12
   or abs(dbt_gap_pp - legacy_gap_pp) > 1e-10
   or abs(dbt_default_share - legacy_default_share) > 1e-12
   or dbt_volume_flag is distinct from legacy_volume_flag
