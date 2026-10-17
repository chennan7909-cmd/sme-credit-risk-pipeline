select *
from {{ ref('int_lending_club__loan_records') }}
where is_non_loan_summary
  and (is_contract_valid or quality_issue <> 'non_loan_summary')
