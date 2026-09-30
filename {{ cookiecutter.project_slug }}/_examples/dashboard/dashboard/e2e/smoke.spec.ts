import { test, expect } from '@playwright/test'

test('has Trends, Map, and SQL tabs', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('tab', { name: 'Trends' })).toBeVisible()
  await expect(page.getByRole('tab', { name: 'Map' })).toBeVisible()
  await expect(page.getByRole('tab', { name: 'SQL' })).toBeVisible()
})

test('Trends renders a chart once DuckDB loads', async ({ page }) => {
  await page.goto('/')
  // Wait generously for DuckDB wasm to initialise and render a chart
  await expect(page.locator('figure svg').first()).toBeVisible({ timeout: 30_000 })
})

test('Map tab renders the choropleth', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('tab', { name: 'Map' }).click()
  await expect(page.locator('.maplibregl-canvas')).toBeVisible({ timeout: 30_000 })
  // The Top-15 ranking only renders once area data has actually loaded — the
  // canvas alone proves nothing about data.
  await expect(page.locator('figure svg').first()).toBeVisible({ timeout: 15_000 })
})

test('request-type filter changes the numbers', async ({ page }) => {
  await page.goto('/')
  const total = page.getByTestId('stat-total')
  await expect(total).toHaveText(/\d/, { timeout: 30_000 })
  const before = (await total.textContent())!.trim()

  await page.getByRole('button', { name: /Request type/ }).click()
  await page.getByRole('option').nth(1).click()

  await expect(total).not.toHaveText(before, { timeout: 30_000 })
})

test('SQL console runs the default query', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('tab', { name: 'SQL' }).click()
  await expect(page.locator('table tbody tr').first()).toBeVisible({ timeout: 30_000 })
})
