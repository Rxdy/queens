# Fonctions Utilitaires — Frontend

---

## format.js

`front/src/utils/format.js`

### `formatMs(ms)`

Formate une durée en millisecondes en chaîne lisible avec l'unité adaptée.

```js
import { formatMs } from './utils/format.js'
```

| Plage | Unité | Exemple |
|---|---|---|
| `null` / `undefined` | — | `"—"` |
| `ms < 0.001` | ns | `"500 ns"` |
| `0.001 ≤ ms < 1` | µs | `"250 µs"` |
| `1 ≤ ms < 1000` | ms | `"42 ms"` / `"42.5 ms"` |
| `ms ≥ 1000` | s | `"1.50 s"` / `"10 s"` |

**Comportement :** les zéros décimaux superflus sont retirés (ex: `"1.0"` → `"1"`, `"1.00"` → `"1"`). Un seul zéro intermédiaire reste (`"1.50"` reste `"1.50"`).

**Utilisé par :** `BenchmarkChart.vue` (axe Y + valeurs de barres + tooltip)

---

## parseMatrix.js

`front/src/utils/parseMatrix.js`

### `parseMatrixTextInput(text, maxColorId = 12)`

Parse un texte représentant une grille de zones et retourne une matrice normalisée. Lance une `Error` en cas d'entrée invalide.

```js
import { parseMatrixTextInput } from './utils/parseMatrix.js'
```

| Paramètre | Type | Description |
|---|---|---|
| `text` | `string` | Texte de la grille. Séparateurs : espaces, virgules ou points-virgules |
| `maxColorId` | `number` | Valeur max autorisée pour un identifiant de zone (défaut : 12) |

**Retourne :** matrice `number[][]` avec identifiants normalisés à partir de 0.

**Exemple :**
```js
parseMatrixTextInput(`5 5 6 6\n5 7 7 6\n8 7 7 6\n8 8 8 6`)
// → [[0,0,1,1],[0,2,2,1],[3,2,2,1],[3,3,3,1]]  (remappé 5→0, 6→1, 7→2, 8→3)
```

**Erreurs levées :**

| Condition | Message |
|---|---|
| Texte vide | `"La matrice est vide."` |
| Matrice non carrée | `"La matrice doit être carrée..."` |
| Taille < 4 | `"La matrice doit être d'au moins 4×4."` |
| Token non entier | `"Valeur invalide : 'X'..."` |
| Valeur < -1 | `"Les valeurs doivent être supérieures ou égales à -1..."` |
| Trop de zones | `"La matrice contient plus de zones distinctes que la taille de la grille."` |
| Zone ID trop grand | `"Les identifiants de zone doivent être inférieurs à N."` |

**Cellules vides :** la valeur `-1` est conservée telle quelle après normalisation.

**Utilisé par :** `App.vue` → `applyImportedMatrix()` (via `parseMatrixTextInput(text, colors.length)`)

### `MAX_COLORS`

Constante exportée : `12`. Correspond au nombre de couleurs disponibles dans la palette de l'interface.

---

[← BenchmarkChart.md](./BenchmarkChart.md) | [Sommaire Frontend](./README.md)
