from __future__ import annotations

from typing import Iterable, Union
import numpy as np

ArrayLike = Union[np.ndarray, list, tuple]


def _ensure_2d(a: np.ndarray) -> np.ndarray:
    """Ensure array is 2D: (N, 8)."""
    a = np.asarray(a)
    if a.ndim == 1:
        a = a[None, :]
    return a


def count_conflicts(y: ArrayLike) -> Union[int, np.ndarray]:
    """
    Count the number of conflicts (column + diagonal) for 8-queens representation:
    y[r] = column index of queen in row r.

    Supports:
    - y shape (8,) -> returns int conflicts
    - y shape (N,8) -> returns np.ndarray shape (N,) conflicts

    Notes:
    - If y contains -1 (unknown rows), those rows are ignored in conflict counting.
    - Conflicts are counted as number of attacking *pairs*.
      Example: if 3 queens share the same column, that's C(3,2)=3 conflicts.
    """
    y2 = _ensure_2d(np.asarray(y, dtype=int))
    n, rows = y2.shape
    if rows != 8:
        raise ValueError(f"Expected y with 8 rows (shape (...,8)), got {y2.shape}")

    conflicts = np.zeros((n,), dtype=int)

    for i in range(n):
        yi = y2[i]
        # keep only placed queens (ignore -1)
        placed_rows = np.where(yi != -1)[0]
        cols = yi[placed_rows]

        # Column conflicts: count pairs of equal columns
        # Compute counts per column
        for c in range(8):
            k = int(np.sum(cols == c))
            if k > 1:
                conflicts[i] += k * (k - 1) // 2

        # Diagonal conflicts: pairs with abs(col_i - col_j) == abs(row_i - row_j)
        # Brute force is fine for 8 (max 28 pairs)
        for a in range(len(placed_rows)):
            ra = int(placed_rows[a])
            ca = int(yi[ra])
            for b in range(a + 1, len(placed_rows)):
                rb = int(placed_rows[b])
                cb = int(yi[rb])
                if abs(ca - cb) == abs(ra - rb):
                    conflicts[i] += 1

    # Return scalar int if input was 1D
    if np.asarray(y).ndim == 1:
        return int(conflicts[0])
    return conflicts


def is_valid_solution(y: ArrayLike) -> Union[bool, np.ndarray]:
    """
    Check if y is a complete valid 8-queens solution.
    Conditions:
    - length = 8
    - all values in [0..7]
    - no -1
    - no conflicts (columns + diagonals)

    Supports:
    - y shape (8,) -> returns bool
    - y shape (N,8) -> returns np.ndarray bool shape (N,)
    """
    y2 = _ensure_2d(np.asarray(y, dtype=int))
    if y2.shape[1] != 8:
        raise ValueError(f"Expected y with shape (...,8), got {y2.shape}")

    # completeness and range
    complete = np.all(y2 != -1, axis=1)
    in_range = np.all((y2 >= 0) & (y2 <= 7), axis=1)

    # no column duplicates (since 1 queen per row already assumed)
    # Only meaningful if complete
    no_dup_cols = np.array([len(set(row.tolist())) == 8 for row in y2], dtype=bool)

    # no attacking pairs
    conf = count_conflicts(y2)
    ok = complete & in_range & no_dup_cols & (conf == 0)

    if np.asarray(y).ndim == 1:
        return bool(ok[0])
    return ok


def solved_rate(preds: ArrayLike) -> float:
    """
    Compute solved rate = fraction of valid solutions in preds.
    preds: shape (N,8) (or list of solutions)
    """
    preds2 = _ensure_2d(np.asarray(preds, dtype=int))
    valid = is_valid_solution(preds2)
    return float(np.mean(valid))


if __name__ == "__main__":
    # Small sanity checks
    # Known 8-queens solution example: [0,4,7,5,2,6,1,3] (one of them)
    sol = np.array([0, 4, 7, 5, 2, 6, 1, 3], dtype=int)
    print("conflicts(sol) =", count_conflicts(sol))
    print("is_valid(sol)  =", is_valid_solution(sol))

    bad = np.array([0, 0, 0, 0, 0, 0, 0, 0], dtype=int)
    print("conflicts(bad) =", count_conflicts(bad))
    print("is_valid(bad)  =", is_valid_solution(bad))
