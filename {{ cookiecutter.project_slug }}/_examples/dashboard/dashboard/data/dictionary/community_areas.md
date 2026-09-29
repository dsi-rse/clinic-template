# community_areas — Data Dictionary

Chicago's 77 community areas with 2008-2012 census socioeconomic indicators. Percent columns are 0-100; hardship_index is a 1-98 composite (higher = more hardship). Sources: Chicago Data Portal igwz-8jzy (boundaries) + kn9c-c2s2 (indicators).

**Rows:** 77

| Column | Type | Nulls | Unique | Min | Max | Sample Values |
|--------|------|-------|--------|-----|-----|---------------|
| area_num | int64 | 0 | 77 | 1.0 | 77.0 | 1, 2, 3, 4, 5 |
| name | str | 0 | 77 | Albany Park | Woodlawn | Rogers Park, West Ridge, Uptown, Lincoln Square, North Center |
| geometry | geometry (WKB, EPSG:4326 MultiPolygon) | 0 | 77 | — | — |  |
| pct_housing_crowded | float64 | 0 | 56 | 0.3 | 15.8 | 7.7, 7.8, 3.8, 3.4, 0.3 |
| pct_below_poverty | float64 | 0 | 67 | 3.3 | 56.5 | 23.6, 17.2, 24.0, 10.9, 7.5 |
| pct_unemployed | float64 | 0 | 66 | 4.7 | 35.9 | 8.7, 8.8, 8.9, 8.2, 5.2 |
| pct_no_hs_diploma | float64 | 0 | 69 | 2.5 | 54.8 | 18.2, 20.8, 11.8, 13.4, 4.5 |
| pct_dependent_age | float64 | 0 | 66 | 13.5 | 51.5 | 27.5, 38.5, 22.2, 25.5, 26.2 |
| per_capita_income | float64 | 0 | 77 | 8201.0 | 88669.0 | 23939.0, 23040.0, 35787.0, 37524.0, 57123.0 |
| hardship_index | float64 | 0 | 77 | 1.0 | 98.0 | 39.0, 46.0, 20.0, 17.0, 6.0 |
| geometry_geojson | str (GeoJSON geometry, for MapLibre) | 0 | 77 | — | — |  |
