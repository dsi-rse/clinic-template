import { useRef, useEffect } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import * as Plot from '@observablehq/plot'
import { Picker, Item } from '@adobe/react-spectrum'
import PlotFigure from '../components/PlotFigure'
import { useQuery } from '../lib/useQuery'
import { useFilters } from '../store/filters'

// Sequential single-hue ramp, light → dark (higher value = darker).
const RAMP = ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b']
const ACCENT = '#2a78d6'

const INDICATORS = {
  hardship_index: {
    label: 'Hardship index',
    format: (v: number) => v.toFixed(0),
  },
  per_capita_income: {
    label: 'Per-capita income',
    format: (v: number) => `$${Math.round(v).toLocaleString()}`,
  },
  pct_below_poverty: {
    label: '% households below poverty',
    format: (v: number) => `${v.toFixed(1)}%`,
  },
  pct_unemployed: {
    label: '% unemployed (aged 16+)',
    format: (v: number) => `${v.toFixed(1)}%`,
  },
  pct_no_hs_diploma: {
    label: '% without HS diploma (aged 25+)',
    format: (v: number) => `${v.toFixed(1)}%`,
  },
  pct_housing_crowded: {
    label: '% housing crowded',
    format: (v: number) => `${v.toFixed(1)}%`,
  },
  pct_dependent_age: {
    label: '% aged under 18 or over 64',
    format: (v: number) => `${v.toFixed(1)}%`,
  },
} as const

type IndicatorKey = keyof typeof INDICATORS
type AreaRow = { name: string; geometry_geojson: string } & Record<IndicatorKey, number>

const INDICATOR_KEYS = Object.keys(INDICATORS) as IndicatorKey[]

function fillExpression(key: IndicatorKey, min: number, max: number): maplibregl.ExpressionSpecification {
  const stops = RAMP.flatMap((color, i) => [min + ((max - min) * i) / (RAMP.length - 1), color])
  return ['interpolate', ['linear'], ['get', key], ...stops] as maplibregl.ExpressionSpecification
}

export default function ChicagoPage() {
  const { indicator, setIndicator } = useFilters()
  const key = indicator as IndicatorKey
  const meta = INDICATORS[key]

  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<maplibregl.Map | null>(null)
  const keyRef = useRef<IndicatorKey>(key)
  keyRef.current = key

  const { data: areas, loading, error } = useQuery<AreaRow>(
    `SELECT name, geometry_geojson, ${INDICATOR_KEYS.join(', ')} FROM community_areas`,
  )

  const values = (areas ?? []).map((a) => a[key])
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
      const expr = fillExpression(key, min, max)
      if (map.getSource('areas')) {
        map.setPaintProperty('areas-fill', 'fill-color', expr)
        return
      }
      const featureCollection = {
        type: 'FeatureCollection' as const,
        features: areas.map((a) => ({
          type: 'Feature' as const,
          geometry: JSON.parse(a.geometry_geojson),
          properties: Object.fromEntries([['name', a.name], ...INDICATOR_KEYS.map((k) => [k, a[k]])]),
        })),
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
        const k = keyRef.current
        popup
          .setLngLat(e.lngLat)
          .setHTML(`<b>${props.name}</b><br>${INDICATORS[k].label}: ${INDICATORS[k].format(Number(props[k]))}`)
          .addTo(map)
      })
      map.on('mouseleave', 'areas-fill', () => popup.remove())
    }

    if (map.loaded()) {
      apply()
    } else {
      map.on('load', apply)
    }
  }, [areas, key, min, max])

  if (error) {
    return (
      <div style={{ padding: '1rem' }}>
        <h1>Chicago</h1>
        <p>
          The <code>community_areas</code> dataset is not loaded. Run{' '}
          <code>make dashboard-data</code> after adding its Box link to{' '}
          <code>data.manifest.json</code> (see <code>data/dictionary/community_areas.md</code>).
        </p>
      </div>
    )
  }

  const top15 = [...(areas ?? [])]
    .sort((a, b) => b[key] - a[key])
    .slice(0, 15)
    .map((a) => ({ name: a.name, value: a[key] }))

  return (
    <div style={{ padding: '1rem' }}>
      <h1>Chicago Community Areas</h1>

      <Picker
        label="Indicator"
        selectedKey={key}
        onSelectionChange={(k) => setIndicator(String(k))}
      >
        {INDICATOR_KEYS.map((k) => (
          <Item key={k}>{INDICATORS[k].label}</Item>
        ))}
      </Picker>

      {loading && <p>Loading data…</p>}

      <figure>
        <figcaption>{meta.label} by community area</figcaption>
        <div ref={mapRef} style={{ width: '100%', maxWidth: 700, height: 520 }} />
        {areas && areas.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, maxWidth: 700, marginTop: 4 }}>
            <span style={{ fontSize: 12, color: '#52514e' }}>{meta.format(min)}</span>
            <div
              style={{
                flex: 1,
                height: 10,
                borderRadius: 4,
                background: `linear-gradient(to right, ${RAMP.join(', ')})`,
              }}
            />
            <span style={{ fontSize: 12, color: '#52514e' }}>{meta.format(max)}</span>
          </div>
        )}
      </figure>

      {top15.length > 0 && (
        <figure>
          <figcaption>Top 15 community areas — {meta.label.toLowerCase()}</figcaption>
          <PlotFigure
            options={{
              width: 700,
              marginLeft: 150,
              x: { label: meta.label },
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
        </figure>
      )}

      {areas && areas.length > 0 && (
        <figure>
          <figcaption>Per-capita income vs. hardship index</figcaption>
          <PlotFigure
            options={{
              width: 700,
              x: { label: 'Per-capita income ($)' },
              y: { label: 'Hardship index' },
              marks: [
                Plot.dot(areas, {
                  x: 'per_capita_income',
                  y: 'hardship_index',
                  fill: ACCENT,
                  fillOpacity: 0.75,
                  r: 4,
                  channels: { name: 'name' },
                  tip: true,
                }),
                Plot.frame(),
              ],
            }}
          />
        </figure>
      )}
    </div>
  )
}
