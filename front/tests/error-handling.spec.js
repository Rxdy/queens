import { test, expect } from '@playwright/test'
import { dismissWelcome, paint4x4 } from './helpers.js'

test.beforeEach(async ({ page }) => {
  await page.goto('/')
  await dismissWelcome(page)
})

test('erreur réseau : message affiché si le TRM est indisponible', async ({ page }) => {
  // Intercepte les appels /api/solve et retourne une erreur réseau
  await page.route('**/api/solve', route => route.abort('failed'))

  await paint4x4(page)
  await page.locator('.solve-icon-btn').click()

  await expect(page.locator('.error-message')).toBeVisible({ timeout: 10_000 })
})

test('erreur réseau : message affiché si l\'API retourne 500', async ({ page }) => {
  await page.route('**/api/solve', route =>
    route.fulfill({ status: 500, body: JSON.stringify({ detail: 'Erreur interne simulée' }) })
  )

  await paint4x4(page)
  await page.locator('.solve-icon-btn').click()

  await expect(page.locator('.error-message')).toBeVisible({ timeout: 10_000 })
})

test('erreur réseau : aucune solution → message explicatif affiché', async ({ page }) => {
  // Simule une réponse valide mais avec 0 solutions
  await page.route('**/api/solve', route =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        solutions: [],
        performance: { execution_time: 0.001, iterations: 1, solutions_count: 0, solutions_per_second: 0 },
      }),
    })
  )

  await paint4x4(page)
  await page.locator('.solve-icon-btn').click()

  await expect(page.locator('.error-message')).toBeVisible({ timeout: 10_000 })
  await expect(page.locator('.error-message')).toContainText('solution')
})

test('erreur : grille incomplète → bouton Résoudre désactivé', async ({ page }) => {
  await page.locator('.size-selector select').selectOption('4')
  // Ne peindre qu'une cellule
  await page.locator('.color-btn').first().click()
  await page.locator('.cell[data-row="0"][data-col="0"]').dispatchEvent('mousedown', { button: 0 })

  await expect(page.locator('.solve-icon-btn')).toBeDisabled()
})

test('erreur : le titre du bouton Résoudre indique le nombre de cases vides', async ({ page }) => {
  await page.locator('.size-selector select').selectOption('4')
  // Grille vide = 16 cases vides
  const title = await page.locator('.solve-icon-btn').getAttribute('title')
  expect(title).toMatch(/16/)
  expect(title).toMatch(/vide/)
})
