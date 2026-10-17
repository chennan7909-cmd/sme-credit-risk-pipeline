select *
from {{ ref('mart_data_quality') }}
where source_records < 0
   or non_loan_summary_records < 0
   or invalid_loan_records < 0
   or duplicate_loan_records < 0
   or accepted_loans < 0
   or source_records <>
      non_loan_summary_records + invalid_loan_records + duplicate_loan_records + accepted_loans
