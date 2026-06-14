/**
 * Helpers partagés entre les tests E2E Playwright.
 */

/** Ferme le modal de bienvenue s'il est présent. */
export async function dismissWelcome(page) {
  const btn = page.getByRole('button', { name: /compris/i })
  if (await btn.isVisible()) {
    await btn.click()
  }
}

/**
 * Sélectionne une couleur dans la palette (index 0-based).
 * La couleur doit être disponible.
 */
export async function pickColor(page, index) {
  await page.locator('.color-btn').nth(index).click()
}

/**
 * Peint une cellule par mousedown.
 * button : 0 = gauche (peindre), 2 = droit (effacer)
 */
export async function paintCell(page, row, col, button = 0) {
  const cell = page.locator(`.cell[data-row="${row}"][data-col="${col}"]`)
  await cell.dispatchEvent('mousedown', { button })
  await cell.dispatchEvent('mouseup')
}

/**
 * Peint une grille 4×4 minimale avec 4 zones (quadrants 2×2).
 * Résultat : grille valide, résolvable, 2 solutions.
 */
export async function paint4x4(page) {
  // Sélecteur de taille → 4
  await page.locator('.size-selector select').selectOption('4')

  const zones = [
    [0, 0, 1, 1],
    [0, 0, 1, 1],
    [2, 2, 3, 3],
    [2, 2, 3, 3],
  ]
  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 4; c++) {
      await pickColor(page, zones[r][c])
      await paintCell(page, r, c)
    }
  }
}
