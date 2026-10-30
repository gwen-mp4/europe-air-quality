with

valid as (
    select * from {{ ref('int_air_quality__valid') }}
),

deduplicated as (
    select *
    from valid
    qualify row_number() over (
        partition by sampling_point_id, pollutant_code, measured_from, measured_to
        order by verification_code asc, result_time desc
    ) = 1
)

select * from deduplicated