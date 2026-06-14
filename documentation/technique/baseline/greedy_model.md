# QueensGreedyBaseline — Algorithme

`baseline-8queens/src/greedy_model.py`

---

## Vue d'ensemble

Solveur de référence intentionnellement **non-optimisé**. Son rôle est de fournir un point de comparaison pour mesurer le gain de performance du TRM.

Contrairement au TRM :
- Pas de bitsets — utilise des listes et sets Python natifs
- Pas de forward-checking — teste chaque colonne séquentiellement
- La contrainte d'adjacence est vérifiée par une boucle O(n) sur les lignes précédentes

---

## Classe QueensGreedyBaseline

```python
class QueensGreedyBaseline:
    def solve_exhaustive(self, n, zones, max_iterations=10**18) -> tuple
```

### `solve_exhaustive(n, zones, max_iterations)`

Backtracking exhaustif qui compte **toutes** les solutions mais ne garde en mémoire que **la première**.

| Paramètre | Type | Description |
|---|---|---|
| `n` | `int` | Taille de la grille |
| `zones` | `list[list[int]]` | Matrice N×N de zones |
| `max_iterations` | `int` | Limite de récursions (non exposée dans l'API) |

**Retourne :** `(first_solution, solution_count)`

| Valeur | Type | Description |
|---|---|---|
| `first_solution` | `List[List[int]]` | Première solution `[[row, col], ...]`, ou `[]` si aucune |
| `solution_count` | `int` | Nombre total de solutions trouvées |

---

## Algorithme interne — `backtrack(row)`

Pour chaque colonne `col` de `0` à `n-1` :

1. **Colonne libre** — vérifie `used_cols[col]`
2. **Zone libre** — vérifie `zone not in used_zones`
3. **Adjacence** — boucle sur toutes les lignes précédentes :
   ```python
   if max(abs(placement[prev_row] - col), abs(prev_row - row)) <= 1:
       valid = False
   ```
4. Si tout est OK → place la reine, récurse, retire la reine

---

## Différences avec le TRM

| Critère | Baseline | TRM |
|---|---|---|
| Représentation des domaines | `list` + `set` | Bitsets (entiers) |
| Forward-checking | Non | Oui, multi-lignes |
| Contrainte adjacence | O(n) par nœud | O(1) via `adj_mask` |
| Performance typique (8×8) | Secondes | Millisecondes |

---

[← Sommaire Baseline](./README.md) | [Routes →](./routes.md)
