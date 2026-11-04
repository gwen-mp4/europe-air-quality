with

source as (
    select * from {{ source('eea__sampling_points_metadata', 'sampling_points_metadata_raw') }}
),

renamed_and_cast as (
    select
    Countrycode as country,
    SamplingPoint as sampling_point_id,
    AirQualityStationEoICode as station_code,
    cast(regexp_extract(AirPollutantCode, '(\d+)$', 1) as integer) as pollutant_code,
    cast(ObservationDateBegin as timestamp) as observation_start,
    cast(nullif(ObservationDateEnd, '') as timestamp) as observation_end,
    cast(Longitude as double) as longitude,
    cast(Latitude as double) as latitude,
    nullif(cast(Altitude as integer), -999) as altitude,
    AirQualityStationType as station_type,
    AirQualityStationArea as area_type
    from source
)

select * from renamed_and_cast