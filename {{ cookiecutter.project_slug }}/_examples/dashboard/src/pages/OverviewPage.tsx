import * as Plot from '@observablehq/plot'
import PlotFigure from '../components/PlotFigure'
import Card from '../components/Card'
import { useQuery } from '../lib/useQuery'
import { useFilters, filterSql } from '../store/filters'

const ACCENT = '#2a78d6'
const DIMMED = '#9ec5f4' // lighter step of the same ramp, for de-emphasised bars

const compact = new Intl.NumberFormat('en-US', {
  notation: 'compact',
  maximumFractionDigits: 1,
})

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <div
      style={{
        flex: '1 1 180px',
        background: '#fcfcfb',
        border: '1px solid rgba(11, 11, 11, 0.1)',
        borderRadius: 8,
        padding: '12px 16px',
      }}
    >
      <div style={{ fontSize: 13, color: '#52514e' }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 600, color: '#0b0b0b' }}>{value}</div>
    </div>
  )
}

export default function OverviewPage() {
  const { requestType, yearRange } = useFilters()
  const where = filterSql(requestType, yearRange)
  // The per-type charts ignore the type filter (they ARE the type breakdown);
  // the selected type is highlighted instead.
  const whereAllTypes = filterSql('All', yearRange)

  const { data: stats, loading } = useQuery<{
    total: number
    completed: number
    median_days: number
  }>(
    `SELECT CAST(COUNT(*) AS INT) AS total,
            CAST(COUNT(*) FILTER (WHERE status = 'Completed') AS INT) AS completed,
            CAST(median(date_diff('day', creation_date, completion_date)) AS DOUBLE) AS median_days
     FROM reqs_311 WHERE ${where}`,
  )

  const { data: monthly } = useQuery<{ month: string; n: number }>(
    `SELECT CAST(date_trunc('month', creation_date) AS VARCHAR) AS month,
            CAST(COUNT(*) AS INT) AS n
     FROM reqs_311 WHERE ${where}
     GROUP BY month ORDER BY month`,
  )

  const { data: byType } = useQuery<{ request_type: string; n: number }>(
    `SELECT type_of_service_request AS request_type, CAST(COUNT(*) AS INT) AS n
     FROM reqs_311 WHERE ${whereAllTypes}
     GROUP BY request_type ORDER BY n DESC`,
  )

  const { data: closeDays } = useQuery<{ request_type: string; days: number }>(
    `SELECT type_of_service_request AS request_type,
            CAST(median(date_diff('day', creation_date, completion_date)) AS DOUBLE) AS days
     FROM reqs_311 WHERE ${whereAllTypes} AND completion_date IS NOT NULL
     GROUP BY request_type ORDER BY days DESC`,
  )

  const { data: byDow } = useQuery<{ dow: string; d: number; n: number }>(
    `SELECT dayname(creation_date) AS dow, CAST(isodow(creation_date) AS INT) AS d,
            CAST(COUNT(*) AS INT) AS n
     FROM reqs_311 WHERE ${where}
     GROUP BY dow, d ORDER BY d`,
  )

  const s = stats?.[0]
  const typeFill = (d: { request_type: string }) =>
    requestType === 'All' || d.request_type === requestType ? ACCENT : DIMMED

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, paddingTop: 16 }}>
      {loading && <p>Loading data…</p>}

      {s && s.total > 0 && (
        <>
          <StatTile label="Total requests" value={compact.format(s.total)} />
          <StatTile label="Completed" value={`${((100 * s.completed) / s.total).toFixed(1)}%`} />
          <StatTile label="Median days to close" value={s.median_days.toFixed(0)} />
        </>
      )}

      {monthly && monthly.length > 0 && (
        <Card
          title={`Requests per month${requestType === 'All' ? '' : ` — ${requestType.toLowerCase()}`}`}
          flex="1 1 100%"
        >
          <PlotFigure
            options={{
              width: 1000,
              height: 240,
              y: { label: 'Requests', grid: true },
              x: { label: null },
              marks: [
                Plot.areaY(monthly, {
                  x: (d: { month: string }) => new Date(d.month),
                  y: 'n',
                  fill: ACCENT,
                  fillOpacity: 0.1,
                }),
                Plot.lineY(monthly, {
                  // Channel labels + formats control what the tooltip says.
                  x: { value: (d: { month: string }) => new Date(d.month), label: 'Month' },
                  y: { value: 'n', label: 'Requests' },
                  stroke: ACCENT,
                  strokeWidth: 2,
                  tip: {
                    format: {
                      x: (d: Date) => d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
                    },
                  },
                }),
                Plot.ruleY([0]),
              ],
            }}
          />
        </Card>
      )}

      {byType && byType.length > 0 && (
        <Card title="Requests by type">
          <PlotFigure
            options={{
              width: 480,
              height: 320,
              marginLeft: 260,
              x: { label: 'Requests' },
              y: { label: null },
              marks: [
                Plot.barX(byType, {
                  y: 'request_type',
                  x: 'n',
                  fill: typeFill,
                  sort: { y: '-x' },
                  tip: true,
                }),
              ],
            }}
          />
        </Card>
      )}

      {closeDays && closeDays.length > 0 && (
        <Card title="Median days to close, by type">
          <PlotFigure
            options={{
              width: 480,
              height: 320,
              marginLeft: 260,
              x: { label: 'Days' },
              y: { label: null },
              marks: [
                Plot.barX(closeDays, {
                  y: 'request_type',
                  x: 'days',
                  fill: typeFill,
                  sort: { y: '-x' },
                  tip: true,
                }),
              ],
            }}
          />
        </Card>
      )}

      {byDow && byDow.length > 0 && (
        <Card title="Requests by day of week">
          <PlotFigure
            options={{
              width: 480,
              height: 240,
              y: { label: 'Requests', grid: true },
              // Rows arrive Monday-first from SQL (isodow); keep that order.
              x: { label: null, domain: byDow.map((d) => d.dow) },
              marks: [
                Plot.barY(byDow, {
                  x: 'dow',
                  y: 'n',
                  fill: ACCENT,
                  tip: true,
                }),
                Plot.ruleY([0]),
              ],
            }}
          />
        </Card>
      )}
    </div>
  )
}
