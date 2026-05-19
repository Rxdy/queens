"""
Modèles Pydantic pour l'API Baseline Solver
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class GridInput(BaseModel):
    size: int = Field(..., description="Taille de la grille (size x size)", ge=1)
    zones: List[List[int]] = Field(..., description="Grille des zones (non utilisée par le baseline)")


class BaselinePerformance(BaseModel):
    execution_time: float = Field(..., description="Temps d'inférence en secondes")
    valid: bool = Field(..., description="La solution prédite est-elle valide (sans conflit)?")
    conflicts: int = Field(..., description="Nombre de conflits dans la solution prédite")


class BaselineSolution(BaseModel):
    supported: bool = Field(..., description="Ce modèle supporte-t-il cette taille de grille?")
    solution: Optional[List[List[int]]] = Field(None, description="Solution prédite [[row, col], ...]")
    performance: Optional[BaselinePerformance] = None
    error: Optional[str] = None
