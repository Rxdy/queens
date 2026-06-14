"""
Routes API pour TRM Solver
"""
import asyncio
from functools import partial
from fastapi import APIRouter, HTTPException, UploadFile, File
import logging
import time

from api.models import GridInput, Solution, PerformanceMetrics, ExtractedMatrix
from core.solver import QueensSolver
from core.config import MAX_ITERATIONS
from utils.image_processor import extract_matrix_from_image

logger = logging.getLogger("trm_solver")
router = APIRouter()

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

        loop = asyncio.get_running_loop()
        start_time = time.time()
        solutions, iterations = await loop.run_in_executor(
            None, partial(solver.solve, grid.size, grid.zones)
        )
        end_time = time.time()

        execution_time = end_time - start_time
        solutions_count = len(solutions)
        solutions_per_second = solutions_count / execution_time if execution_time > 0 else 0

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


@router.post("/extract-matrix", response_model=ExtractedMatrix)
async def extract_matrix(file: UploadFile = File(...)):
    """
    Extrait une matrice de zones d'une image de grille.

    Args:
        file: Fichier image (PNG, JPG, etc.)

    Returns:
        Matrice extraite avec taille et score de confiance
    """
    try:
        if file.content_type not in ["image/png", "image/jpeg", "image/jpg", "image/gif"]:
            raise HTTPException(
                status_code=400,
                detail=f"Type de fichier non supporté: {file.content_type}. Utilisez PNG, JPG ou GIF."
            )

        image_data = await file.read()

        if not image_data:
            raise HTTPException(status_code=400, detail="Fichier image vide")

        logger.info(f"🖼️  Traitement d'image: {file.filename} ({len(image_data)} bytes)")

        result = extract_matrix_from_image(image_data)

        logger.info(f"✅ Matrice extraite: {result['size']}x{result['size']}")
        logger.info(f"📊 Confiance: {result['confidence']:.2%}")

        return ExtractedMatrix(
            size=result["size"],
            zones=result["zones"],
            confidence=result["confidence"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement de l'image: {str(e)}")


@router.get("/health")
async def health():
    """Point de santé de l'API"""
    return {
        "status": "healthy",
        "service": "TRM Solver",
        "max_iterations": MAX_ITERATIONS
    }
