import { useState, useEffect } from 'react'
import { query } from './duckdb'

const cache = new Map<string, unknown[]>()

export function useQuery<T = Record<string, unknown>>(sql: string) {
  const [data, setData] = useState<T[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false
    if (cache.has(sql)) {
      setData(cache.get(sql) as T[])
      setLoading(false)
      return
    }
    setLoading(true)
    query<T>(sql)
      .then((rows) => {
        if (!cancelled) {
          cache.set(sql, rows)
          setData(rows)
          setLoading(false)
        }
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setError(err)
          setLoading(false)
        }
      })
    return () => {
      cancelled = true
    }
  }, [sql])

  return { data, loading, error }
}
