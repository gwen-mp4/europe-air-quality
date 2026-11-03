-- Change the ref by another

with

station_days as (
    select *
    from {{ ref('int_e2a__daily') }}
    where is_valid_day
),

country_daily as (
    select
        country,
        pollutant_code,
        pollutant_name,
        unit,
        measurement_date,
        round(avg(daily_mean), 4)           as country_mean,
        round(min(daily_mean), 4)           as min_station_mean,
        round(max(daily_mean), 4)           as max_station_mean,
        count(distinct sampling_point_id)   as n_stations,
        max(max_verification_code)          as max_verification_code
    from station_days
    group by all
)

select * from country_daily