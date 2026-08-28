import * as duckdb from '@duckdb/duckdb-wasm'
import duckdb_wasm from '@duckdb/duckdb-wasm/dist/duckdb-mvp.wasm?url'
import mvp_worker from '@duckdb/duckdb-wasm/dist/duckdb-browser-mvp.worker.js?url'
import duckdb_wasm_eh from '@duckdb/duckdb-wasm/dist/duckdb-eh.wasm?url'
import eh_worker from '@duckdb/duckdb-wasm/dist/duckdb-browser-eh.worker.js?url'
import manifest from '../../data.manifest.json'

const MANUAL_BUNDLES: duckdb.DuckDBBundles = {
  mvp: {
    mainModule: duckdb_wasm,
    mainWorker: mvp_worker,
  },
  eh: {
    mainModule: duckdb_wasm_eh,
    mainWorker: eh_worker,
  },
}

let dbPromise: Promise<duckdb.AsyncDuckDB> | null = null

function getDB(): Promise<duckdb.AsyncDuckDB> {
  if (!dbPromise) {
    dbPromise = (async () => {
      const bundle = await duckdb.selectBundle(MANUAL_BUNDLES)
      const worker = new Worker(bundle.mainWorker!)
      const logger = new duckdb.ConsoleLogger()
      const db = new duckdb.AsyncDuckDB(logger, worker)
      await db.instantiate(bundle.mainModule)

      const conn = await db.connect()

      // Every manifest entry becomes a view named by its parquet file stem,
      // served from public/data/.
      const base = import.meta.env.BASE_URL
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
