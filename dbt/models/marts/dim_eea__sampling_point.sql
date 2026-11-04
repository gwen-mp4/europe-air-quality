with

staged as (
    select * from {{ ref('stg_eea__sampling_points') }}
    WHERE pollutant_code IN (6001, 5, 8, 7, 1)
),

final as (
    select *
    from staged
    qualify row_number() over(
        partition by sampling_point_id
        order by observation_end is null desc, observation_start desc
    ) = 1
)

select * from final