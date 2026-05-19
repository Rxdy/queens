"""
Modèles Pydantic pour l'API TRM Solver
"""
from pydantic import BaseModel, Field
from typing import List


class GridInput(BaseModel):
    """Modèle pour la requête de résolution"""
    rows: int = Field(..., description="Taille de la grille (rows x rows)", ge=1)
    cols: int = Field(..., description="Taille de la grille (cols x cols)", ge=1)
    zones: List[List[int]] = Field(..., description="Grille des zones (matrice size x size)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rows": 4,
                "cols": 4,
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
