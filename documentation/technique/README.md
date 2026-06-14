# Documentation Technique

Explication du fonctionnement interne de chaque service.

---

## Services

### [TRM — Solveur Optimisé](./trm/README.md)
FastAPI, port 8000. Solveur N-Reines par backtracking avec bitsets et forward-checking.

| Fichier | Description |
|---|---|
| [solver.md](./trm/solver.md) | Algorithme QueensSolver — bitsets, forward-checking, backtracking |
| [routes.md](./trm/routes.md) | Routes API : `/api/solve`, `/api/extract-matrix`, `/api/health` |
| [models.md](./trm/models.md) | Modèles Pydantic : GridInput, Solution, PerformanceMetrics, ExtractedMatrix |
| [logger.md](./trm/logger.md) | Configuration du logger |

---

### [Baseline — Solveur Naïf](./baseline/README.md)
FastAPI, port 8001. Backtracking exhaustif sans optimisation — sert de référence pour les benchmarks.

| Fichier | Description |
|---|---|
| [greedy_model.md](./baseline/greedy_model.md) | Classe QueensGreedyBaseline — backtracking naïf |
| [routes.md](./baseline/routes.md) | Routes API : `/api/solve`, `/api/health` |

---

### [Frontend — Interface Vue 3](./frontend/README.md)
Vue 3 + Vite, port 5173 (dev) / port 8080 via Nginx (prod).

| Fichier | Description |
|---|---|
| [App.md](./frontend/App.md) | Composant racine — état global, peinture, brouillons, résolution |
| [BenchmarkChart.md](./frontend/BenchmarkChart.md) | Graphique SVG des performances |
| [utils.md](./frontend/utils.md) | Fonctions utilitaires : `formatMs`, `parseMatrixTextInput` |

---

[← Retour au sommaire général](../README.md)
