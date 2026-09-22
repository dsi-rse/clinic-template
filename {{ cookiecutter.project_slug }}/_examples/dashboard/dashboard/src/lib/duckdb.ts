import * as duckdb from '@duckdb/duckdb-wasm'
import manifest from '../../data.manifest.json'

let dbPromise: Promise<duckdb.AsyncDuckDB> | null = null

function getDB(): Promise<duckdb.AsyncDuckDB> {
  if (!dbPromise) {
    dbPromise = (async () => {
      // Load the wasm bundles from jsDelivr rather than bundling them:
      // they are >25 MiB each, which exceeds Cloudflare Pages' per-file limit.
      const bundle = await duckdb.selectBundle(duckdb.getJsDelivrBundles())
      // Same-origin blob wrapper so the cross-origin worker script can load.
      const workerUrl = URL.createObjectURL(
        new Blob([`importScripts("${bundle.mainWorker!}");`], { type: 'text/javascript' }),
      )
      const worker = new Worker(workerUrl)
      URL.revokeObjectURL(workerUrl)
      const logger = new duckdb.ConsoleLogger()
      const db = new duckdb.AsyncDuckDB(logger, worker)
      await db.instantiate(bundle.mainModule)
      // Return TIMESTAMP/DATE columns as JS Dates instead of epoch numbers.
      await db.open({ query: { castTimestampToDate: true } })

      const conn = await db.connect()

      // Every manifest entry becomes a view named by its parquet file stem,
      // served from public/data/. URLs must be absolute: the DB runs in a
      // blob-wrapped worker that can't resolve relative paths.
      const base = new URL(import.meta.env.BASE_URL, window.location.href).href
      const names = new Set<string>(manifest.map((entry) => entry.name))
      for (const name of names) {
        const filename = `${name}.parquet`
        try {
          await db.registerFileURL(
            filename,
            `${base}data/${filename}`,
            duckdb.DuckDBDataProtocol.HTTP,
            false,
          )
          await conn.query(
            `CREATE OR REPLACE VIEW "${name}" AS SELECT * FROM parquet_scan('${filename}')`,
          )
        } catch (e) {
          // A manifest entry that hasn't been pulled yet (`make dashboard-data`)
          // shouldn't take down the views that do exist.
          console.warn(`skipping view "${name}": ${filename} not available`, e)
        }
      }

      await conn.close()
      return db
    })()
  }
  return dbPromise
}

export async function query<T = Record<string, unknown>>(sql: string): Promise<T[]> {
  const db = await getDB()
  const conn = await db.connect()
  try {
    const result = await conn.query(sql)
    return result.toArray().map((r) => r.toJSON()) as T[]
  } finally {
    await conn.close()
  }
}
