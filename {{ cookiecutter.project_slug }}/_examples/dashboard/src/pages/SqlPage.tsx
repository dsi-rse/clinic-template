import { useEffect, useState } from 'react'
import { ActionButton, Button, TextArea } from '@adobe/react-spectrum'
import Card from '../components/Card'
import { query } from '../lib/duckdb'
import manifest from '../../data.manifest.json'

const EXAMPLES: Record<string, string> = {
  'Top request types': `SELECT type_of_service_request AS type, COUNT(*) AS n
FROM reqs_311
GROUP BY type
ORDER BY n DESC
LIMIT 10`,
  'Requests per year': `SELECT year(creation_date) AS year, COUNT(*) AS n
FROM reqs_311
GROUP BY year
ORDER BY year`,
  'Join to community areas': `SELECT ca.name, COUNT(*) AS n
FROM reqs_311 r
JOIN community_areas ca ON r.community_area = ca.area_num
GROUP BY ca.name
ORDER BY n DESC
LIMIT 10`,
}

const DEFAULT_SQL = EXAMPLES['Top request types']
const MAX_ROWS = 200

type Row = Record<string, unknown>

const isNumeric = (v: unknown) => typeof v === 'number' || typeof v === 'bigint'

export default function SqlPage() {
  const [sql, setSql] = useState(DEFAULT_SQL)
  const [rows, setRows] = useState<Row[] | null>(null)
  const [elapsed, setElapsed] = useState(0)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function run(text: string) {
    setRunning(true)
    setError(null)
    const t0 = performance.now()
    try {
      // Cap SELECT-style queries in SQL: without this, `SELECT * FROM reqs_311`
      // materializes 1.6M row objects in the browser before the display cap —
      // enough to crash a tab. DDL statements pass through unwrapped.
      const trimmed = text.trim().replace(/;+\s*$/, '')
      const capped = /^\s*(select|with|from|pivot|describe|show|summarize)\b/i.test(trimmed)
        ? `SELECT * FROM (${trimmed}) LIMIT ${MAX_ROWS + 1}`
        : trimmed
      const result = await query<Row>(capped)
      setRows(result)
      setElapsed(performance.now() - t0)
    } catch (e) {
      setError(String(e))
      setRows(null)
    }
    setRunning(false)
  }

  // Run the default query once so the tab opens with a live result.
  useEffect(() => {
    void run(DEFAULT_SQL)
  }, [])

  const columns = rows && rows.length > 0 ? Object.keys(rows[0]) : []

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, paddingTop: 16 }}>
      <Card title="Query" flex="1 1 100%">
        <p style={{ marginTop: 0, fontSize: 13, color: '#52514e' }}>
          Queries run entirely in your browser (DuckDB-wasm) against the views{' '}
          {manifest.map((entry, i) => (
            <span key={entry.name}>
              {i > 0 && ', '}
              <code>{entry.name}</code>
            </span>
          ))}
          {' '}— one per parquet file in <code>public/data/</code>. Column docs live in{' '}
          <code>data/dictionary/&lt;name&gt;.md</code>. This tab queries the raw extract
          (2011–2019), unfiltered by the controls above. Nothing you run here can break
          anything: results are capped at {MAX_ROWS} rows, and a reload resets everything.
        </p>
        <TextArea
          aria-label="SQL query"
          value={sql}
          onChange={setSql}
          width="100%"
          height="size-1600"
          onKeyDown={(e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') void run(sql)
          }}
        />
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap', marginTop: 8 }}>
          <Button variant="accent" isPending={running} onPress={() => void run(sql)}>
            Run (⌘⏎)
          </Button>
          <span style={{ fontSize: 13, color: '#52514e' }}>Examples:</span>
          {Object.entries(EXAMPLES).map(([label, text]) => (
            <ActionButton
              key={label}
              onPress={() => {
                setSql(text)
                void run(text)
              }}
            >
              {label}
            </ActionButton>
          ))}
        </div>
      </Card>

      {error && (
        <Card title="Error" flex="1 1 100%">
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: 13, color: '#d03b3b' }}>
            {error}
          </pre>
        </Card>
      )}

      {rows && (
        <Card
          title={`Results — ${
            rows.length > MAX_ROWS
              ? `${MAX_ROWS}+ rows (showing first ${MAX_ROWS})`
              : `${rows.length.toLocaleString()} row${rows.length === 1 ? '' : 's'}`
          } in ${Math.round(elapsed)} ms`}
          flex="1 1 100%"
        >
          {rows.length === 0 ? (
            <p style={{ margin: 0, color: '#52514e' }}>No rows returned.</p>
          ) : (
            <div style={{ overflowX: 'auto', maxHeight: 480, overflowY: 'auto' }}>
              <table style={{ borderCollapse: 'collapse', fontSize: 13, fontVariantNumeric: 'tabular-nums' }}>
                <thead>
                  <tr>
                    {columns.map((c) => (
                      <th
                        key={c}
                        style={{
                          textAlign: isNumeric(rows[0][c]) ? 'right' : 'left',
                          padding: '6px 12px',
                          borderBottom: '2px solid #e1e0d9',
                          position: 'sticky',
                          top: 0,
                          background: '#fcfcfb',
                        }}
                      >
                        {c}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.slice(0, MAX_ROWS).map((row, i) => (
                    <tr key={i}>
                      {columns.map((c) => (
                        <td
                          key={c}
                          style={{
                            textAlign: isNumeric(row[c]) ? 'right' : 'left',
                            padding: '4px 12px',
                            borderBottom: '1px solid #e1e0d9',
                            color: row[c] == null ? '#898781' : '#0b0b0b',
                          }}
                        >
                          {row[c] == null ? 'NULL' : String(row[c])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
