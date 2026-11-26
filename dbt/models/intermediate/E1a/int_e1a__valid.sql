{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='batch_key',
        tags=['heavy']
    )
}}

with

staged as (
    select * from {{ ref('stg_e1a__air_quality') }}
    where country = {{ var("country") }}
    and year = {{ var("year") }}
),

normalize as (
    select
        country,
        sampling_point_id                              as sampling_point_source_id,
        regexp_replace(sampling_point_id, '^.*/', '')  as sampling_point_id,
        pollutant_code,
        pollutant_name,
        measured_from,
        measured_to,
        value,
        unit,
        aggregation_type,
        validity_code,
        verification_code,
        data_capture,
        result_time,
        year,
        month
    from staged
),

valid_only as (
    select
        * exclude (value),
        nullif(value, -999)       as value,
        validity_code in (2, 3)   as is_below_detection_limit,
        validity_code = 3         as is_imputed
    from normalize
    where validity_code in (1, 2, 3)
),

final as (
    select
        *,
        value < 0                                  as is_negative,
        country || '-' || cast(year as varchar)    as batch_key  -- slice identifier, not unique per row
    from valid_only
)

select * from final