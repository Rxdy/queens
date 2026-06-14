# App.vue — Composant Racine

`front/src/App.vue`

---

## Responsabilités

Composant unique qui gère l'intégralité de la logique de l'application :
- État de la grille (zones, taille, solutions)
- Peinture des zones (souris + tactile)
- Système undo/redo
- Brouillons (persistance localStorage)
- Appels API (TRM + Baseline)
- Navigation entre les vues (Jeu / Historique / Statistiques)
- Benchmark automatique
- Import de grilles (texte ou image)

---

## État réactif principal

| Variable | Type | Description |
|---|---|---|
| `size` | `ref(8)` | Taille courante de la grille |
| `zones` | `ref([])` | Matrice N×N de couleurs. `-1` = cellule vide |
| `solutions` | `ref([])` | Solutions retournées par le TRM |
| `currentSolutionIndex` | `ref(0)` | Index de la solution affichée |
| `selectedColor` | `ref(0)` | Couleur active pour la peinture |
| `paintHistory` | `ref([])` | Pile des états précédents (undo) |
| `drafts` | `useLocalStorage(...)` | Brouillons persistés |
| `currentDraftIndex` | `useLocalStorage(...)` | Index du brouillon actif |
| `trmPerformance` | `ref(null)` | Métriques TRM de la dernière résolution |
| `baselineResult` | `ref(null)` | Résultat Baseline de la dernière résolution |
| `history` | `ref([])` | Historique de session pour le graphique |

---

## Computed properties clés

| Computed | Description |
|---|---|
| `isGridComplete` | `true` si toutes les cellules sont peintes (aucune à `-1`) |
| `emptyCellsCount` | Nombre de cellules encore à `-1` |
| `hasGridData` | `true` si au moins une cellule est peinte |
| `isViewingHistory` | `true` si on visualise un résultat de l'historique |
| `isMobile` | `true` si `screenWidth < 600` |
| `speedup` | Ratio `baselineTime / trmTime` |
| `availableColorIndices` | Couleurs disponibles selon le nombre de zones remplies |
| `importMatrixParseResult` | Parse live le texte import pour preview et validation |

---

## Fonctions principales

### Peinture

| Fonction | Description |
|---|---|
| `initializeZones()` | Crée une grille N×N de `-1`, remet à zéro toutes les données |
| `clickCell(row, col, button)` | Peint (`button=0`) ou efface (`button=2`) une cellule |
| `snapshotPaintState()` | Pousse l'état courant dans `paintHistory` (MAX_UNDO = 20) |
| `undoPaint()` | Restaure le dernier état depuis `paintHistory` |
| `onMouseDown / onMouseEnter / onMouseUp` | Gestion du dessin à la souris |
| `onTouchStart / onTouchMove / onTouchEnd` | Gestion du dessin au toucher |
| `getCellStyle(row, col)` | Calcule le style CSS d'une cellule (couleur + bordures épaisses entre zones) |

### Brouillons

| Fonction | Description |
|---|---|
| `saveDraft()` | Met à jour le brouillon courant dans `drafts` |
| `createNewDraft()` | Crée un nouveau brouillon vide et le sélectionne |
| `switchDraft(index)` | Sauvegarde le brouillon courant et charge celui à `index` |
| `deleteDraft(index)` | Supprime un brouillon, sélectionne le suivant ou remet à zéro |

### Résolution

| Fonction | Description |
|---|---|
| `submit()` | Lance TRM et Baseline en parallèle, met à jour l'historique |
| `loadSolution(index)` | Affiche la solution à l'index donné |
| `runBenchmark()` | Itère sur toutes les tailles (4→12), résout chacune, remplit l'historique |

### Import

| Fonction | Description |
|---|---|
| `applyImportedMatrix()` | Valide et applique le texte importé ou la matrice extraite de l'image |
| `uploadImportImage()` | Envoie l'image à `POST /api/extract-matrix` |
| `parseMatrixTextInput(text)` | (importé depuis `utils/parseMatrix.js`) Parse et normalise le texte |

---

## Cycle de vie

```
setup → initializeZones() → initializeHistoryVisibility()
      → createNewDraft() si aucun brouillon

onMounted → updateScreenSize(), addEventListener keydown/mouseup/resize
onUnmounted → removeEventListener
watch(zones) → saveDraft() si brouillon actif
watch(isMobile) → masquer/afficher l'historique
```

---

## Variables d'environnement

```js
const TRM_BASE      = import.meta.env.VITE_TRM_API_BASE ?? ""
const BASELINE_BASE = import.meta.env.VITE_BASELINE_API_BASE ?? ""
```

En production, `TRM_BASE = ""` (même domaine) et `BASELINE_BASE = "/baseline"`.

---

[← Sommaire Frontend](./README.md) | [BenchmarkChart →](./BenchmarkChart.md)
