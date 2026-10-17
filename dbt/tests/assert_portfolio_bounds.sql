select *
from {{ ref('mart_portfolio') }}
where accepted_loans < 0
   or resolved_loans < 0
   or defaulted_loans < 0
   or defaulted_loans > resolved_loans
   or resolved_loans > accepted_loans
   or resolved_share not between 0 and 1
   or resolved_default_rate not between 0 and 1
