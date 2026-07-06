"""
Tests unitaires pour QueensSolver (TRM).
"""

import concurrent.futures
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.solver import QueensSolver

# ── Grilles de référence ────────────────────────────────────────────────────

# 4×4 : 4 zones en quadrants 2×2 — 2 solutions connues
ZONES_4x4 = [
    [0, 0, 1, 1],
    [0, 0, 1, 1],
    [2, 2, 3, 3],
    [2, 2, 3, 3],
]

# 4×4 sans solution possible (toutes les cellules en zone 0)
ZONES_4x4_IMPOSSIBLE = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
]


def is_valid_solution(solution, size, zones):
    """Vérifie qu'une solution respecte toutes les contraintes du jeu."""
    if len(solution) != size:
        return False

    cols = [pos[1] for pos in solution]
    z_used = [zones[pos[0]][pos[1]] for pos in solution]

    # 1 reine par colonne
    if len(set(cols)) != size:
        return False

    # 1 reine par zone
    if len(set(z_used)) != size:
        return False

    # Aucune adjacence (orthogonale ou diagonale)
    for i in range(len(solution)):
        for j in range(i + 1, len(solution)):
            if max(abs(solution[i][0] - solution[j][0]), abs(solution[i][1] - solution[j][1])) <= 1:
                return False

    return True


# ── Tests unitaires du solveur ──────────────────────────────────────────────


class TestQueensSolverBasic:
    def test_solve_4x4_returns_solutions(self):
        solver = QueensSolver()
        solutions, iterations = solver.solve(4, ZONES_4x4)
        assert len(solutions) > 0

    def test_solve_4x4_exact_count(self):
        solver = QueensSolver()
        solutions, _ = solver.solve(4, ZONES_4x4)
        assert len(solutions) == 2

    def test_all_solutions_are_valid(self):
        solver = QueensSolver()
        solutions, _ = solver.solve(4, ZONES_4x4)
        for sol in solutions:
            assert is_valid_solution(sol, 4, ZONES_4x4), f"Solution invalide : {sol}"

    def test_impossible_grid_returns_empty(self):
        solver = QueensSolver()
        solutions, _ = solver.solve(4, ZONES_4x4_IMPOSSIBLE)
        assert solutions == []

    def test_iterations_counter_is_positive(self):
        solver = QueensSolver()
        _, iterations = solver.solve(4, ZONES_4x4)
        assert iterations > 0

    def test_solution_has_one_queen_per_row(self):
        solver = QueensSolver()
        solutions, _ = solver.solve(4, ZONES_4x4)
        for sol in solutions:
            rows = [pos[0] for pos in sol]
            assert sorted(rows) == list(range(4))

    def test_solution_has_one_queen_per_column(self):
        solver = QueensSolver()
        solutions, _ = solver.solve(4, ZONES_4x4)
        for sol in solutions:
            cols = [pos[1] for pos in sol]
            assert len(set(cols)) == 4

    def test_solution_has_one_queen_per_zone(self):
        solver = QueensSolver()
        solutions, _ = solver.solve(4, ZONES_4x4)
        for sol in solutions:
            zones_used = [ZONES_4x4[pos[0]][pos[1]] for pos in sol]
            assert len(set(zones_used)) == 4


class TestQueensSolverMaxIterations:
    def test_max_iterations_one_stops_early(self):
        solver = QueensSolver(max_iterations=1)
        solutions, _ = solver.solve(4, ZONES_4x4)
        # La limite est dépassée dès la 2e récursion → aucune solution complète
        assert solutions == []

    def test_max_iterations_limits_exploration(self):
        # Avec une limite basse, on explore moins que sans limite
        solver_limited = QueensSolver(max_iterations=5)
        _, iter_limited = solver_limited.solve(4, ZONES_4x4)

        solver_full = QueensSolver()
        _, iter_full = solver_full.solve(4, ZONES_4x4)

        assert iter_limited < iter_full


class TestQueensSolverThreadSafety:
    def test_concurrent_calls_are_independent(self):
        """Deux appels parallèles ne partagent pas d'état — iterations sont indépendants."""
        solver = QueensSolver()

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            futures = [pool.submit(solver.solve, 4, ZONES_4x4) for _ in range(6)]
            for f in concurrent.futures.as_completed(futures):
                solutions, iterations = f.result()
                results.append((len(solutions), iterations))

        # Tous les appels doivent retourner 2 solutions
        for solution_count, _ in results:
            assert solution_count == 2

        # Les compteurs d'itérations doivent tous être identiques (même entrée)
        iteration_counts = [it for _, it in results]
        assert len(set(iteration_counts)) == 1, (
            f"Compteurs incohérents entre threads : {iteration_counts}"
        )
