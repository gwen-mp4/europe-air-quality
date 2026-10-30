with

renamed_and_cast as (
    select
        cast(Samplingpoint as varchar)          as sampling_point_id,
        cast(Pollutant as integer)              as pollutant_code,
        cast("Start" as timestamp)              as measured_from,
        cast("End" as timestamp)                as measured_to,
        cast(Value as decimal(10, 3))           as value,
        cast(Unit as varchar)                   as unit,
        cast(AggType as varchar)                as aggregation_type,
        cast(Validity as integer)               as validity_code,
        cast(Verification as integer)           as verification_code,
        cast(DataCapture as decimal(6, 3))      as data_capture,
        cast(ResultTime as timestamp)           as result_time,
        country,
        pollutant_name,
        year,
        month
    from {{ source('eea_air_quality', 'air_quality_raw') }}
)

select * from renamed_and_cast