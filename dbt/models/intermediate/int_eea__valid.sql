with

source as (
    select
        *,
        upper(trim(air_pollutant)) as pollutant_normalized

    from {{ ref('stg_eea__sampling_points') }}
),

classified as (

    select *
    from source
    where air_pollutant in (
        'PM2.5',
        'PM10',
        'NO2',
        'O3',
        'SO2'
    )
)

select * from classified