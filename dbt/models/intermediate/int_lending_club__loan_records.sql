-- Grain: one physical source record. Valid occurrences are ranked in file order so
-- the first valid occurrence of an ID wins, matching analytics/run.py.
with ranked as (
    select
        *,
        sum(case when is_contract_valid then 1 else 0 end) over (
            partition by loan_id
            order by source_row_number
            rows between unbounded preceding and current row
        ) as valid_occurrence_rank
    from {{ ref('stg_lending_club__accepted_loans') }}
)

select
    source_row_number,
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
    is_non_loan_summary,
    is_contract_valid,
    is_contract_valid and valid_occurrence_rank > 1 as is_duplicate,
    quality_issue,
    cast(loan_status in ('Fully Paid', 'Charged Off', 'Default') as integer) as is_resolved,
    cast(loan_status in ('Charged Off', 'Default') as integer) as is_default
from ranked
