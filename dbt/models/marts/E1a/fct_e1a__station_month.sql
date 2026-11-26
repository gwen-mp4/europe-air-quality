{{ config(
    materialized='external',
    location='../evidence-legacy/sources/air_quality/mart_station_month.parquet',
    format='parquet'
) }}

with

final as (
    select
        s.country,
        m.sampling_point_id,
        s.station_code,
        s.latitude,
        s.longitude,
        s.station_type,
        s.area_type,
        m.pollutant_name,
        m.unit,
        m.month_start,
        cast(m.sum_value as double)   as sum_value,
        cast(m.min_value as double)   as min_value,
        cast(m.max_value as double)   as max_value,
        m.n_valid_hours,
        m.n_hours_expected
    from {{ ref('fct_e1a__monthly_pollutants') }} m
    inner join {{ ref('dim_eea__sampling_point') }} s
        on m.sampling_point_id = s.sampling_point_id
    where s.latitude is not null
    and s.longitude is not null
)

select * from final