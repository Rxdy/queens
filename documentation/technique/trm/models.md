# Modèles Pydantic — TRM

`TRM/api/models.py`

---

## GridInput

Modèle de la requête de résolution.

```python
class GridInput(BaseModel):
    size: int   # taille N de la grille
    zones: List[List[int]]  # matrice N×N d'identifiants de zones
```

| Champ | Validation | Description |
|---|---|---|
| `size` | `ge=1` | Entier ≥ 1 |
| `zones` | — | Matrice N×N. Les identifiants commencent à 0. |

---

## PerformanceMetrics

Métriques retournées après résolution.

```python
class PerformanceMetrics(BaseModel):
    execution_time: float       # en secondes
    iterations: int             # nœuds explorés
    solutions_count: int        # solutions trouvées
    solutions_per_second: float # débit
```

---

## Solution

Réponse complète de `POST /api/solve`.

```python
class Solution(BaseModel):
    solutions: List[List[List[int]]]  # liste de solutions [[row,col], ...]
    performance: PerformanceMetrics
```

**Format d'une solution :**
```json
[[0, 1], [1, 3], [2, 0], [3, 2]]
```
Chaque élément `[row, col]` est la position de la reine dans la ligne `row`.

---

## ExtractedMatrix

Réponse de `POST /api/extract-matrix`.

```python
class ExtractedMatrix(BaseModel):
    size: int               # taille détectée
    zones: List[List[int]]  # matrice extraite
    confidence: float       # score 0–1
```

`confidence` reflète la qualité de la détection par l'algorithme d'extraction d'image.

---

[← routes.md](./routes.md) | [Logger →](./logger.md) | [Sommaire TRM](./README.md)
