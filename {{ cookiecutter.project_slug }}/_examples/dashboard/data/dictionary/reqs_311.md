# reqs_311 — Data Dictionary

Toy sample of Chicago 311 service requests (Chicago Data Portal via the Kaggle 311 archive): 12 request types, 50% random sample, 2011 onward, duplicate-flagged rows removed, sorted by creation_date. `community_area` joins to community_areas.area_num. `status` and `completion_date` are NULL for vacant-building reports (that dataset has no status column). Location columns are dropped to keep the file under Cloudflare Pages' 25 MiB per-asset limit.

**Rows:** 1605643

| Column | Type | Nulls | Unique | Min | Max | Sample Values |
|--------|------|-------|--------|-----|-----|---------------|
| creation_date | datetime64[us] | 0 | 3261 | 2011-01-01 00:00:00 | 2019-12-05 00:00:00 | 2011-01-01 00:00:00, 2011-01-01 00:00:00, 2011-01-01 00:00:00, 2011-01-01 00:00:00, 2011-01-01 00:00:00 |
| status | object | 29118 | 2 | Completed | Open | Completed, Completed, Completed, Completed, Completed |
| completion_date | datetime64[us] | 41191 | 3126 | 2011-01-01 00:00:00 | 2019-12-05 00:00:00 | 2011-01-03 00:00:00, 2011-04-05 00:00:00, 2011-01-14 00:00:00, 2011-01-17 00:00:00, 2011-01-03 00:00:00 |
| type_of_service_request | str | 0 | 13 | Abandoned Vehicle Complaint | Vacant/Abandoned Building | Graffiti Removal, Alley Light Out, Pothole in Street, Street Light - 1/Out, Sanitation Code Violation |
| community_area | int64 | 0 | 77 | 1 | 77 | 5, 15, 21, 74, 21 |
