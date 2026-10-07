import { test, expect, type Page, type ConsoleMessage } from '@playwright/test'

// Walks the real golden path a user would: landing -> category -> product
// dashboard -> explore -> review drawer. Every assertion here checks for
// real page content (text that comes from the actual exported JSON), not a
// mocked fixture. Console errors anywhere during the walk fail the run --
// a silently broken fetch or render often never throws, it just logs.

function trackConsoleErrors(page: Page): string[] {
  const errors: string[] = []
  page.on('console', (msg: ConsoleMessage) => {
    if (msg.type() === 'error') errors.push(msg.text())
  })
  page.on('pageerror', (err) => errors.push(`pageerror: ${err.message}`))
  return errors
}

test('landing page shows the Wearables & Fitness category', async ({ page }) => {
  const errors = trackConsoleErrors(page)
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Wearables & Fitness' })).toBeVisible()
  await page.screenshot({ path: 'tests/results/01-landing.png', fullPage: true })
  expect(errors, `console errors on landing page: ${errors.join('; ')}`).toEqual([])
})

test('full golden path: landing -> category -> dashboard -> explore -> review drawer', async ({ page }) => {
  const errors = trackConsoleErrors(page)

  await page.goto('/')
  await page.getByRole('heading', { name: 'Wearables & Fitness' }).click()

  await expect(page.getByRole('heading', { name: 'WHOOP' })).toBeVisible()
  await page.screenshot({ path: 'tests/results/02-category.png', fullPage: true })

  await page.getByRole('heading', { name: 'WHOOP' }).click()

  await expect(page.getByRole('heading', { name: /WHOOP: Priority Insights/ })).toBeVisible()
  await page.screenshot({ path: 'tests/results/03-dashboard-insights.png', fullPage: true })

  await page.getByRole('button', { name: 'Explore all' }).click()

  await expect(page.getByRole('heading', { name: 'Category & subcategory breakdown' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Watch categories' }).first()).toBeVisible()
  const trendSection = page.locator('#trend-view')
  await expect(trendSection).toBeVisible()
  // Rising & falling renders a real chart (recharts -> svg) once trend data loads.
  await expect(trendSection.locator('svg').first()).toBeVisible({ timeout: 10_000 })
  await page.screenshot({ path: 'tests/results/04-dashboard-explore.png', fullPage: true })

  // Open the review drawer from the first category row's "N reviews ->" button.
  const viewReviewsButton = page.getByRole('button', { name: /reviews →/ }).first()
  await viewReviewsButton.click()

  const drawer = page.locator('aside.fixed')
  await expect(drawer).toBeVisible()
  // A real review's text paragraph, not a placeholder/empty state.
  const reviewText = drawer.locator('p.text-sm.leading-relaxed').first()
  await expect(reviewText).toBeVisible({ timeout: 10_000 })
  await expect(reviewText).not.toHaveText('')
  const text = await reviewText.textContent()
  expect((text ?? '').trim().length, 'review drawer text looked empty/placeholder').toBeGreaterThan(10)
  await page.screenshot({ path: 'tests/results/05-review-drawer.png', fullPage: true })

  expect(errors, `console errors during golden path: ${errors.join('; ')}`).toEqual([])
})
