"""
Tests unitaires pour les statistiques globales agrégées (core.stats) et
tests d'intégration pour l'endpoint GET /api/stats.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import core.stats as stats_module  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_stats(tmp_path, monkeypatch):
    """Isole chaque test : fichier temporaire + state en mémoire réinitialisé."""
    monkeypatch.setattr(stats_module, "_STATS_PATH", tmp_path / "stats.json")
    monkeypatch.setattr(stats_module, "_stats", stats_module._empty_stats())
    yield tmp_path / "stats.json"


class TestUpdateBucket:
    def test_moyenne_incrementale(self):
        bucket = stats_module._empty_bucket()
        stats_module._update_bucket(bucket, 0.01, 2)
        stats_module._update_bucket(bucket, 0.03, 4)
        assert bucket["count"] == 2
        assert bucket["avg_execution_time"] == pytest.approx(0.02)
        assert bucket["avg_solutions_count"] == pytest.approx(3)

    def test_min_max(self):
        bucket = stats_module._empty_bucket()
        for t in (0.05, 0.01, 0.09, 0.02):
            stats_module._update_bucket(bucket, t, 1)
        assert bucket["min_execution_time"] == pytest.approx(0.01)
        assert bucket["max_execution_time"] == pytest.approx(0.09)


class TestRecordSolve:
    def test_incremente_total_solves(self):
        stats_module.record_solve(6, 0.01, 2)
        stats_module.record_solve(8, 0.02, 3)
        result = stats_module.get_stats()
        assert result["total_solves"] == 2

    def test_ventile_par_taille(self):
        stats_module.record_solve(6, 0.01, 2)
        stats_module.record_solve(6, 0.03, 4)
        stats_module.record_solve(8, 0.05, 1)
        result = stats_module.get_stats()
        assert result["by_size"]["6"]["count"] == 2
        assert result["by_size"]["8"]["count"] == 1
        assert result["by_size"]["6"]["avg_execution_time"] == pytest.approx(0.02)

    def test_overall_agrege_toutes_tailles(self):
        stats_module.record_solve(6, 0.01, 2)
        stats_module.record_solve(8, 0.03, 4)
        result = stats_module.get_stats()
        assert result["overall"]["count"] == 2
        assert result["overall"]["avg_execution_time"] == pytest.approx(0.02)

    def test_persiste_sur_disque(self, isolated_stats):
        stats_module.record_solve(6, 0.01, 2)
        with open(isolated_stats, encoding="utf-8") as f:
            on_disk = json.load(f)
        assert on_disk["total_solves"] == 1
        assert on_disk["by_size"]["6"]["count"] == 1

    def test_ne_stocke_aucune_partie_individuelle(self, isolated_stats):
        stats_module.record_solve(6, 0.01, 2)
        with open(isolated_stats, encoding="utf-8") as f:
            on_disk = json.load(f)
        # Seulement des agrégats : ni zones, ni timestamp par résolution, ni liste de parties.
        assert set(on_disk.keys()) == {
            "since",
            "last_updated",
            "total_solves",
            "overall",
            "by_size",
        }
        assert "solves" not in on_disk
        assert "history" not in on_disk


class TestLoad:
    def test_fichier_absent_retourne_stats_vides(self):
        # _load() lit stats_module._STATS_PATH courant (monkeypatché par la fixture),
        # qui pointe vers un fichier temporaire inexistant.
        result = stats_module._load()
        assert result["total_solves"] == 0

    def test_fichier_corrompu_retourne_stats_vides(self, isolated_stats):
        isolated_stats.write_text("{ceci n'est pas du json", encoding="utf-8")
        result = stats_module._load()
        assert result["total_solves"] == 0


@pytest.mark.asyncio
class TestStatsEndpoint:
    async def test_stats_returns_200(self):
        from httpx import ASGITransport, AsyncClient

        from app import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.get("/api/stats")
        assert r.status_code == 200

    async def test_stats_shape(self):
        from httpx import ASGITransport, AsyncClient

        from app import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.get("/api/stats")
        data = r.json()
        assert "total_solves" in data
        assert "overall" in data
        assert "by_size" in data

    async def test_solve_incremente_les_stats(self):
        from httpx import ASGITransport, AsyncClient

        from app import app

        payload = {
            "size": 4,
            "zones": [
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [2, 2, 3, 3],
                [2, 2, 3, 3],
            ],
        }
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            before = (await client.get("/api/stats")).json()["total_solves"]
            await client.post("/api/solve", json=payload)
            after = (await client.get("/api/stats")).json()["total_solves"]
        assert after == before + 1
