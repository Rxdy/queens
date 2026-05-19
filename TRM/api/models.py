"""
Modèles Pydantic pour l'API TRM Solver
"""
from pydantic import BaseModel, Field
from typing import List


class GridInput(BaseModel):
    """Modèle pour la requête de résolution"""
    size: int = Field(..., description="Taille de la grille (size x size)", ge=1)
    zones: List[List[int]] = Field(..., description="Grille des zones (matrice size x size)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "size": 4,
                "zones": [
                    [0, 0, 1, 1],
                    [0, 2, 2, 1],
                    [3, 2, 2, 1],
                    [3, 3, 3, 1]
                ]
            }
        }


class PerformanceMetrics(BaseModel):
    """Métriques de performance de la résolution"""
    execution_time: float = Field(..., description="Temps d'exécution en secondes")
    iterations: int = Field(..., description="Nombre d'itérations effectuées")
    solutions_count: int = Field(..., description="Nombre de solutions trouvées")
    solutions_per_second: float = Field(..., description="Solutions par seconde")


class Solution(BaseModel):
    """Modèle pour la réponse de résolution"""
    solutions: List[List[List[int]]] = Field(
        ...,
        description="Liste des solutions (chaque solution est une liste de [row, col])"
    )
    performance: PerformanceMetrics = Field(..., description="Métriques de performance")
    
    class Config:
        json_schema_extra = {
            "example": {
                "solutions": [
                    [[0, 1], [1, 3], [2, 0], [3, 2]]
                ],
                "performance": {
                    "execution_time": 0.0123,
                    "iterations": 42,
                    "solutions_count": 1,
                    "solutions_per_second": 81.3
                }
            }
        }


class ExtractedMatrix(BaseModel):
    """Modèle pour la réponse d'extraction de matrice d'image"""
    size: int = Field(..., description="Taille de la grille détectée")
    zones: List[List[int]] = Field(..., description="Matrice de zones extraite")
    confidence: float = Field(..., description="Score de confiance de l'extraction (0-1)")
    
    class Config:
        json_schema_extra = {
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
                    [12, 12, 12, 12, 10, 10, 10, 10]
                ],
                "confidence": 0.85
            }
        }

