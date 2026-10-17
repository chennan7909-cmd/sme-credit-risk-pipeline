-- Grain: one physical record from the accepted-loan CSV, including non-loan summaries.
-- All source columns arrive as VARCHAR so invalid values can be flagged before casting.
with source_records as (
    select
        row_number() over () as source_row_number,
        trim(id) as raw_loan_id,
        trim(loan_amnt) as raw_loan_amnt,
        trim(loan_status) as raw_loan_status,
        trim(issue_d) as raw_issue_d,
        trim(term) as raw_term,
        trim(grade) as raw_grade,
        trim(purpose) as raw_purpose,
        trim(addr_state) as raw_addr_state,
        trim(int_rate) as raw_int_rate,
        trim(fico_range_low) as raw_fico_range_low
    from {{ source('lending_club', 'accepted_loans_csv') }}
),

typed as (
    select
        source_row_number,
        raw_loan_id as loan_id,
        try_cast(nullif(raw_loan_amnt, '') as double) as loan_amnt,
        raw_loan_status as loan_status,
        cast(date_trunc('month', try_strptime(raw_issue_d, '%b-%Y')) as date) as issue_month,
        try_cast(regexp_extract(raw_term, '^([0-9]+)', 1) as integer) as term_months,
        coalesce(nullif(raw_grade, ''), 'Unknown') as grade,
        coalesce(nullif(raw_purpose, ''), 'Unknown') as purpose,
        coalesce(nullif(raw_addr_state, ''), 'Unknown') as addr_state,
        try_cast(nullif(replace(raw_int_rate, '%', ''), '') as double) as int_rate,
        try_cast(nullif(raw_fico_range_low, '') as double) as fico_range_low,
        raw_loan_amnt,
        raw_issue_d,
        raw_term,
        raw_int_rate,
        raw_fico_range_low,
        regexp_matches(
            raw_loan_id,
            '^(Total amount funded in policy code [12]:|Loans that do not meet the credit policy:?)'
        ) as is_non_loan_summary
    from source_records
),

quality_flags as (
    select
        *,
        not is_non_loan_summary
            and nullif(loan_id, '') is not null
            and loan_amnt is not null and isfinite(loan_amnt) and loan_amnt > 0
            and nullif(loan_status, '') is not null
            and issue_month is not null
            and term_months in (36, 60)
            and (int_rate is null or (isfinite(int_rate) and int_rate between 0 and 100))
            and (fico_range_low is null or (isfinite(fico_range_low) and fico_range_low between 300 and 850))
            as is_contract_valid
    from typed
)

select
    *,
    case
        when is_non_loan_summary then 'non_loan_summary'
        when nullif(loan_id, '') is null then 'missing_id'
        when loan_amnt is null or not isfinite(loan_amnt) or loan_amnt <= 0 then 'invalid_loan_amount'
        when nullif(loan_status, '') is null then 'missing_status'
        when issue_month is null then 'invalid_issue_month'
        when term_months not in (36, 60) or term_months is null then 'invalid_term'
        when int_rate is not null and (not isfinite(int_rate) or int_rate not between 0 and 100) then 'invalid_interest_rate'
        when fico_range_low is not null and (not isfinite(fico_range_low) or fico_range_low not between 300 and 850) then 'invalid_fico'
        else null
    end as quality_issue
from quality_flags
