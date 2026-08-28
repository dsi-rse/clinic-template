import * as Plot from '@observablehq/plot'
import { Picker, Item } from '@adobe/react-spectrum'
import PlotFigure from '../components/PlotFigure'
import { useQuery } from '../lib/useQuery'
import { useFilters } from '../store/filters'

interface DemoRow {
  city: string
  category: string
  value: number
  date: string
}

export default function OverviewPage() {
  const { city, setCity } = useFilters()

  const where = city === 'All' ? '' : `WHERE city = '${city}'`

  // City options come from the data itself — never hardcode column values.
  const { data: cityRows } = useQuery<{ city: string }>(
    'SELECT DISTINCT city FROM demo ORDER BY city',
  )
  const cities = ['All', ...(cityRows ?? []).map((r) => r.city)]

  const { data: rows, loading } = useQuery<DemoRow>(
    `SELECT city, category, value, CAST(date AS VARCHAR) AS date FROM demo ${where} LIMIT 2000`,
  )

  const { data: byCat } = useQuery<{ category: string; avg_value: number }>(
    `SELECT category, AVG(value) AS avg_value FROM demo ${where} GROUP BY category ORDER BY avg_value DESC`,
  )

  return (
    <div style={{ padding: '1rem' }}>
      <h1>Overview</h1>
      <Picker
        label="City"
        selectedKey={city}
        onSelectionChange={(key) => setCity(String(key))}
      >
        {cities.map((c) => (
          <Item key={c}>{c}</Item>
        ))}
      </Picker>

      {loading && <p>Loading data…</p>}

      {rows && rows.length > 0 && (
        <figure>
          <figcaption>Value over time</figcaption>
          <PlotFigure
            options={{
              width: 700,
              marks: [
                Plot.dot(rows, {
                  x: (d: DemoRow) => new Date(d.date),
                  y: 'value',
                  stroke: 'category',
                  tip: true,
                }),
                Plot.frame(),
              ],
            }}
          />
        </figure>
      )}

      {byCat && byCat.length > 0 && (
        <figure>
          <figcaption>Average value by category</figcaption>
          <PlotFigure
            options={{
              width: 700,
              marks: [
                Plot.barY(byCat, { x: 'category', y: 'avg_value', fill: 'category', tip: true }),
                Plot.frame(),
              ],
            }}
          />
        </figure>
      )}
    </div>
  )
}
