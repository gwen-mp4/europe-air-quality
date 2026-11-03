-- Change ref by another

with

measurements as (
    select * from {{ ref('int_e1a__deduplicated') }}
),

usable as (
    select
        *,
        case when is_negative then null else value end as usable_value
    from measurements
),

daily as (
    select
        country,
        pollutant_code,
        pollutant_name,
        unit,
        sampling_point_id,
        cast(measured_from as date)           as measurement_date,
        round(avg(usable_value), 4)           as daily_mean,
        round(min(usable_value), 4)           as daily_min,
        round(max(usable_value), 4)           as daily_max,
        count(usable_value)                   as n_valid_hours,
        count(*) filter (where is_negative)   as n_negative_excluded,
        max(verification_code)                as max_verification_code
    from usable
    group by all
),

final as (
    select
        *,
        round(n_valid_hours / 24.0, 4) as coverage,
        n_valid_hours >= 18  as is_valid_day
    from daily
)

select * from final