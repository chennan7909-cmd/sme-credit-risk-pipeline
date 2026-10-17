-- Grain: one row per raw loan status among valid, distinct loans.
select
    loan_status,
    count(*) as loans
from {{ ref('int_lending_club__valid_loans') }}
group by loan_status
