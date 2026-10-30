with

staged as (
    select * from {{ ref('stg_eea__air_quality') }}
),

valid_only as (
    select
        * exclude (value),
        nullif(value, -999) as value,
        validity_code in (2, 3) as is_below_detection_limit,
        validity_code = 3 as is_imputed
    from staged
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