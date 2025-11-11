"""
Routes API pour TRM Solver
"""
from fastapi import APIRouter, HTTPException
import logging
import time

from api.models import GridInput, Solution, PerformanceMetrics
from core.solver import QueensSolver
from core.config import MAX_ITERATIONS

logger = logging.getLogger("trm_solver")
router = APIRouter()

# Instance du solveur
solver = QueensSolver(max_iterations=MAX_ITERATIONS)


@router.post("/solve", response_model=Solution)
async def solve(grid: GridInput):
    """
    Résout le problème des N-Reines avec contraintes de zones
    
    Args:
        grid: Grille avec taille et zones
    
    Returns:
        Solutions trouvées avec métriques de performance
    """
    try:
        logger.info(f"🔍 Reçu grille de taille {grid.size}")
        logger.debug("📊 Grille des zones:")
        for i, row in enumerate(grid.zones):
            logger.debug(f"   Ligne {i}: {row}")
        
        # Validation de la grille
        if len(grid.zones) != grid.size:
            raise HTTPException(
                status_code=400,
                detail=f"La grille doit avoir {grid.size} lignes, reçu {len(grid.zones)}"
            )
        
        for i, row in enumerate(grid.zones):
            if len(row) != grid.size:
                raise HTTPException(
                    status_code=400,
                    detail=f"La ligne {i} doit avoir {grid.size} colonnes, reçu {len(row)}"
                )
        
        # Résolution
        start_time = time.time()
        solutions, iterations = solver.solve(grid.size, grid.zones)
        end_time = time.time()
        
        execution_time = end_time - start_time
        solutions_count = len(solutions)
        solutions_per_second = solutions_count / execution_time if execution_time > 0 else 0
        
        # Métriques de performance
        performance = PerformanceMetrics(
            execution_time=execution_time,
            iterations=iterations,
            solutions_count=solutions_count,
            solutions_per_second=solutions_per_second
        )
        
        logger.info(f"✅ {solutions_count} solutions trouvées")
        logger.info(f"⏱️  Temps d'exécution: {execution_time:.4f} secondes")
        logger.info(f"🔢 Itérations totales: {iterations}")
        logger.info(f"📈 Performance: {solutions_per_second:.2f} solutions/seconde")
        
        return Solution(solutions=solutions, performance=performance)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la résolution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.get("/health")
async def health():
    """Point de santé de l'API"""
    return {
        "status": "healthy",
        "service": "TRM Solver",
        "max_iterations": MAX_ITERATIONS
    }
