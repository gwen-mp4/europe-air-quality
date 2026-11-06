with

source as (
    select * from {{ source('eea__sampling_points_metadata', 'sampling_points_metadata_raw') }}
),

renamed_and_cast as (
    select
    Country as                                                                      country,
    "Sampling Point Id" as                                                          sampling_point_id,
    "Air Quality Station EoI Code" as                                               station_code,
    "Air Pollutant" as                                                              air_pollutant,
    try_cast("Year" as integer) as                                                  reporting_year,
    try_strptime(nullif("Operational Activity Begin", ''), '%d/%m/%Y %H:%M:%S') as  observation_start,
    try_strptime(nullif("Operational Activity End", ''), '%d/%m/%Y %H:%M:%S') as    observation_end,
    try_strptime(nullif(Imported, ''), '%d/%m/%Y %H:%M:%S') as                      imported_at,
    try_cast(nullif(Longitude, '') as double) as                                    longitude,
    try_cast(nullif(Latitude, '') as double) as                                     latitude,
    try_cast(nullif(Altitude, '') as double) as                                     altitude,
    "Air Quality Station Type" as                                                   station_type,
    "Air Quality Station Area" as                                                   area_type,
    from source
)

select * from renamed_and_cast