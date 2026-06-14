import { test, expect } from '@playwright/test'
import { dismissWelcome, paint4x4, paintCell, pickColor } from './helpers.js'

test.beforeEach(async ({ page }) => {
  // Vider le localStorage pour isoler les tests
  await page.goto('/')
  await page.evaluate(() => localStorage.clear())
  await page.reload()
  await dismissWelcome(page)
})

test('brouillons : un brouillon initial est créé au démarrage', async ({ page }) => {
  await expect(page.locator('.draft-tab')).toHaveCount(1)
})

test('brouillons : le bouton Nouvelle grille crée un brouillon supplémentaire', async ({ page }) => {
  await page.locator('.new-icon-btn').click()
  await expect(page.locator('.draft-tab')).toHaveCount(2)
})

test('brouillons : le nouveau brouillon devient actif', async ({ page }) => {
  await page.locator('.new-icon-btn').click()
  // Le premier onglet (index 0) doit être actif (createNewDraft() insère en tête)
  await expect(page.locator('.draft-tab').first()).toHaveClass(/active/)
})

test('brouillons : changer de brouillon charge l\'autre configuration', async ({ page }) => {
  // Peindre le brouillon 1
  await page.locator('.size-selector select').selectOption('4')
  await pickColor(page, 0)
  await paintCell(page, 0, 0)

  // Créer un second brouillon (vide)
  await page.locator('.new-icon-btn').click()

  // Cellule (0,0) du nouveau brouillon doit être blanche
  const cell = page.locator('.cell[data-row="0"][data-col="0"]')
  const bg = await cell.evaluate(el => getComputedStyle(el).backgroundColor)
  expect(bg).toBe('rgb(255, 255, 255)')

  // Revenir au brouillon 1 (index 1 dans la liste après insertion en tête)
  await page.locator('.draft-tab').nth(1).click()

  // La cellule (0,0) doit être peinte
  const bgBack = await cell.evaluate(el => getComputedStyle(el).backgroundColor)
  expect(bgBack).not.toBe('rgb(255, 255, 255)')
})

test('brouillons : supprimer un brouillon le retire de la liste', async ({ page }) => {
  await page.locator('.new-icon-btn').click()
  await expect(page.locator('.draft-tab')).toHaveCount(2)

  // Supprimer le premier brouillon
  await page.locator('.draft-tab').first().locator('.draft-delete-btn').click()
  await expect(page.locator('.draft-tab')).toHaveCount(1)
})

test('brouillons : persistance — les brouillons survivent au rechargement', async ({ page }) => {
  // Peindre une cellule pour différencier
  await page.locator('.size-selector select').selectOption('5')
  await pickColor(page, 0)
  await paintCell(page, 0, 0)

  // Créer un second brouillon
  await page.locator('.new-icon-btn').click()
  await expect(page.locator('.draft-tab')).toHaveCount(2)

  // Recharger la page
  await page.reload()
  await dismissWelcome(page)

  // Les deux brouillons doivent toujours être là
  await expect(page.locator('.draft-tab')).toHaveCount(2)
})

test('brouillons : la taille du brouillon est affichée dans l\'onglet', async ({ page }) => {
  await page.locator('.size-selector select').selectOption('6')
  // La sauvegarde auto se fait au changement de taille (initializeZones est appelé)
  await expect(page.locator('.draft-tab').first().locator('.draft-size')).toContainText('6×6')
})
