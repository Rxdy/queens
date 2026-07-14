"""
Statistiques globales agrégées, persistées sur disque (fichier JSON).

Aucune résolution individuelle n'est conservée : uniquement des compteurs
glissants par taille de grille (moyenne incrémentale, min, max), mis à jour
à chaque résolution. Reste volontairement léger — pas de moteur SQL, un
simple fichier JSON écrit atomiquement, protégé par un verrou pour les accès
concurrents (les résolutions tournent dans un thread pool).
"""

import json
import logging
import os
import threading
from datetime import UTC, datetime
from pathlib import Path

from core.config import STATS_FILE_PATH

logger = logging.getLogger("trm_solver")

_STATS_PATH = Path(STATS_FILE_PATH)
_lock = threading.Lock()


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _empty_bucket() -> dict:
    return {
        "count": 0,
        "avg_execution_time": 0.0,
        "min_execution_time": None,
        "max_execution_time": None,
        "avg_solutions_count": 0.0,
    }


def _empty_stats() -> dict:
    now = _now()
    return {
        "since": now,
        "last_updated": now,
        "total_solves": 0,
        "overall": _empty_bucket(),
        "by_size": {},
    }


def _load() -> dict:
    try:
        with open(_STATS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        if isinstance(e, json.JSONDecodeError):
            logger.warning(f"⚠️ Fichier de stats corrompu ({e}), réinitialisation.")
        return _empty_stats()


def _save(stats: dict) -> None:
    _STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = _STATS_PATH.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    os.replace(tmp_path, _STATS_PATH)


_stats = _load()


def _update_bucket(bucket: dict, execution_time: float, solutions_count: int) -> None:
    bucket["count"] += 1
    n = bucket["count"]
    bucket["avg_execution_time"] += (execution_time - bucket["avg_execution_time"]) / n
    bucket["avg_solutions_count"] += (solutions_count - bucket["avg_solutions_count"]) / n
    bucket["min_execution_time"] = (
        execution_time
        if bucket["min_execution_time"] is None
        else min(bucket["min_execution_time"], execution_time)
    )
    bucket["max_execution_time"] = (
        execution_time
        if bucket["max_execution_time"] is None
        else max(bucket["max_execution_time"], execution_time)
    )


def record_solve(size: int, execution_time: float, solutions_count: int) -> None:
    """Met à jour les statistiques agrégées et persiste sur disque.

    Best-effort : les appelants doivent capturer les exceptions pour ne
    jamais faire échouer une résolution à cause d'un problème de stats.
    """
    with _lock:
        _stats["total_solves"] += 1
        _stats["last_updated"] = _now()
        _update_bucket(_stats["overall"], execution_time, solutions_count)
        bucket = _stats["by_size"].setdefault(str(size), _empty_bucket())
        _update_bucket(bucket, execution_time, solutions_count)
        _save(_stats)


def get_stats() -> dict:
    with _lock:
        return json.loads(json.dumps(_stats))
