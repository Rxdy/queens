import { test, expect } from '@playwright/test';

test('benchmark toutes tailles puis affiche les stats', async ({ page }) => {
  await page.goto('http://localhost:5173/');

  // Fermer le modal de bienvenue
  await page.getByRole('button', { name: /compris/i }).click();

  // Lancer le benchmark (toutes tailles 4→12)
  await page.click('.benchmark-icon-btn');

  // Attendre que le benchmark se termine
  await expect(page.locator('.benchmark-icon-btn')).not.toBeDisabled({ timeout: 60_000 });

  // Aller sur l'onglet Statistiques
  await page.getByRole('button', { name: /statistiques/i }).click();

  // Vérifier que le graphique SVG est présent et que des barres ont été générées
  await expect(page.locator('svg').first()).toBeVisible({ timeout: 5_000 });
  await expect(page.locator('rect.bar, rect.trm-bar').first()).toBeVisible({ timeout: 5_000 });
});
