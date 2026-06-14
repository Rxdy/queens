# BenchmarkChart.vue — Graphique de Performance

`front/src/BenchmarkChart.vue`

---

## Responsabilité

Affiche un graphique SVG comparatif TRM vs Baseline basé sur l'historique de résolutions de la session courante. Chaque barre représente la **moyenne** des temps de résolution pour une taille de grille.

---

## Props

| Prop | Type | Défaut | Description |
|---|---|---|---|
| `history` | `Array` | `[]` | Tableau d'entrées `{ size, trmTime, baselineTime }`. `trmTime` et `baselineTime` sont en **secondes**. |

---

## Computed properties

### `chartData`

Agrège l'historique par taille de grille :
```js
{
  size: 8,
  trm: 0.001,        // moyenne en ms
  baseline: 45.2,    // moyenne en ms
  trmCount: 3,       // nombre de mesures
  baselineCount: 3,
  speedup: "45200.00"  // baseline/trm
}
```

Les entrées sont **triées par taille croissante**.

### Échelle logarithmique

L'axe Y utilise une échelle logarithmique (`log10`) pour permettre l'affichage simultané de valeurs allant de la microseconde à la seconde.

| Computed | Description |
|---|---|
| `yMin` | Min des valeurs, avec plancher `LOG_FLOOR = 0.001` ms |
| `yMax` | Max des valeurs × 2.5 |
| `yTicks` | Puissances de 10 dans la plage visible |
| `yScale(v)` | Convertit une valeur ms en coordonnée SVG Y |

---

## Dimensions SVG

```js
const ML = 72, MR = 24, MT = 28, MB = 52  // marges
const W = 640, H = 340                      // viewBox
```

Le SVG est responsive via `viewBox` + `preserveAspectRatio="xMidYMid meet"`.

---

## Tooltip

L'état du tooltip est dans `ref({ visible, x, y, lines })`.

| Événement | Comportement |
|---|---|
| `mouseenter` sur barre | Affiche tooltip avec label, temps moyen, nombre de mesures, speedup |
| `mousemove` sur `.svg-container` | Met à jour la position du tooltip |
| `mouseleave` sur barre | Cache le tooltip |

Le tooltip est rendu en SVG inline (`<rect>` + `<text>`).

---

## Dépendances

- `formatMs` importée depuis `./utils/format.js`
- Aucune dépendance externe — SVG pur

---

[← App.md](./App.md) | [Utils →](./utils.md) | [Sommaire Frontend](./README.md)
