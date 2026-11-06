with

staged as (
    select * from {{ ref('int_eea__valid') }}
),

final as (
    select
        country,
        sampling_point_id,
        station_code,
        air_pollutant,
        reporting_year,
        observation_start,
        observation_end,
        imported_at,
        longitude,
        latitude,
        altitude,
        station_type,
        area_type
    from staged
    qualify row_number() over(
        partition by sampling_point_id
        order by
            observation_end is null desc,
            observation_start desc,
            imported_at desc
    ) = 1
)

select * from final