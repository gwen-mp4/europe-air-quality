---
title: Europe Air Quality Monitoring
---

```sql pollutants
select distinct pollutant_name from air_quality.mart_station_month order by 1
```

```sql months
select distinct month_start from air_quality.mart_station_month order by 1
```

<Dropdown data={pollutants} name=pollutant value=pollutant_name />

<DateRange
    name=period
    data={months}
    dates=month_start
    presetRanges={['Last 3 Months', 'Year to Date', 'All Time']}
/>

```sql stations
select
    sampling_point_id,
    station_code,
    latitude,
    longitude,
    station_type,
    area_type,
    sum(sum_value) / sum(n_valid_hours)       as mean_value,
    min(min_value)                            as min_value,
    max(max_value)                            as max_value,
    sum(n_valid_hours)                        as n_valid_hours,
    sum(n_valid_hours) / sum(n_hours_expected) as coverage
from air_quality.mart_station_month
where pollutant_name = '${inputs.pollutant.value}'
  and month_start >= date_trunc('month', cast('${inputs.period.start}' as date))
  and month_start <= cast('${inputs.period.end}' as date)
group by all
having sum(n_valid_hours) > 0
```

<PointMap
    data={stations}
    lat=latitude
    long=longitude
    value=mean_value
    valueFmt=num1
    pointName=station_code
    colorPalette={['yellow','orange','red','darkred']}
    basemap="https://{ '{' }s{ '}' }.basemaps.cartocdn.com/light_all/{ '{' }z{ '}' }/{ '{' }x{ '}' }/{ '{' }y{ '}' }.png?key=cb1_5aub_1_0023a59448831feacf46495b"
    startingLat=46.6
    startingLong=2.4
    startingZoom=5
    height=600
    tooltip={[
        {id: 'station_code', showColumnName: false, valueClass: 'text-xl font-semibold'},
        {id: 'mean_value', title: 'Mean', fmt: 'num1'},
        {id: 'min_value', title: 'Min (hourly)', fmt: 'num1'},
        {id: 'max_value', title: 'Max (hourly)', fmt: 'num1'},
        {id: 'coverage', title: 'Data coverage', fmt: 'pct0'},
        {id: 'station_type'},
        {id: 'area_type'},
    ]}
/>