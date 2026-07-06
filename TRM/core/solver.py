"""
TRM — Tiny Recursive Model
Solveur N-Reines avec backtracking récursif + bitsets + forward-checking.

Optimisations par rapport au baseline naïf :
  1. Bitsets (entiers Python) : toutes les opérations de domaine sont O(1) via
     opérations bit-à-bit natives en C (AND, OR, NOT, bit_length).
  2. Pré-calcul des masques de zones par ligne : row_zone_mask[r][z] = bitset
     des colonnes de la zone z dans la ligne r. Union rapide lors du backtrack.
  3. Forward-checking multi-lignes + atteignabilité des zones via bitsets :
     après chaque placement, O(n) opérations bitset pour vérifier toutes les
     lignes restantes — au lieu de O(n²) boucles imbriquées dans le baseline.
  4. Masque d'adjacence calculé en O(1) par nœud.
"""

import logging

logger = logging.getLogger("trm_solver")


class QueensSolver:
    """
    Solveur N-Reines par backtracking avec bitsets + forward-checking.
    """

    def __init__(self, max_iterations: int = 10**18):
        self.max_iterations = max_iterations

    def solve(self, size: int, zones: list[list[int]]) -> tuple[list[list[list[int]]], int]:
        """
        Résout le problème des Queens avec contraintes de zones.

        Returns:
            (solutions, iterations)
        """
        iterations = 0
        solutions = []
        n = size
        ALL = (1 << n) - 1

        # ── Pré-calcul des masques de zones ───────────────────────────────
        # row_zone_mask[r][z] = bitset des colonnes de zone z dans ligne r
        row_zone_mask: list[list[int]] = []
        for r in range(n):
            rz = [0] * n
            for c in range(n):
                rz[zones[r][c]] |= 1 << c
            row_zone_mask.append(rz)

        # adj_mask[col] = masque excluant col-1, col, col+1
        adj_mask = [0] * n
        for c in range(n):
            forbidden = 1 << c
            if c > 0:
                forbidden |= 1 << (c - 1)
            if c < n - 1:
                forbidden |= 1 << (c + 1)
            adj_mask[c] = ALL ^ forbidden

        placement = [-1] * n

        def domain(r: int, free_cols: int, free_zones: int, prev_col: int) -> int:
            """Domaine valide de la ligne r sous les contraintes courantes."""
            rz = row_zone_mask[r]
            cols_in_free_zones = 0
            fz = free_zones
            while fz:
                lsb = fz & (-fz)
                z = lsb.bit_length() - 1
                cols_in_free_zones |= rz[z]
                fz ^= lsb
            d = free_cols & cols_in_free_zones
            if prev_col >= 0:
                d &= adj_mask[prev_col]
            return d

        def backtrack(row: int, free_cols: int, free_zones: int) -> None:
            nonlocal iterations
            iterations += 1
            if iterations > self.max_iterations:
                return

            if row == n:
                solutions.append([[i, placement[i]] for i in range(n)])
                return

            prev_col = placement[row - 1] if row > 0 else -1

            # Domaine de la ligne courante
            d = domain(row, free_cols, free_zones, prev_col)
            if d == 0:
                return

            # Itérer sur les colonnes du domaine via bit tricks
            while d:
                lsb = d & (-d)
                col = lsb.bit_length() - 1
                d ^= lsb

                z = zones[row][col]
                new_free_cols = free_cols ^ lsb
                new_free_zones = free_zones ^ (1 << z)

                # ── Forward-checking multi-lignes ─────────────────────────
                # Pour chaque ligne restante : domaine doit être non vide.
                # Aussi : chaque zone libre doit être vue depuis au moins une
                # ligne restante (atteignabilité).
                ok = True
                zone_seen = 0

                for r2 in range(row + 1, n):
                    # Domaine sans contrainte d'adjacence (conservative mais O(1))
                    rz2 = row_zone_mask[r2]
                    cols2 = 0
                    fz = new_free_zones
                    while fz:
                        lb = fz & (-fz)
                        z2 = lb.bit_length() - 1
                        cols2 |= rz2[z2]
                        fz ^= lb
                    cols2 &= new_free_cols
                    if cols2 == 0:
                        ok = False
                        break
                    # Accumuler les zones atteignables depuis cette ligne
                    # (colonnes libres de r2 → zones correspondantes)
                    fz = new_free_zones
                    while fz:
                        lb = fz & (-fz)
                        z2 = lb.bit_length() - 1
                        if rz2[z2] & new_free_cols:
                            zone_seen |= lb
                        fz ^= lb

                if ok and zone_seen != new_free_zones:
                    ok = False

                if not ok:
                    continue

                placement[row] = col
                backtrack(row + 1, new_free_cols, new_free_zones)
                placement[row] = -1

        logger.info(f"🚀 TRM — résolution {n}x{n}")
        backtrack(0, ALL, ALL)
        logger.info(f"🎯 {len(solutions)} solutions, {iterations} itérations")

        return solutions, iterations
