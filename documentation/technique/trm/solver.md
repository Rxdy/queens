# QueensSolver — Algorithme

`TRM/core/solver.py`

---

## Vue d'ensemble

`QueensSolver` résout le problème des N-Reines avec contraintes de zones par **backtracking récursif** accéléré par trois optimisations :

1. **Bitsets** — les ensembles de colonnes et zones libres sont représentés comme des entiers Python (opérations bit-à-bit O(1))
2. **Pré-calcul des masques de zones** — pour chaque ligne et chaque zone, le masque de colonnes disponibles est calculé une seule fois avant le backtracking
3. **Forward-checking multi-lignes** — après chaque placement, on vérifie que toutes les lignes restantes ont un domaine non-vide **et** que chaque zone libre reste atteignable

---

## Classe QueensSolver

```python
class QueensSolver:
    def __init__(self, max_iterations: int = 10**18)
    def solve(self, size: int, zones: List[List[int]]) -> Tuple[List[List[List[int]]], int]
```

### `__init__(max_iterations)`

| Paramètre | Type | Défaut | Description |
|---|---|---|---|
| `max_iterations` | `int` | `10**18` | Limite de nœuds explorés avant arrêt forcé. Évite les boucles infinies sur des grilles pathologiques. |

---

### `solve(size, zones)`

Point d'entrée principal. **Thread-safe** : toutes les variables locales sont propres à chaque appel.

| Paramètre | Type | Description |
|---|---|---|
| `size` | `int` | Taille de la grille (N) |
| `zones` | `List[List[int]]` | Matrice N×N d'identifiants de zones (0-based) |

**Retourne :** `(solutions, iterations)`

| Valeur | Type | Description |
|---|---|---|
| `solutions` | `List[List[List[int]]]` | Liste de solutions. Chaque solution = liste de `[row, col]` (une reine par ligne) |
| `iterations` | `int` | Nombre de nœuds explorés dans l'arbre de backtracking |

---

## Fonctions internes

### `domain(r, free_cols, free_zones, prev_col)`

Calcule le domaine valide (bitset de colonnes) pour la ligne `r` en tenant compte de :
- Les colonnes déjà occupées (`free_cols`)
- Les zones déjà occupées (`free_zones`)
- La contrainte d'adjacence avec la reine de la ligne précédente (`prev_col`)

### `backtrack(row, free_cols, free_zones)`

Récursion principale. Pour chaque colonne du domaine de `row` :
1. Calcule la nouvelle zone occupée
2. Lance le forward-checking sur toutes les lignes restantes
3. Vérifie l'atteignabilité de chaque zone libre
4. Si tout est OK, place la reine et récurse

---

## Complexité

| Aspect | Complexité |
|---|---|
| Opérations bitset | O(1) |
| Forward-checking par nœud | O(n²) dans le pire cas |
| Espace mémoire | O(n) pour `placement`, solutions mises en cache |

---

## Thread-safety

Le compteur `iterations` et le tableau `placement` sont des **variables locales** à chaque appel de `solve()`. Plusieurs appels simultanés (ex: pool de threads asyncio) ne partagent aucun état.

---

[← Sommaire TRM](./README.md) | [Routes →](./routes.md)
