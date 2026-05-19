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

_model: QueensBaseline | None = None
_CKPT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "best.pt")


def _load_model() -> QueensBaseline:
    global _model
    if _model is not None:
        return _model

    m = QueensBaseline()
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
    else:
        m.load_state_dict(checkpoint)

    m.eval()
    _model = m
    return _model


@router.post("/solve", response_model=BaselineSolution)
async def solve(grid: GridInput):
    """
    Résout les 8-Reines via inférence neuronale (one-shot MLP).
    Ne supporte que les grilles 8x8. Les zones sont ignorées.
    """
    if grid.size != 8:
        return BaselineSolution(
            supported=False,
            error=f"Le modèle baseline supporte uniquement les grilles 8x8 (reçu {grid.size}x{grid.size})",
        )

    model = _load_model()

    # Entrée entièrement inconnue (toutes les lignes à prédire)
    x = torch.full((1, 8), -1, dtype=torch.long)

    start = time.perf_counter()
    pred = model.predict(x)  # (1, 8)
    elapsed = time.perf_counter() - start

    cols = pred[0].tolist()
    solution = [[r, cols[r]] for r in range(8)]

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


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "Baseline Queens Solver"}
