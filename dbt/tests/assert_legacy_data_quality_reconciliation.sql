select dbt.*
from {{ ref('mart_data_quality') }} as dbt
cross join {{ source('legacy_sql', 'manifest') }} as legacy
where dbt.source_records <> legacy.quality.source_rows
   or dbt.accepted_loans <> legacy.quality.loaded_rows
   or dbt.non_loan_summary_records + dbt.invalid_loan_records + dbt.duplicate_loan_records
      <> legacy.quality.rejected_rows
   or dbt.duplicate_loan_records <> legacy.quality.duplicate_ids
