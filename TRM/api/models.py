"""
Modèles Pydantic pour l'API TRM Solver
"""

from pydantic import BaseModel, ConfigDict, Field


class GridInput(BaseModel):
    """Modèle pour la requête de résolution"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "size": 4,
                "zones": [[0, 0, 1, 1], [0, 2, 2, 1], [3, 2, 2, 1], [3, 3, 3, 1]],
            }
        }
    )

    size: int = Field(..., description="Taille de la grille (size x size)", ge=1)
    zones: list[list[int]] = Field(..., description="Grille des zones (matrice size x size)")


class PerformanceMetrics(BaseModel):
    """Métriques de performance de la résolution"""

    execution_time: float = Field(..., description="Temps d'exécution en secondes")
    iterations: int = Field(..., description="Nombre d'itérations effectuées")
    solutions_count: int = Field(..., description="Nombre de solutions trouvées")
    solutions_per_second: float = Field(..., description="Solutions par seconde")


class Solution(BaseModel):
    """Modèle pour la réponse de résolution"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "solutions": [[[0, 1], [1, 3], [2, 0], [3, 2]]],
                "performance": {
                    "execution_time": 0.0123,
                    "iterations": 42,
                    "solutions_count": 1,
                    "solutions_per_second": 81.3,
                },
            }
        }
    )

    solutions: list[list[list[int]]] = Field(
        ..., description="Liste des solutions (chaque solution est une liste de [row, col])"
    )
    performance: PerformanceMetrics = Field(..., description="Métriques de performance")


class ExtractedMatrix(BaseModel):
    """Modèle pour la réponse d'extraction de matrice d'image"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "size": 8,
                "zones": [
                    [0, 0, 1, 1, 2, 2, 3, 3],
                    [0, 4, 4, 1, 2, 5, 5, 3],
                    [6, 4, 7, 1, 2, 5, 8, 3],
                    [6, 6, 7, 7, 2, 2, 8, 8],
                    [9, 9, -1, -1, 10, 10, 11, 11],
                    [9, -1, -1, -1, 10, -1, 11, 11],
                    [12, -1, -1, -1, 10, -1, -1, 11],
                    [12, 12, 12, 12, 10, 10, 10, 10],
                ],
                "confidence": 0.85,
            }
        }
    )

    size: int = Field(..., description="Taille de la grille détectée")
    zones: list[list[int]] = Field(..., description="Matrice de zones extraite")
    confidence: float = Field(..., description="Score de confiance de l'extraction (0-1)")


class SizeStats(BaseModel):
    """Statistiques agrégées (moyenne glissante) pour une taille de grille donnée"""

    count: int = Field(..., description="Nombre de résolutions comptabilisées")
    avg_execution_time: float = Field(..., description="Temps d'exécution moyen (secondes)")
    min_execution_time: float | None = Field(
        None, description="Temps d'exécution minimal (secondes)"
    )
    max_execution_time: float | None = Field(
        None, description="Temps d'exécution maximal (secondes)"
    )
    avg_solutions_count: float = Field(..., description="Nombre moyen de solutions trouvées")


class GlobalStats(BaseModel):
    """Statistiques globales agrégées depuis la mise en service (pas de données par partie)"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "since": "2026-07-14T08:00:00+00:00",
                "last_updated": "2026-07-14T20:00:00+00:00",
                "total_solves": 128,
                "overall": {
                    "count": 128,
                    "avg_execution_time": 0.0123,
                    "min_execution_time": 0.0001,
                    "max_execution_time": 0.512,
                    "avg_solutions_count": 3.4,
                },
                "by_size": {
                    "8": {
                        "count": 40,
                        "avg_execution_time": 0.0098,
                        "min_execution_time": 0.0002,
                        "max_execution_time": 0.041,
                        "avg_solutions_count": 2.1,
                    }
                },
            }
        }
    )

    since: str = Field(..., description="Horodatage de la première résolution enregistrée")
    last_updated: str = Field(..., description="Horodatage de la dernière mise à jour")
    total_solves: int = Field(..., description="Nombre total de résolutions comptabilisées")
    overall: SizeStats = Field(..., description="Statistiques toutes tailles confondues")
    by_size: dict[str, SizeStats] = Field(..., description="Statistiques par taille de grille")
