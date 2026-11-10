with

source as (
    select
        country,
        sampling_point_id,
        pollutant_code,
        pollutant_name,
        value,
        unit,
        cast(date_trunc('month', measured_from) as date) as month_start,
        is_negative,
        is_imputed,
        is_below_detection_limit,
    from {{ ref('int_e1a__valid') }}
),

usable as (
    select
        *,
        case when is_negative then null else value end as usable_value
    from source
),

monthly as (
    select
        country, sampling_point_id, pollutant_code, pollutant_name, unit, month_start,
        sum(usable_value)                                  as sum_value,
        count(usable_value)                                as n_valid_hours,
        min(usable_value)                                  as min_value,
        max(usable_value)                                  as max_value,
        count(*) filter (where is_negative)                as n_negative_excluded,
        count(*) filter (where is_imputed)                 as n_imputed,
        count(*) filter (where is_below_detection_limit)   as n_below_detection_limit
    from usable
    group by all
),

final as (
    select
        *,
        round(sum_value / nullif(n_valid_hours, 0), 3)                          as mean_value,
        day(last_day(month_start)) * 24                                         as n_hours_expected,
        round(n_valid_hours / (day(last_day(month_start)) * 24.0), 3)           as coverage
    from monthly
)

select * from final