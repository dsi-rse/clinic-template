import { test, expect } from '@playwright/test'

test('has Trends and Map tabs', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('tab', { name: 'Trends' })).toBeVisible()
  await expect(page.getByRole('tab', { name: 'Map' })).toBeVisible()
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
})
