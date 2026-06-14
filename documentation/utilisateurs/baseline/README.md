# API Baseline — Endpoints

Solveur naïf exhaustif. Utilisé pour les benchmarks comparatifs avec le TRM.

**Base URL (dev) :** `http://localhost:8001`
**Base URL (prod) :** `https://ton-domaine.com/baseline`

---

## POST /api/solve

Résout la grille par backtracking exhaustif. Trouve **toutes** les solutions et retourne la première.

### Corps de la requête

Identique à l'API TRM :

```json
{
  "size": 4,
  "zones": [
    [0, 0, 1, 1],
    [0, 2, 2, 1],
    [3, 2, 2, 1],
    [3, 3, 3, 1]
  ]
}
```

### Réponse 200 — Succès

```json
{
  "supported": true,
  "solution": [[0, 1], [1, 3], [2, 0], [3, 2]],
  "solutions": [
    [[0, 1], [1, 3], [2, 0], [3, 2]]
  ],
  "performance": {
    "execution_time": 0.045,
    "valid": true,
    "conflicts": 0,
    "solutions_count": 1
  }
}
```

| Champ | Type | Description |
|---|---|---|
| `supported` | `boolean` | Toujours `true` si la résolution a pu être tentée |
| `solution` | `[row, col][]` | Première solution trouvée (ou `null` si aucune) |
| `solutions` | `[row, col][][]` | Tableau contenant la première solution |
| `performance.execution_time` | `float` | Durée en secondes |
| `performance.valid` | `boolean` | `true` si au moins une solution existe |
| `performance.conflicts` | `integer` | Toujours `0` (backtracking ne retourne que des solutions valides) |
| `performance.solutions_count` | `integer` | Nombre total de solutions trouvées |

### Réponse 200 — Erreur interne

```json
{
  "supported": false,
  "error": "Erreur lors de la résolution: ..."
}
```

> Le Baseline retourne toujours HTTP 200. Les erreurs sont encodées dans le champ `supported: false`.

### Exemple cURL

```bash
curl -X POST http://localhost:8001/api/solve \
  -H "Content-Type: application/json" \
  -d '{"size": 4, "zones": [[0,0,1,1],[0,2,2,1],[3,2,2,1],[3,3,3,1]]}'
```

---

## GET /api/health

```bash
curl http://localhost:8001/api/health
```

### Réponse 200

```json
{
  "status": "healthy",
  "service": "Baseline Queens Solver (Greedy)"
}
```

---

[← API TRM](../trm/README.md) | [Interface →](../frontend/README.md) | [Sommaire général](../../README.md)
