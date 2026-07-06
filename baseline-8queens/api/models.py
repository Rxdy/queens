"""
Modèles Pydantic pour l'API Baseline Solver
"""

from pydantic import BaseModel, Field


class GridInput(BaseModel):
    size: int = Field(..., description="Taille de la grille (size x size)", ge=1)
    zones: list[list[int]] = Field(..., description="Grille des zones (matrice size x size)")


class BaselinePerformance(BaseModel):
    execution_time: float = Field(..., description="Temps d'exécution en secondes")
    valid: bool = Field(..., description="La solution est-elle valide (sans conflit)?")
    conflicts: int = Field(..., description="Nombre de conflits dans la première solution")
    solutions_count: int = Field(0, description="Nombre total de solutions trouvées")


class BaselineSolution(BaseModel):
    supported: bool = Field(..., description="La taille de grille est-elle supportée?")
    solution: list[list[int]] | None = Field(
        None, description="Première solution [[row, col], ...]"
    )
    solutions: list[list[list[int]]] | None = Field(None, description="Toutes les solutions")
    performance: BaselinePerformance | None = None
    error: str | None = None
