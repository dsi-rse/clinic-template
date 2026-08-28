import { useRef, useEffect } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import * as Plot from '@observablehq/plot'
import { Picker, Item } from '@adobe/react-spectrum'
import PlotFigure from '../components/PlotFigure'
import Card from '../components/Card'
import { useQuery } from '../lib/useQuery'
import { useFilters, filterSql } from '../store/filters'

// Sequential single-hue ramp, light → dark (higher value = darker).
const RAMP = ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b']
const ACCENT = '#2a78d6'

const fmt = (v: number) => Math.round(v).toLocaleString()

// The choropleth metrics; keys must match the SQL column aliases below.
const METRICS = {
  requests: { label: 'Requests', format: fmt },
  median_days: { label: 'Median days to close', format: (v: number) => v.toFixed(0) },
  pct_completed: { label: '% completed', format: (v: number) => `${v.toFixed(1)}%` },
} as const

type MetricKey = keyof typeof METRICS
const METRIC_KEYS = Object.keys(METRICS) as MetricKey[]

type AreaRow = { name: string; geometry_geojson: string } & Record<MetricKey, number>

function fillExpression(key: MetricKey, min: number, max: number): maplibregl.ExpressionSpecification {
  const stops = RAMP.flatMap((color, i) => [min + ((max - min) * i) / (RAMP.length - 1), color])
  return ['interpolate', ['linear'], ['get', key], ...stops] as maplibregl.ExpressionSpecification
}

// Tiny inline-SVG line chart for the hover popup (popup content is an HTML string).
function sparklineSvg(values: number[]): string {
  if (values.length < 2) return ''
  const w = 140
  const h = 32
  const max = Math.max(...values, 1)
  const points = values
    .map((v, i) => `${((i / (values.length - 1)) * w).toFixed(1)},${(h - (v / max) * h).toFixed(1)}`)
    .join(' ')
  return (
    `<svg width="${w}" height="${h}" viewBox="-2 -2 ${w + 4} ${h + 4}">` +
    `<polyline points="${points}" fill="none" stroke="${ACCENT}" stroke-width="1.5"/></svg>`
  )
}

// Vertical gradient legend, overlaid on the map (dark = higher value, on top).
function MapLegend({ min, max, format }: { min: number; max: number; format: (v: number) => string }) {
  const label = { fontSize: 11, color: '#52514e', lineHeight: 1 }
  return (
    <div
      style={{
        position: 'absolute',
        top: 12,
        right: 12,
        display: 'flex',
        gap: 8,
        padding: '10px 12px',
        background: 'rgba(252, 252, 251, 0.92)',
        border: '1px solid rgba(11, 11, 11, 0.1)',
        borderRadius: 6,
      }}
    >
      <div
        style={{
          width: 10,
          height: 120,
          borderRadius: 4,
          background: `linear-gradient(to top, ${RAMP.join(', ')})`,
        }}
      />
      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <span style={label}>{format(max)}</span>
        <span style={label}>{format(min + (max - min) / 2)}</span>
        <span style={label}>{format(min)}</span>
      </div>
    </div>
  )
}

export default function MapPage() {
  const { requestType, yearRange, mapMetric, setMapMetric } = useFilters()
  const metric = (mapMetric in METRICS ? mapMetric : 'requests') as MetricKey

  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<maplibregl.Map | null>(null)
  // The popup handler is registered once; refs keep it reading current state.
  const requestTypeRef = useRef(requestType)
  requestTypeRef.current = requestType
  const metricRef = useRef<MetricKey>(metric)
  metricRef.current = metric
  const seriesRef = useRef<globalThis.Map<string, number[]>>(new globalThis.Map())

  // Aggregate 311 requests to community areas with an attribute join —
  // reqs_311.community_area matches community_areas.area_num.
  const { data: areas, loading, error } = useQuery<AreaRow>(
    `SELECT ca.name, ca.geometry_geojson,
            CAST(COUNT(r.community_area) AS INT) AS requests,
            CAST(COALESCE(median(date_diff('day', r.creation_date, r.completion_date)), 0) AS DOUBLE) AS median_days,
            CAST(COALESCE(100.0 * COUNT(*) FILTER (WHERE r.status = 'Completed')
                          / NULLIF(COUNT(r.community_area), 0), 0) AS DOUBLE) AS pct_completed
     FROM community_areas ca
     LEFT JOIN reqs_311 r
       ON r.community_area = ca.area_num AND ${filterSql(requestType, yearRange, 'r.')}
     GROUP BY ca.name, ca.geometry_geojson`,
  )

  // Per-area monthly request counts, for the popup sparkline.
  const { data: series } = useQuery<{ name: string; n: number }>(
    `SELECT ca.name, CAST(COUNT(*) AS INT) AS n
     FROM reqs_311 r
     JOIN community_areas ca ON r.community_area = ca.area_num
     WHERE ${filterSql(requestType, yearRange, 'r.')}
     GROUP BY ca.name, date_trunc('month', r.creation_date)
     ORDER BY ca.name, date_trunc('month', r.creation_date)`,
  )
  useEffect(() => {
    const byName = new globalThis.Map<string, number[]>()
    for (const row of series ?? []) {
      const values = byName.get(row.name) ?? []
      values.push(row.n)
      byName.set(row.name, values)
    }
    seriesRef.current = byName
  }, [series])

  const values = (areas ?? []).map((a) => a[metric])
  const min = Math.min(...values)
  const max = Math.max(...values)

  useEffect(() => {
    if (!mapRef.current) return
    const map = new maplibregl.Map({
      container: mapRef.current,
      // Blank background — the choropleth is the map; no basemap needed.
      style: {
        version: 8,
        sources: {},
        layers: [{ id: 'bg', type: 'background', paint: { 'background-color': '#f9f9f7' } }],
      },
      center: [-87.73, 41.83],
      zoom: 9.3,
      attributionControl: false,
    })
    mapInstanceRef.current = map
    return () => map.remove()
  }, [])

  useEffect(() => {
    const map = mapInstanceRef.current
    if (!map || !areas || areas.length === 0) return

    const apply = () => {
      const featureCollection = {
        type: 'FeatureCollection' as const,
        features: areas.map((a) => ({
          type: 'Feature' as const,
          geometry: JSON.parse(a.geometry_geojson),
          properties: Object.fromEntries([['name', a.name], ...METRIC_KEYS.map((k) => [k, a[k]])]),
        })),
      }
      const expr = fillExpression(metric, min, max)
      const source = map.getSource('areas') as maplibregl.GeoJSONSource | undefined
      if (source) {
        // Values change with the filters, so update both the data and the ramp.
        source.setData(featureCollection)
        map.setPaintProperty('areas-fill', 'fill-color', expr)
        return
      }
      map.addSource('areas', { type: 'geojson', data: featureCollection })
      map.addLayer({ id: 'areas-fill', type: 'fill', source: 'areas', paint: { 'fill-color': expr } })
      // Hairline surface-colored boundaries between fills
      map.addLayer({
        id: 'areas-line',
        type: 'line',
        source: 'areas',
        paint: { 'line-color': '#fcfcfb', 'line-width': 1 },
      })
      map.fitBounds([[-87.94, 41.64], [-87.52, 42.03]], { padding: 16, duration: 0 })

      const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false })
      map.on('mousemove', 'areas-fill', (e) => {
        const props = e.features?.[0]?.properties
        if (!props) return
        const k = metricRef.current
        const requestLabel =
          requestTypeRef.current === 'All' ? 'All requests' : requestTypeRef.current
        const spark = sparklineSvg(seriesRef.current.get(String(props.name)) ?? [])
        popup
          .setLngLat(e.lngLat)
          .setHTML(
            `<b>${props.name}</b><br>` +
              `${METRICS[k].label}: ${METRICS[k].format(Number(props[k]))}<br>` +
              (spark
                ? `${spark}<br><span style="color:#52514e">${requestLabel} per month</span>`
                : ''),
          )
          .addTo(map)
      })
      map.on('mouseleave', 'areas-fill', () => popup.remove())
    }

    if (map.loaded()) {
      apply()
    } else {
      map.on('load', apply)
    }
  }, [areas, metric, min, max])

  if (error) {
    return (
      <div style={{ paddingTop: 16 }}>
        <p>
          The <code>community_areas</code> dataset is not loaded. Run{' '}
          <code>make dashboard-data</code> to pull it from Box (see{' '}
          <code>data/dictionary/community_areas.md</code>).
        </p>
      </div>
    )
  }

  const top15 = [...(areas ?? [])]
    .sort((a, b) => b[metric] - a[metric])
    .slice(0, 15)
    .map((a) => ({ name: a.name, value: a[metric] }))

  const subtitle = requestType === 'All' ? 'All 311 requests' : requestType

  return (
    <div style={{ paddingTop: 16 }}>
      <Picker
        label="Color by"
        selectedKey={metric}
        onSelectionChange={(key) => setMapMetric(String(key))}
      >
        {METRIC_KEYS.map((k) => (
          <Item key={k}>{METRICS[k].label}</Item>
        ))}
      </Picker>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, paddingTop: 16 }}>
        {loading && <p>Loading data…</p>}

        <Card title={`${METRICS[metric].label} by community area — ${subtitle.toLowerCase()}`}>
          <div style={{ position: 'relative' }}>
            <div ref={mapRef} style={{ width: '100%', height: 520 }} />
            {areas && areas.length > 0 && (
              <MapLegend min={min} max={max} format={METRICS[metric].format} />
            )}
          </div>
        </Card>

        {top15.length > 0 && (
          <Card title={`Top 15 community areas — ${METRICS[metric].label.toLowerCase()}`}>
            <PlotFigure
              options={{
                width: 480,
                height: 520,
                marginLeft: 150,
                x: { label: METRICS[metric].label },
                y: { label: null },
                marks: [
                  Plot.barX(top15, {
                    y: 'name',
                    x: 'value',
                    fill: ACCENT,
                    sort: { y: '-x' },
                    tip: true,
                  }),
                ],
              }}
            />
          </Card>
        )}
      </div>
    </div>
  )
}
