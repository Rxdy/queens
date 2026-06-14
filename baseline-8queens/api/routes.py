"""
Routes API pour Baseline Solver (heuristique greedy + local search)
"""
import asyncio
import time
from fastapi import APIRouter
from functools import partial

from api.models import GridInput, BaselineSolution, BaselinePerformance
from src.greedy_model import QueensGreedyBaseline

router = APIRouter()

# Instance du modèle baseline
_model = QueensGreedyBaseline()


@router.post("/solve", response_model=BaselineSolution)
async def solve(grid: GridInput):
    """
    Résout les N-Reines par backtracking naïf exhaustif (sans optimisations).
    Trouve TOUTES les solutions comme le TRM, pour une comparaison équitable.
    """
    size = grid.size
    zones = grid.zones

    try:
        loop = asyncio.get_running_loop()
        start = time.perf_counter()
        first_solution, count = await loop.run_in_executor(
            None, partial(_model.solve_exhaustive, size, zones)
        )
        elapsed = time.perf_counter() - start

        valid = count > 0

        return BaselineSolution(
            supported=True,
            solution=first_solution,
            solutions=[first_solution] if first_solution else [],
            performance=BaselinePerformance(
                execution_time=elapsed,
                valid=valid,
                conflicts=0,
                solutions_count=count,
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
