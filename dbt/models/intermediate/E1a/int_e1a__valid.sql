with

staged as (
    select * from {{ ref('stg_e1a__air_quality') }}
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
        nullif(value, -999) as value,
        validity_code in (2, 3) as is_below_detection_limit,
        validity_code = 3 as is_imputed
    from normalize
    where validity_code in (1, 2, 3)
),

flagged as (
    select
        *,
        value < 0 and value <> -999 as is_negative
    from valid_only
),

cleaned as (
    select
        * exclude (value),
        nullif(value, -999) as value
    from flagged
)

select * from cleaned