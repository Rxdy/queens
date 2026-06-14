# Frontend — Documentation Technique

Interface Vue 3 + Vite. Composant unique `App.vue` orchestrant toute la logique de jeu.

Vue 3 · Vite 7 · @vueuse/core · axios · Vitest

---

## Fichiers

| Fichier | Rôle |
|---|---|
| `src/App.vue` | Composant racine — état global, peinture, brouillons, résolution |
| `src/BenchmarkChart.vue` | Graphique SVG des performances de session |
| `src/utils/format.js` | Fonction `formatMs` — formatage des durées |
| `src/utils/parseMatrix.js` | Fonction `parseMatrixTextInput` — parsing de grille texte |
| `src/main.js` | Point d'entrée Vue |
| `vite.config.js` | Configuration Vite + Vitest |
| `nginx.conf` | Reverse proxy de production |

## Documentation

- [App.md](./App.md) — Composant App.vue
- [BenchmarkChart.md](./BenchmarkChart.md) — Graphique SVG
- [utils.md](./utils.md) — Fonctions utilitaires

---

[← Documentation Technique](../README.md) | [Sommaire général](../../README.md)
