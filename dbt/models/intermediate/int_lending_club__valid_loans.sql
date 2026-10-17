{{ config(materialized='view') }}

-- Grain: one valid, distinct accepted US personal loan keyed by loan_id.
select
    loan_id,
    loan_amnt,
    loan_status,
    issue_month,
    term_months,
    grade,
    purpose,
    addr_state,
    int_rate,
    fico_range_low,
    is_resolved,
    is_default
from {{ ref('int_lending_club__loan_records') }}
where is_contract_valid and not is_duplicate
