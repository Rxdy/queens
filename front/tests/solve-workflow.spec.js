import { test, expect } from '@playwright/test'
import { dismissWelcome, paint4x4 } from './helpers.js'

test.beforeEach(async ({ page }) => {
  await page.goto('/')
  await dismissWelcome(page)
})

test('résolution : grille 4×4 → solutions trouvées', async ({ page }) => {
  await paint4x4(page)
  await page.locator('.solve-icon-btn').click()

  await expect(page.locator('.solutions-info')).toBeVisible({ timeout: 15_000 })
  await expect(page.locator('.solutions-info strong')).toHaveText('2')
})

test('résolution : reine(s) affichée(s) sur la grille', async ({ page }) => {
  await paint4x4(page)
  await page.locator('.solve-icon-btn').click()

  await expect(page.locator('.queen-icon').first()).toBeVisible({ timeout: 15_000 })
  expect(await page.locator('.queen-icon').count()).toBe(4)
})

test('résolution : panneau de comparaison TRM / Baseline visible', async ({ page }) => {
  await paint4x4(page)
  await page.locator('.solve-icon-btn').click()

  await expect(page.locator('.comparison-panel')).toBeVisible({ timeout: 15_000 })
  await expect(page.locator('.trm-label')).toBeVisible()
  await expect(page.locator('.baseline-label')).toBeVisible()
})

test('navigation : boutons Solution 1 / Solution 2 permettent de changer de solution', async ({ page }) => {
  await paint4x4(page)
  await page.locator('.solve-icon-btn').click()
  await expect(page.locator('.solution-btn').nth(1)).toBeVisible({ timeout: 15_000 })

  // La solution 1 est active par défaut
  await expect(page.locator('.solution-btn').nth(0)).toHaveClass(/active/)

  // Clic sur solution 2
  await page.locator('.solution-btn').nth(1).click()
  await expect(page.locator('.solution-btn').nth(1)).toHaveClass(/active/)
  await expect(page.locator('.solution-btn').nth(0)).not.toHaveClass(/active/)
})

test('navigation : flèche droite → solution suivante', async ({ page }) => {
  await paint4x4(page)
  await page.locator('.solve-icon-btn').click()
  await expect(page.locator('.solution-btn').first()).toBeVisible({ timeout: 15_000 })

  await page.keyboard.press('ArrowRight')
  await expect(page.locator('.solution-btn').nth(1)).toHaveClass(/active/)
})

test('navigation : flèche gauche revient à la solution précédente', async ({ page }) => {
  await paint4x4(page)
  await page.locator('.solve-icon-btn').click()
  await expect(page.locator('.solution-btn').first()).toBeVisible({ timeout: 15_000 })

  await page.keyboard.press('ArrowRight')
  await page.keyboard.press('ArrowLeft')
  await expect(page.locator('.solution-btn').nth(0)).toHaveClass(/active/)
})

test('raccourci Entrée : lance la résolution quand la grille est complète', async ({ page }) => {
  await paint4x4(page)
  await page.keyboard.press('Enter')

  await expect(page.locator('.solutions-info')).toBeVisible({ timeout: 15_000 })
})

test('raccourci Espace : lance la résolution quand la grille est complète', async ({ page }) => {
  await paint4x4(page)
  await page.keyboard.press(' ')

  await expect(page.locator('.solutions-info')).toBeVisible({ timeout: 15_000 })
})

test('remplissage aléatoire : génère une grille complète et résolvable', async ({ page }) => {
  await page.locator('.size-selector select').selectOption('4')
  await page.locator('.random-icon-btn').click()

  await expect(page.locator('.solve-icon-btn')).toBeEnabled()
  await page.locator('.solve-icon-btn').click()
  await expect(page.locator('.solutions-info')).toBeVisible({ timeout: 15_000 })
})
