-- Grain: exactly one row summarizing source classification and load eligibility.
select
    count(*) as source_records,
    sum(cast(is_non_loan_summary as integer)) as non_loan_summary_records,
    sum(cast(not is_non_loan_summary and not is_contract_valid as integer)) as invalid_loan_records,
    sum(cast(is_duplicate as integer)) as duplicate_loan_records,
    sum(cast(is_contract_valid and not is_duplicate as integer)) as accepted_loans
from {{ ref('int_lending_club__loan_records') }}
