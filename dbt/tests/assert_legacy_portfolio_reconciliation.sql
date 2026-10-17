select dbt.*
from {{ ref('mart_portfolio') }} as dbt
cross join {{ source('legacy_sql', 'portfolio') }} as legacy
where dbt.accepted_loans <> legacy.accepted_loans
   or dbt.original_principal_usd <> legacy.original_principal_usd
   or dbt.resolved_loans <> legacy.resolved_loans
   or dbt.defaulted_loans <> legacy.defaulted_loans
   or abs(dbt.resolved_share - legacy.resolved_share) > 1e-12
   or abs(dbt.resolved_default_rate - legacy.resolved_default_rate) > 1e-12
