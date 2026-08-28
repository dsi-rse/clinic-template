import { test, expect } from '@playwright/test'

test('nav has Overview, Map, and Chicago links', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('link', { name: 'Overview' })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Map' })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Chicago' })).toBeVisible()
})

test('Overview renders a chart once DuckDB loads', async ({ page }) => {
  await page.goto('/')
  // Wait generously for DuckDB wasm to initialise and render a chart
  await expect(page.locator('figure svg').first()).toBeVisible({ timeout: 30_000 })
})
