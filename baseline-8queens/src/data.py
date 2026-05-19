import argparse
import os
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


@dataclass
class DatasetSplit:
    x: np.ndarray  # (N, 8) values in {-1..7}  (-1 = unknown)
    y: np.ndarray  # (N, 8) values in {0..7}   (full solution)
    fixed_mask: np.ndarray  # (N, 8) bool, True where x is fixed (not -1)
    k_fixed: np.ndarray  # (N,) int, number of fixed rows in x


def solve_all_nqueens(n: int = 8) -> List[np.ndarray]:
    """
    Returns all solutions to the N-Queens problem with 1 queen per row.
    Each solution is an array of length n where sol[r] = column index for row r.
    """
    solutions: List[np.ndarray] = []

    cols_used = [False] * n
    diag1_used = [False] * (2 * n - 1)  # r + c
    diag2_used = [False] * (2 * n - 1)  # r - c + (n - 1)
    sol = [-1] * n

    def backtrack(r: int):
        if r == n:
            solutions.append(np.array(sol, dtype=np.int8))
            return
        for c in range(n):
            d1 = r + c
            d2 = r - c + (n - 1)
            if cols_used[c] or diag1_used[d1] or diag2_used[d2]:
                continue
            sol[r] = c
            cols_used[c] = True
            diag1_used[d1] = True
            diag2_used[d2] = True

            backtrack(r + 1)

            cols_used[c] = False
            diag1_used[d1] = False
            diag2_used[d2] = False
            sol[r] = -1

    backtrack(0)
    return solutions


def make_partial_from_solution(
    full_solution: np.ndarray, kmin: int, kmax: int, rng: np.random.Generator
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """
    Create a partial input x from a full solution y.
    - Choose k rows to keep (k in [kmin, kmax])
    - Set other rows to -1
    Returns: x, y, fixed_mask, k
    """
    n = full_solution.shape[0]
    k = int(rng.integers(kmin, kmax + 1))
    rows = np.arange(n)
    fixed_rows = rng.choice(rows, size=k, replace=False)

    x = np.full((n,), -1, dtype=np.int8)
    x[fixed_rows] = full_solution[fixed_rows]

    fixed_mask = x != -1
    y = full_solution.astype(np.int8, copy=True)
    return x, y, fixed_mask, k


def build_split(
    solutions: List[np.ndarray],
    count: int,
    kmin: int,
    kmax: int,
    seed: int,
    desc: str = "split",
) -> DatasetSplit:
    """
    Build one dataset split by sampling full solutions and masking them into partial inputs.
    """
    rng = np.random.default_rng(seed)
    n = solutions[0].shape[0]

    x_all = np.empty((count, n), dtype=np.int8)
    y_all = np.empty((count, n), dtype=np.int8)
    fixed_mask_all = np.empty((count, n), dtype=bool)
    k_fixed_all = np.empty((count,), dtype=np.int16)

    indices = rng.integers(0, len(solutions), size=count)

    iterator = range(count)
    if tqdm is not None:
        iterator = tqdm(iterator, total=count, desc=f"Generating {desc}")

    for i in iterator:
        sol = solutions[int(indices[i])]
        x, y, fixed_mask, k = make_partial_from_solution(sol, kmin, kmax, rng)
        x_all[i] = x
        y_all[i] = y
        fixed_mask_all[i] = fixed_mask
        k_fixed_all[i] = k

    return DatasetSplit(
        x=x_all, y=y_all, fixed_mask=fixed_mask_all, k_fixed=k_fixed_all
    )


def parse_args():
    p = argparse.ArgumentParser(
        description="Generate 8-Queens partial->full dataset (.npz)."
    )
    p.add_argument(
        "--out",
        type=str,
        default="outputs/dataset.npz",
        help="Output .npz path (default: outputs/dataset.npz)",
    )
    p.add_argument(
        "--train", type=int, default=20000, help="Number of training samples"
    )
    p.add_argument("--val", type=int, default=2000, help="Number of validation samples")
    p.add_argument("--test", type=int, default=2000, help="Number of test samples")
    p.add_argument(
        "--kmin", type=int, default=2, help="Min fixed rows in partial input"
    )
    p.add_argument(
        "--kmax", type=int, default=6, help="Max fixed rows in partial input"
    )
    p.add_argument("--seed", type=int, default=42, help="Random seed")
    p.add_argument("--n", type=int, default=8, help="Board size N (default 8)")
    return p.parse_args()


def main():
    args = parse_args()

    if args.kmin < 0 or args.kmax > args.n or args.kmin > args.kmax:
        raise ValueError(
            f"Invalid k range: kmin={args.kmin}, kmax={args.kmax}, n={args.n}"
        )

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    solutions = solve_all_nqueens(args.n)
    if len(solutions) == 0:
        raise RuntimeError(f"No solutions found for n={args.n}")

    print(f"Found {len(solutions)} solutions for {args.n}-Queens.")

    # Use different seeds per split for reproducibility but separation
    train_split = build_split(
        solutions, args.train, args.kmin, args.kmax, seed=args.seed + 0, desc="train"
    )
    val_split = build_split(
        solutions, args.val, args.kmin, args.kmax, seed=args.seed + 1, desc="val"
    )
    test_split = build_split(
        solutions, args.test, args.kmin, args.kmax, seed=args.seed + 2, desc="test"
    )

    np.savez_compressed(
        args.out,
        n=np.int16(args.n),
        kmin=np.int16(args.kmin),
        kmax=np.int16(args.kmax),
        seed=np.int32(args.seed),
        solutions_count=np.int16(len(solutions)),
        x_train=train_split.x,
        y_train=train_split.y,
        fixed_mask_train=train_split.fixed_mask,
        k_fixed_train=train_split.k_fixed,
        x_val=val_split.x,
        y_val=val_split.y,
        fixed_mask_val=val_split.fixed_mask,
        k_fixed_val=val_split.k_fixed,
        x_test=test_split.x,
        y_test=test_split.y,
        fixed_mask_test=test_split.fixed_mask,
        k_fixed_test=test_split.k_fixed,
    )

    print(f"Saved dataset to: {args.out}")
    print("Shapes:")
    print(f"  x_train: {train_split.x.shape}, y_train: {train_split.y.shape}")
    print(f"  x_val:   {val_split.x.shape}, y_val:   {val_split.y.shape}")
    print(f"  x_test:  {test_split.x.shape}, y_test:  {test_split.y.shape}")


if __name__ == "__main__":
    main()
