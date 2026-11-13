---
title: Europe Air Quality Monitoring
---

```sql pollutants
select distinct air_pollutant from air_quality.mart_station_info order by 1
```

<Dropdown data={pollutants} name=pollutant value=air_pollutant />

```sql stations
select distinct
    sampling_point_id,
    station_code,
    latitude,
    longitude,
    altitude,
    station_type,
    area_type
from air_quality.mart_station_info
where air_pollutant = '${inputs.pollutant.value}'
  and longitude is not null
  and latitude is not null
```

<PointMap
    data={stations}
    lat=latitude
    long=longitude
    pointName=station_code
    colorPalette={['yellow','orange','red','darkred']}
    basemap="https://{ '{' }s{ '}' }.tile.openstreetmap.org/{ '{' }z{ '}' }/{ '{' }x{ '}' }/{ '{' }y{ '}' }.png"
    startingLat=46.6
    startingLong=2.4
    startingZoom=5
    height=600
    tooltip={[
        {id: 'station_code', showColumnName: false, valueClass: 'text-xl font-semibold'},
        {id: 'station_type'},
        {id: 'area_type'},
    ]}
/>