# API TRM — Endpoints

Solveur optimisé (bitsets + forward-checking). En production, tous les endpoints sont préfixés par `/api/`.

**Base URL (dev) :** `http://localhost:8000`
**Base URL (prod) :** `https://ton-domaine.com`

---

## POST /api/solve

Résout le problème des N-Reines avec contraintes de zones. Trouve **toutes** les solutions.

### Corps de la requête

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

| Champ | Type | Description |
|---|---|---|
| `size` | `integer` | Taille de la grille (N×N) |
| `zones` | `integer[][]` | Matrice N×N où chaque cellule contient l'identifiant de zone (0-based) |

### Réponse 200

```json
{
  "solutions": [
    [[0, 1], [1, 3], [2, 0], [3, 2]]
  ],
  "performance": {
    "execution_time": 0.0012,
    "iterations": 42,
    "solutions_count": 1,
    "solutions_per_second": 833.0
  }
}
```

| Champ | Type | Description |
|---|---|---|
| `solutions` | `[row, col][][]` | Liste de solutions. Chaque solution = liste de positions `[ligne, colonne]` |
| `performance.execution_time` | `float` | Durée en secondes |
| `performance.iterations` | `integer` | Nombre de nœuds explorés dans l'arbre de recherche |
| `performance.solutions_count` | `integer` | Nombre de solutions trouvées |
| `performance.solutions_per_second` | `float` | Débit de résolution |

### Erreurs

| Code | Cas |
|---|---|
| `400` | Nombre de lignes incorrect (`len(zones) != size`) |
| `400` | Nombre de colonnes incorrect dans une ligne |
| `500` | Erreur interne inattendue |

### Exemple cURL

```bash
curl -X POST http://localhost:8000/api/solve \
  -H "Content-Type: application/json" \
  -d '{"size": 4, "zones": [[0,0,1,1],[0,2,2,1],[3,2,2,1],[3,3,3,1]]}'
```

---

## POST /api/extract-matrix

Extrait automatiquement une grille de zones depuis une image (capture d'écran du jeu Queens).

### Corps de la requête

Multipart form-data avec un champ `file` contenant l'image.

```bash
curl -X POST http://localhost:8000/api/extract-matrix \
  -F "file=@screenshot.png"
```

Types acceptés : `image/png`, `image/jpeg`, `image/jpg`, `image/gif`

### Réponse 200

```json
{
  "size": 8,
  "zones": [[0, 0, 1, 1, 2, 2, 3, 3], ...],
  "confidence": 0.87
}
```

| Champ | Type | Description |
|---|---|---|
| `size` | `integer` | Taille détectée de la grille |
| `zones` | `integer[][]` | Matrice extraite |
| `confidence` | `float` | Score de confiance entre 0 et 1 |

### Erreurs

| Code | Cas |
|---|---|
| `400` | Type de fichier non supporté |
| `400` | Fichier image vide |
| `500` | Échec de l'extraction |

---

## GET /api/health

Vérifie que le service est opérationnel.

### Réponse 200

```json
{
  "status": "healthy",
  "service": "TRM Solver",
  "max_iterations": 1000000000000000000
}
```

---

[← Documentation Utilisateur](../README.md) | [API Baseline →](../baseline/README.md) | [Sommaire général](../../README.md)
