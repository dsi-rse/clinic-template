# reqs_311 — Data Dictionary

Toy sample of Chicago 311 service requests (Chicago Data Portal via the Kaggle 311 archive): 12 request types, 50% random sample, 2011 onward, duplicate-flagged rows removed. `community_area` joins to community_areas.area_num. `status` is NULL for vacant-building reports (that dataset has no status column).

**Rows:** 1605643

| Column | Type | Nulls | Unique | Min | Max | Sample Values |
|--------|------|-------|--------|-----|-----|---------------|
| creation_date | datetime64[us] | 0 | 3261 | 2011-01-01 00:00:00 | 2019-12-05 00:00:00 | 2015-09-24 00:00:00, 2018-08-31 00:00:00, 2012-01-26 00:00:00, 2011-04-05 00:00:00, 2014-05-22 00:00:00 |
| status | object | 29118 | 2 | Completed | Open | Completed, Completed, Completed, Completed, Completed |
| completion_date | datetime64[us] | 41191 | 3126 | 2011-01-01 00:00:00 | 2019-12-05 00:00:00 | 2015-10-22 00:00:00, 2018-08-31 00:00:00, 2012-01-26 00:00:00, 2011-04-15 00:00:00, 2014-05-22 00:00:00 |
| service_request_number | str | 0 | 1594618 | 11-00000212 | 19-00169287 | 15-05033236, 18-02537719, 12-00116544, 11-00630606, 14-00765327 |
| type_of_service_request | str | 0 | 13 | Abandoned Vehicle Complaint | Vacant/Abandoned Building | Rodent Baiting/Rat Complaint, Sanitation Code Violation, Tree Trim, Pothole in Street, Tree Trim |
| community_area | int64 | 0 | 77 | 1 | 77 | 19, 6, 17, 63, 71 |
| latitude | float64 | 1119 | 790693 | 0.0 | 42.02296045252183 | 41.93399493553111, 41.94225995167597, 41.94174478009426, 41.79118757971278, 41.74851155933513 |
| longitude | float64 | 1119 | 790693 | -87.93520003121188 | 0.0 | -87.76265695744752, -87.64223930140751, -87.82401237748044, -87.69846450143315, -87.65489884097713 |
