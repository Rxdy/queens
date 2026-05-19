"""
Routes API pour Baseline Solver (réseau de neurones MLP one-shot)
"""
import os
import time

import torch
from fastapi import APIRouter

from api.models import GridInput, BaselineSolution, BaselinePerformance
from src.model import QueensBaseline
from src.metrics import count_conflicts

router = APIRouter()

_models: dict[int, QueensBaseline] = {}  # Cache de modèles par taille
_CKPT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "best.pt")


def _load_model(n: int) -> QueensBaseline:
    """
    Charger ou créer un modèle pour la taille n.
    - Si n=8 et checkpoint existe: charger les poids pré-entraînés
    - Sinon: créer un nouveau modèle avec initialisation aléatoire
    """
    if n in _models:
        return _models[n]

    m = QueensBaseline(n=n)

    # Charger les poids du checkpoint uniquement pour n=8
    if n == 8 and os.path.exists(_CKPT_PATH):
        try:
            checkpoint = torch.load(_CKPT_PATH, map_location="cpu", weights_only=True)

            if isinstance(checkpoint, dict):
                # Format sauvegardé par train.py : {"model_state": ..., "config": ..., ...}
                if "model_state" in checkpoint:
                    m.load_state_dict(checkpoint["model_state"])
                elif "model_state_dict" in checkpoint:
                    m.load_state_dict(checkpoint["model_state_dict"])
                elif "state_dict" in checkpoint:
                    m.load_state_dict(checkpoint["state_dict"])
                else:
                    # Tentative de chargement direct (OrderedDict de poids)
                    m.load_state_dict(checkpoint)
        except Exception as e:
            print(f"Impossible de charger le checkpoint pour n=8: {e}")
            # Continuer avec initialisation aléatoire

    m.eval()
    _models[n] = m
    return _models[n]


@router.post("/solve", response_model=BaselineSolution)
async def solve(grid: GridInput):
    """
    Résout les N-Reines via inférence neuronale (one-shot MLP).
    Supporte n'importe quelle taille de grille (contrairement à la version 8x8).
    """
    size = grid.size

    try:
        model = _load_model(size)

        # Entrée entièrement inconnue (toutes les lignes à prédire)
        x = torch.full((1, size), -1, dtype=torch.long)

        start = time.perf_counter()
        pred = model.predict(x)  # (1, size)
        elapsed = time.perf_counter() - start

        cols = pred[0].tolist()
        solution = [[r, cols[r]] for r in range(size)]

        conflicts = int(count_conflicts(cols))
        valid = conflicts == 0

        return BaselineSolution(
            supported=True,
            solution=solution,
            performance=BaselinePerformance(
                execution_time=elapsed,
                valid=valid,
                conflicts=conflicts,
            ),
        )
    except Exception as e:
        return BaselineSolution(
            supported=False,
            error=f"Erreur lors de la résolution: {str(e)}",
        )


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "Baseline Queens Solver"}
