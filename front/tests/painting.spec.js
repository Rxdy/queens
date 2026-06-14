import { test, expect } from '@playwright/test'
import { dismissWelcome, pickColor, paintCell, paint4x4 } from './helpers.js'

test.beforeEach(async ({ page }) => {
  await page.goto('/')
  await dismissWelcome(page)
})

test('peinture : une cellule peinte change de couleur', async ({ page }) => {
  await page.locator('.size-selector select').selectOption('4')
  await pickColor(page, 0)
  await paintCell(page, 0, 0)

  // La cellule ne doit plus avoir un fond blanc
  const cell = page.locator('.cell[data-row="0"][data-col="0"]')
  const bg = await cell.evaluate(el => getComputedStyle(el).backgroundColor)
  expect(bg).not.toBe('rgb(255, 255, 255)')
})

test('peinture : clic droit efface une cellule', async ({ page }) => {
  await page.locator('.size-selector select').selectOption('4')
  await pickColor(page, 0)
  await paintCell(page, 0, 0)
  // Efface avec clic droit
  await paintCell(page, 0, 0, 2)

  const cell = page.locator('.cell[data-row="0"][data-col="0"]')
  const bg = await cell.evaluate(el => getComputedStyle(el).backgroundColor)
  expect(bg).toBe('rgb(255, 255, 255)')
})

test('peinture : Ctrl+Z annule la dernière peinture', async ({ page }) => {
  await page.locator('.size-selector select').selectOption('4')
  await pickColor(page, 0)
  await paintCell(page, 0, 0)

  const cell = page.locator('.cell[data-row="0"][data-col="0"]')
  const bgPainted = await cell.evaluate(el => getComputedStyle(el).backgroundColor)
  expect(bgPainted).not.toBe('rgb(255, 255, 255)')

  await page.keyboard.press('Control+z')

  const bgAfterUndo = await cell.evaluate(el => getComputedStyle(el).backgroundColor)
  expect(bgAfterUndo).toBe('rgb(255, 255, 255)')
})

test('peinture : nouvelle grille remet toutes les cellules à blanc', async ({ page }) => {
  await page.locator('.size-selector select').selectOption('4')
  await pickColor(page, 0)
  await paintCell(page, 0, 0)
  await paintCell(page, 1, 1)

  await page.locator('.new-icon-btn').click()

  const cells = page.locator('.cell')
  const count = await cells.count()
  for (let i = 0; i < count; i++) {
    const bg = await cells.nth(i).evaluate(el => getComputedStyle(el).backgroundColor)
    expect(bg).toBe('rgb(255, 255, 255)')
  }
})

test('peinture : le bouton Réinitialiser remet la grille courante à blanc', async ({ page }) => {
  await page.locator('.size-selector select').selectOption('4')
  await pickColor(page, 0)
  await paintCell(page, 0, 0)

  await page.locator('.reset-icon-btn').click()

  const cell = page.locator('.cell[data-row="0"][data-col="0"]')
  const bg = await cell.evaluate(el => getComputedStyle(el).backgroundColor)
  expect(bg).toBe('rgb(255, 255, 255)')
})

test('peinture : grille 4×4 complète active le bouton Résoudre', async ({ page }) => {
  await paint4x4(page)
  await expect(page.locator('.solve-icon-btn')).toBeEnabled()
})
