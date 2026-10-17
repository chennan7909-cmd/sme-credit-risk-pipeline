-- Grain: exactly one row for the complete valid-loan portfolio.
select
    count(*) as accepted_loans,
    sum(loan_amnt) as original_principal_usd,
    sum(is_resolved) as resolved_loans,
    sum(is_default) as defaulted_loans,
    sum(is_resolved)::double / nullif(count(*), 0) as resolved_share,
    sum(is_default)::double / nullif(sum(is_resolved), 0) as resolved_default_rate
from {{ ref('int_lending_club__valid_loans') }}
