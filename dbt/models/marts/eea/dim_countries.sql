with

countries as (
    select * from {{ ref('countries') }}
),

valid as (
    select * from {{ ref('int_air_quality__deduplicated') }}
),

station_count as (
    select
        country,
        count(distinct sampling_point_id) as station_count
    from valid
    group by country
),

country_dim as (
    select
        c.country_code,
        c.country_name,
        coalesce(sc.station_count, 0) as station_count
    from countries as c
    left join station_count as sc
        on c.country_code = sc.country
    order by country_code
)

select * from country_dim