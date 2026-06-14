"""
Tests d'intégration des routes API TRM via httpx.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from httpx import AsyncClient, ASGITransport
from app import app

TRANSPORT = ASGITransport(app=app)
BASE = "http://test"

VALID_PAYLOAD_4x4 = {
    "size": 4,
    "zones": [
        [0, 0, 1, 1],
        [0, 0, 1, 1],
        [2, 2, 3, 3],
        [2, 2, 3, 3],
    ],
}

IMPOSSIBLE_PAYLOAD = {
    "size": 4,
    "zones": [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
}


@pytest.mark.asyncio
class TestHealth:
    async def test_health_returns_200(self):
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.get("/api/health")
        assert r.status_code == 200

    async def test_health_returns_healthy_status(self):
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.get("/api/health")
        assert r.json()["status"] == "healthy"

    async def test_health_identifies_service(self):
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.get("/api/health")
        assert "TRM" in r.json()["service"]


@pytest.mark.asyncio
class TestSolveEndpoint:
    async def test_solve_valid_grid_returns_200(self):
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.post("/api/solve", json=VALID_PAYLOAD_4x4)
        assert r.status_code == 200

    async def test_solve_returns_solutions_list(self):
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.post("/api/solve", json=VALID_PAYLOAD_4x4)
        data = r.json()
        assert "solutions" in data
        assert isinstance(data["solutions"], list)
        assert len(data["solutions"]) > 0

    async def test_solve_returns_performance_metrics(self):
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.post("/api/solve", json=VALID_PAYLOAD_4x4)
        perf = r.json()["performance"]
        assert "execution_time" in perf
        assert "iterations" in perf
        assert "solutions_count" in perf
        assert perf["execution_time"] > 0
        assert perf["iterations"] > 0

    async def test_solve_impossible_grid_returns_empty_solutions(self):
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.post("/api/solve", json=IMPOSSIBLE_PAYLOAD)
        assert r.status_code == 200
        assert r.json()["solutions"] == []

    async def test_solve_wrong_row_count_returns_400(self):
        payload = {
            "size": 4,
            "zones": [
                [0, 0, 1, 1],
                [2, 2, 3, 3],
                # manque 2 lignes
            ],
        }
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.post("/api/solve", json=payload)
        assert r.status_code == 400

    async def test_solve_wrong_column_count_returns_400(self):
        payload = {
            "size": 4,
            "zones": [
                [0, 0, 1],  # 3 colonnes au lieu de 4
                [0, 0, 1, 1],
                [2, 2, 3, 3],
                [2, 2, 3, 3],
            ],
        }
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.post("/api/solve", json=payload)
        assert r.status_code == 400


@pytest.mark.asyncio
class TestExtractMatrixEndpoint:
    async def test_extract_matrix_text_file_returns_400(self):
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.post(
                "/api/extract-matrix",
                files={"file": ("test.txt", b"hello", "text/plain")},
            )
        assert r.status_code == 400

    async def test_extract_matrix_empty_image_returns_400(self):
        async with AsyncClient(transport=TRANSPORT, base_url=BASE) as client:
            r = await client.post(
                "/api/extract-matrix",
                files={"file": ("empty.png", b"", "image/png")},
            )
        assert r.status_code == 400
