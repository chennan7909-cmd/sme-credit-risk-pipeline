select *
from {{ ref('int_lending_club__valid_loans') }}
where loan_amnt <= 0
   or not isfinite(loan_amnt)
   or term_months not in (36, 60)
   or (int_rate is not null and (not isfinite(int_rate) or int_rate not between 0 and 100))
   or (fico_range_low is not null and (not isfinite(fico_range_low) or fico_range_low not between 300 and 850))
   or is_default > is_resolved
   or is_resolved <> cast(loan_status in ('Fully Paid', 'Charged Off', 'Default') as integer)
   or is_default <> cast(loan_status in ('Charged Off', 'Default') as integer)
