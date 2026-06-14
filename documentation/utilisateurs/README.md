# Documentation Utilisateur

Comment utiliser les API et l'interface du Queens Game Solveur.

---

## API REST

### [API TRM](./trm/README.md)
Solveur optimisé — port 8000 en local, `/api/` en production.

| Endpoint | Description |
|---|---|
| `POST /api/solve` | Résoudre une grille |
| `POST /api/extract-matrix` | Extraire une grille depuis une image |
| `GET /api/health` | Vérifier l'état du service |

### [API Baseline](./baseline/README.md)
Solveur naïf — port 8001 en local, `/baseline/api/` en production.

| Endpoint | Description |
|---|---|
| `POST /api/solve` | Résoudre une grille (backtracking exhaustif) |
| `GET /api/health` | Vérifier l'état du service |

---

## Interface

### [Frontend](./frontend/README.md)

| Page / Fonctionnalité | Description |
|---|---|
| [Grille](./frontend/grille.md) | Peindre les zones, naviguer dans les solutions |
| [Brouillons](./frontend/brouillons.md) | Sauvegarder et switcher entre plusieurs grilles |
| [Import](./frontend/import.md) | Importer une grille par texte ou image |
| [Benchmark & Stats](./frontend/benchmark.md) | Comparer TRM vs Baseline, graphique de performance |
| [Raccourcis clavier](./frontend/raccourcis.md) | Tous les raccourcis disponibles |

---

[← Retour au sommaire général](../README.md)
