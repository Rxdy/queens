"""
Tests unitaires pour les statistiques du défi quotidien (core.daily_stats) et
tests d'intégration pour les endpoints POST /api/daily/solve et
GET /api/daily/stats/{puzzle_day}.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import core.daily_stats as daily_stats_module  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_daily_stats(tmp_path, monkeypatch):
    monkeypatch.setattr(daily_stats_module, "_STATS_PATH", tmp_path / "daily_stats.json")
    monkeypatch.setattr(daily_stats_module, "_stats", {})
    yield tmp_path / "daily_stats.json"


class TestRecordDailySolve:
    def test_premiere_resolution(self):
        bucket = daily_stats_module.record_daily_solve("2026-07-14", 6, 15000)
        assert bucket == {"count": 1, "best_time_ms": 15000}

    def test_incremente_le_compteur(self):
        daily_stats_module.record_daily_solve("2026-07-14", 6, 15000)
        bucket = daily_stats_module.record_daily_solve("2026-07-14", 6, 20000)
        assert bucket["count"] == 2

    def test_garde_le_meilleur_temps(self):
        daily_stats_module.record_daily_solve("2026-07-14", 6, 20000)
        daily_stats_module.record_daily_solve("2026-07-14", 6, 9000)
        bucket = daily_stats_module.record_daily_solve("2026-07-14", 6, 15000)
        assert bucket["best_time_ms"] == 9000
        assert bucket["count"] == 3

    def test_isole_par_taille_et_par_jour(self):
        daily_stats_module.record_daily_solve("2026-07-14", 6, 10000)
        daily_stats_module.record_daily_solve("2026-07-14", 7, 12000)
        daily_stats_module.record_daily_solve("2026-07-15", 6, 8000)
        result = daily_stats_module.get_daily_stats("2026-07-14")
        assert set(result.keys()) == {"6", "7"}
        assert result["6"]["count"] == 1

    def test_persiste_sur_disque(self, isolated_daily_stats):
        daily_stats_module.record_daily_solve("2026-07-14", 8, 30000)
        with open(isolated_daily_stats, encoding="utf-8") as f:
            on_disk = json.load(f)
        assert on_disk["2026-07-14:8"]["count"] == 1


class TestGetDailyStats:
    def test_jour_sans_resolution_retourne_vide(self):
        assert daily_stats_module.get_daily_stats("2026-01-01") == {}


@pytest.mark.asyncio
class TestDailyEndpoints:
    async def test_daily_solve_returns_200(self):
        from httpx import ASGITransport, AsyncClient

        from app import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post(
                "/api/daily/solve",
                json={"puzzle_day": "2026-07-14", "size": 6, "time_ms": 15000},
            )
        assert r.status_code == 200
        assert r.json()["count"] >= 1

    async def test_daily_solve_rejette_jour_mal_formate(self):
        from httpx import ASGITransport, AsyncClient

        from app import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post(
                "/api/daily/solve",
                json={"puzzle_day": "14-07-2026", "size": 6, "time_ms": 15000},
            )
        assert r.status_code == 422

    async def test_daily_solve_rejette_temps_trop_petit(self):
        from httpx import ASGITransport, AsyncClient

        from app import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post(
                "/api/daily/solve",
                json={"puzzle_day": "2026-07-14", "size": 6, "time_ms": 1},
            )
        assert r.status_code == 422

    async def test_daily_stats_reflete_les_resolutions(self):
        from httpx import ASGITransport, AsyncClient

        from app import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post(
                "/api/daily/solve",
                json={"puzzle_day": "2026-08-01", "size": 9, "time_ms": 45000},
            )
            r = await client.get("/api/daily/stats/2026-08-01")
        data = r.json()
        assert data["9"]["count"] == 1
        assert data["9"]["best_time_ms"] == 45000
