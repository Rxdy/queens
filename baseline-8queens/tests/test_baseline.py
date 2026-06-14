"""
Tests unitaires et d'intégration pour le Baseline Solver.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from httpx import AsyncClient, ASGITransport
from src.greedy_model import QueensGreedyBaseline
from app import app

TRANSPORT = ASGITransport(app=app)
BASE = "http://test"

ZONES_4x4 = [
    [0, 0, 1, 1],
    [0, 0, 1, 1],
    [2, 2, 3, 3],
    [2, 2, 3, 3],
]

ZONES_4x4_IMPOSSIBLE = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
]


def is_valid_solution(solution, size, zones):
    if len(solution) != size:
        return False
    cols   = [pos[1] for pos in solution]
    z_used = [zones[pos[0]][pos[1]] for pos in solution]
    if len(set(cols)) != size:
        return False
    if len(set(z_used)) != size:
        return False
    for i in range(len(solution)):
        for j in range(i + 1, len(solution)):
            if max(abs(solution[i][0] - solution[j][0]),
                   abs(solution[i][1] - solution[j][1])) <= 1:
                return False
    return True


# ── Tests unitaires du modèle ───────────────────────────────────────────────

class TestQueensGreedyBaseline:
    def test_solve_4x4_returns_solution(self):
        model = QueensGreedyBaseline()
        sol, count = model.solve_exhaustive(4, ZONES_4x4)
        assert count > 0
        assert sol is not None
        assert len(sol) == 4

    def test_solve_4x4_count_matches_trm(self):
        """Le baseline doit trouver le même nombre de solutions que le TRM (2 pour cette grille)."""
        model = QueensGreedyBaseline()
        _, count = model.solve_exhaustive(4, ZONES_4x4)
        assert count == 2

    def test_first_solution_is_valid(self):
        model = QueensGreedyBaseline()
        sol, count = model.solve_exhaustive(4, ZONES_4x4)
        assert is_valid_solution(sol, 4, ZONES_4x4)

    def test_impossible_grid_returns_zero_count(self):
        model = QueensGreedyBaseline()
        sol, count = model.solve_exhaustive(4, ZONES_4x4_IMPOSSIBLE)
        assert count == 0

    def test_impossible_grid_returns_empty_solution(self):
        model = QueensGreedyBaseline()
        sol, count = model.solve_exhaustive(4, ZONES_4x4_IMPOSSIBLE)
        assert sol == []

    def test_solution_columns_are_unique(self):
        model = QueensGreedyBaseline()
        sol, _ = model.solve_exhaustive(4, ZONES_4x4)
        cols = [pos[1] for pos in sol]
        assert len(set(cols)) == 4

    def test_solution_zones_are_unique(self):
        model = QueensGreedyBaseline()
        sol, _ = model.solve_exhaustive(4, ZONES_4x4)
        zones_used = [ZONES_4x4[pos[0]][pos[1]] for pos in sol]
        assert len(set(zones_used)) == 4

    def test_no_adjacent_queens(self):
        model = QueensGreedyBaseline()
        sol, _ = model.solve_exhaustive(4, ZONES_4x4)
        for i in range(len(sol)):
            for j in range(i + 1, len(sol)):
                dist = max(abs(sol[i][0] - sol[j][0]), abs(sol[i][1] - sol[j][1]))
                assert dist > 1, f"Reines adjacentes : {sol[i]} et {sol[j]}"


# ── Tests d'intégration API ─────────────────────────────────────────────────

@pytest.mark.asyncio
class TestBaselineHealth:
    async def test_health_returns_200(self):
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.get("/api/health")
        assert r.status_code == 200

    async def test_health_status_is_healthy(self):
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.get("/api/health")
        assert r.json()["status"] == "healthy"


@pytest.mark.asyncio
class TestBaselineSolveEndpoint:
    async def test_solve_valid_grid_returns_200(self):
        payload = {"size": 4, "zones": ZONES_4x4}
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.post("/api/solve", json=payload)
        assert r.status_code == 200

    async def test_solve_returns_supported_true(self):
        payload = {"size": 4, "zones": ZONES_4x4}
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.post("/api/solve", json=payload)
        assert r.json()["supported"] is True

    async def test_solve_returns_solution(self):
        payload = {"size": 4, "zones": ZONES_4x4}
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.post("/api/solve", json=payload)
        data = r.json()
        assert data["solution"] is not None
        assert len(data["solution"]) == 4

    async def test_solve_returns_correct_solution_count(self):
        payload = {"size": 4, "zones": ZONES_4x4}
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.post("/api/solve", json=payload)
        assert r.json()["performance"]["solutions_count"] == 2

    async def test_solve_impossible_grid_returns_zero_count(self):
        payload = {"size": 4, "zones": ZONES_4x4_IMPOSSIBLE}
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.post("/api/solve", json=payload)
        data = r.json()
        assert data["performance"]["solutions_count"] == 0
