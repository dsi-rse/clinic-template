import { create } from 'zustand'

// The extract is trimmed to complete years: Chicago migrated 311 systems in
// late 2018, so later years in this dataset are sparse/partial.
export const DATA_YEARS = { min: 2011, max: 2017 }

export interface YearRange {
  start: number
  end: number
}

interface FiltersState {
  requestType: string
  setRequestType: (requestType: string) => void
  yearRange: YearRange
  setYearRange: (yearRange: YearRange) => void
  // Which metric the choropleth colors by (a key of METRICS in MapPage)
  mapMetric: string
  setMapMetric: (mapMetric: string) => void
}

export const useFilters = create<FiltersState>((set) => ({
  requestType: 'All',
  setRequestType: (requestType) => set({ requestType }),
  yearRange: { start: DATA_YEARS.min, end: DATA_YEARS.max },
  setYearRange: (yearRange) => set({ yearRange }),
  mapMetric: 'requests',
  setMapMetric: (mapMetric) => set({ mapMetric }),
}))

// SQL predicate for the global filters. `prefix` qualifies columns when
// reqs_311 is aliased in a join (e.g. 'r.').
export function filterSql(
  requestType: string,
  { start, end }: YearRange,
  prefix = '',
): string {
  const clauses = [
    `${prefix}creation_date >= DATE '${start}-01-01'`,
    `${prefix}creation_date < DATE '${end + 1}-01-01'`,
  ]
  if (requestType !== 'All') {
    clauses.push(`${prefix}type_of_service_request = '${requestType}'`)
  }
  return clauses.join(' AND ')
}
