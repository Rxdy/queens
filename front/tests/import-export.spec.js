import { test, expect } from '@playwright/test'
import { dismissWelcome } from './helpers.js'

const VALID_MATRIX = `0 0 1 1
0 0 1 1
2 2 3 3
2 2 3 3`

const INVALID_MATRIX_NON_SQUARE = `0 1 2
0 1 2
0 1 2
0 1 2`

const INVALID_MATRIX_TOO_SMALL = `0 1 2
0 1 2
0 1 2`

test.beforeEach(async ({ page }) => {
  await page.goto('/')
  await dismissWelcome(page)
})

test('import : ouverture du modal', async ({ page }) => {
  await page.locator('.import-icon-btn').click()
  await expect(page.locator('.modal-window')).toBeVisible()
  await expect(page.locator('.modal-window h3')).toHaveText('Importer une image')
})

test('import : Échap ferme le modal', async ({ page }) => {
  await page.locator('.import-icon-btn').click()
  await expect(page.locator('.modal-window')).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(page.locator('.modal-window')).not.toBeVisible()
})

test('import : clic Annuler ferme le modal', async ({ page }) => {
  await page.locator('.import-icon-btn').click()
  await page.getByRole('button', { name: 'Annuler' }).click()
  await expect(page.locator('.modal-window')).not.toBeVisible()
})

test('import texte : matrice valide charge la grille', async ({ page }) => {
  await page.locator('.import-icon-btn').click()
  await page.locator('.matrix-textarea').fill(VALID_MATRIX)

  // Bouton Valider doit être actif
  await expect(page.getByRole('button', { name: 'Valider' })).toBeEnabled()
  await page.getByRole('button', { name: 'Valider' }).click()

  // Modal fermé, grille chargée en 4×4
  await expect(page.locator('.modal-window')).not.toBeVisible()
  expect(await page.locator('.cell').count()).toBe(16)
})

test('import texte : matrice valide active le bouton Résoudre', async ({ page }) => {
  await page.locator('.import-icon-btn').click()
  await page.locator('.matrix-textarea').fill(VALID_MATRIX)
  await page.getByRole('button', { name: 'Valider' }).click()

  await expect(page.locator('.solve-icon-btn')).toBeEnabled()
})

test('import texte : matrice non carrée affiche une erreur', async ({ page }) => {
  await page.locator('.import-icon-btn').click()
  await page.locator('.matrix-textarea').fill(INVALID_MATRIX_NON_SQUARE)

  await expect(page.locator('.modal-error')).toBeVisible()
  await expect(page.locator('.modal-error')).toContainText('carrée')
  await expect(page.getByRole('button', { name: 'Valider' })).toBeDisabled()
})

test('import texte : matrice trop petite affiche une erreur', async ({ page }) => {
  await page.locator('.import-icon-btn').click()
  await page.locator('.matrix-textarea').fill(INVALID_MATRIX_TOO_SMALL)

  await expect(page.locator('.modal-error')).toBeVisible()
  await expect(page.locator('.modal-error')).toContainText('4×4')
})

test('import texte : matrice vide → bouton Valider désactivé sans erreur', async ({ page }) => {
  await page.locator('.import-icon-btn').click()
  await page.locator('.matrix-textarea').fill('')

  await expect(page.getByRole('button', { name: 'Valider' })).toBeDisabled()
  await expect(page.locator('.modal-error')).not.toBeVisible()
})
