"""
Routes API pour Baseline Solver (heuristique greedy + local search)
"""
import time
from fastapi import APIRouter

from api.models import GridInput, BaselineSolution, BaselinePerformance
from src.greedy_model import QueensGreedyBaseline

router = APIRouter()

# Instance du modèle heuristique
_model = QueensGreedyBaseline()


@router.post("/solve", response_model=BaselineSolution)
async def solve(grid: GridInput):
    """
    Résout les N-Reines via heuristique greedy + local search (très rapide).
    Supporte n'importe quelle taille de grille.
    """
    size = grid.size

    try:
        start = time.perf_counter()
        solution, conflicts = _model.solve(size)
        elapsed = time.perf_counter() - start

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
    return {"status": "healthy", "service": "Baseline Queens Solver (Greedy)"}
