import { lazy, Suspense } from 'react'
import { Item, Picker, RangeSlider, TabList, TabPanels, Tabs } from '@adobe/react-spectrum'
import OverviewPage from './pages/OverviewPage'
import { useQuery } from './lib/useQuery'
import { useFilters, DATA_YEARS } from './store/filters'

// Lazy-load the heavy tabs so MapLibre isn't downloaded and parsed by
// visitors who never open them (the Trends tab is the landing view).
const MapPage = lazy(() => import('./pages/MapPage'))
const SqlPage = lazy(() => import('./pages/SqlPage'))

export default function App() {
  const { requestType, setRequestType, yearRange, setYearRange } = useFilters()

  // Request-type options come from the data itself — never hardcode column values.
  const { data: typeRows, error } = useQuery<{ request_type: string }>(
    'SELECT DISTINCT type_of_service_request AS request_type FROM reqs_311 ORDER BY request_type',
  )
  const types = ['All', ...(typeRows ?? []).map((r) => r.request_type)]

  return (
    <div style={{ maxWidth: 1080, margin: '0 auto', padding: '1rem 1.5rem 3rem' }}>
      <header>
        <h1 style={{ marginBottom: 4 }}>Chicago 311 Service Requests</h1>
        <p style={{ marginTop: 0, color: '#52514e' }}>
          Toy sample of {DATA_YEARS.min}–{DATA_YEARS.max} service requests, aggregated to
          community areas.
        </p>
      </header>

      {error ? (
        <p>
          The <code>reqs_311</code> dataset is not loaded. Run{' '}
          <code>make dashboard-data</code> to pull it from Box (see{' '}
          <code>data/dictionary/reqs_311.md</code>).
        </p>
      ) : (
        <>
          <div
            style={{ display: 'flex', gap: 32, flexWrap: 'wrap', alignItems: 'end', marginBottom: 8 }}
          >
            <Picker
              label="Request type"
              selectedKey={requestType}
              onSelectionChange={(key) => setRequestType(String(key))}
            >
              {types.map((t) => (
                <Item key={t}>{t}</Item>
              ))}
            </Picker>
            <RangeSlider
              label="Years"
              minValue={DATA_YEARS.min}
              maxValue={DATA_YEARS.max}
              defaultValue={yearRange}
              onChangeEnd={setYearRange}
              formatOptions={{ useGrouping: false }}
              width="size-3000"
            />
          </div>

          <Tabs aria-label="Dashboard views">
            <TabList>
              <Item key="trends">Trends</Item>
              <Item key="map">Map</Item>
              <Item key="sql">SQL</Item>
            </TabList>
            <TabPanels>
              <Item key="trends">
                <OverviewPage />
              </Item>
              <Item key="map">
                <Suspense fallback={<p style={{ paddingTop: 16 }}>Loading…</p>}>
                  <MapPage />
                </Suspense>
              </Item>
              <Item key="sql">
                <Suspense fallback={<p style={{ paddingTop: 16 }}>Loading…</p>}>
                  <SqlPage />
                </Suspense>
              </Item>
            </TabPanels>
          </Tabs>
        </>
      )}
    </div>
  )
}
