"""
Statistiques du défi quotidien : nombre de résolutions humaines et meilleur
temps, par (jour, taille de grille). Le jeu étant anonyme (pas de compte,
pas d'identifiant joueur), on ne stocke ici que des compteurs agrégés — comme
core.stats.py pour les performances du solveur, mais pour les temps humains.
"""

import json
import os
import threading
from pathlib import Path

from core.config import DAILY_STATS_FILE_PATH

_STATS_PATH = Path(DAILY_STATS_FILE_PATH)
_lock = threading.Lock()


def _bucket_key(puzzle_day: str, size: int) -> str:
    return f"{puzzle_day}:{size}"


def _load() -> dict:
    try:
        with open(_STATS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(stats: dict) -> None:
    _STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = _STATS_PATH.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    os.replace(tmp_path, _STATS_PATH)


_stats = _load()


def record_daily_solve(puzzle_day: str, size: int, time_ms: float) -> dict:
    """Enregistre une résolution humaine et retourne le compteur mis à jour."""
    with _lock:
        key = _bucket_key(puzzle_day, size)
        bucket = _stats.setdefault(key, {"count": 0, "best_time_ms": None})
        bucket["count"] += 1
        if bucket["best_time_ms"] is None or time_ms < bucket["best_time_ms"]:
            bucket["best_time_ms"] = time_ms
        _save(_stats)
        return dict(bucket)


def get_daily_stats(puzzle_day: str) -> dict:
    """Retourne {taille (str): {count, best_time_ms}} pour le jour demandé."""
    with _lock:
        prefix = f"{puzzle_day}:"
        return {
            key[len(prefix) :]: dict(bucket)
            for key, bucket in _stats.items()
            if key.startswith(prefix)
        }
