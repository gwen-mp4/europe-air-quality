with

final as (
    select
        count(distinct m.sampling_point_id) as n_in_measurements,
        count(distinct d.sampling_point_id) as n_with_coordinates
    from (select distinct sampling_point_id from {{ ref('stg_e1a__air_quality') }}) m
    left join {{ ref('dim_eea__sampling_point') }} d
        on m.sampling_point_id = d.sampling_point_id
)

select * from final