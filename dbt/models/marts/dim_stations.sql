with

comparaison as (
    select
        count(distinct m.sampling_point_id) as n_in_measurements,
        count(distinct d.sampling_point_id) as n_with_coordinates
    from (select distinct sampling_point_id from {{ ref('int_e1a__valid') }}) m
    left join {{ ref('dim_eea__sampling_point') }} d
        on m.sampling_point_id = d.sampling_point_id
),

points_per_year as (
    select distinct year(measured_from) as year, sampling_point_id
    from {{ ref('int_e1a__valid') }}
),

final as (
    select
        p.year,
        count(*)                       as n_points,
        count(d.sampling_point_id)     as n_with_coordinates,
        round(100.0 * count(d.sampling_point_id) / count(*), 1) as pct_matched
    from points_per_year p
    left join {{ ref('dim_eea__sampling_point') }} d
        on p.sampling_point_id = d.sampling_point_id
    group by 1
    order by 1
)

select * from comparaison, final