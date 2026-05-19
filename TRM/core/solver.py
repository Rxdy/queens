"""
Solveur pour le problème des N-Reines avec contraintes de zones
"""
from typing import List, Tuple, Set
import logging

logger = logging.getLogger("trm_solver")


class QueensSolver:
    """
    Classe pour résoudre le problème des N-Reines avec contraintes de zones
    """
    
    def __init__(self, max_iterations: int = 10_000_000):
        """
        Initialise le solveur
        
        Args:
            max_iterations: Nombre maximum d'itérations autorisées
        """
        self.max_iterations = max_iterations
        self.iterations = 0
    
    def is_safe(self, row: int, col: int, positions: List[List[int]]) -> bool:
        """
        Vérifie si une position est sûre pour placer une reine.

        Optimisation clé : avec un placement ligne par ligne, seule la reine
        de la ligne précédente (row-1) peut être adjacente au sens max(dr,dc)==1.
        Pour toute reine à row-k (k>=2), dr=k>=2 donc max(dr,dc)>=2 → jamais adjacent.
        → Vérification O(1) au lieu de O(row).
        """
        if not positions:
            return True
        _, prev_col = positions[-1]   # prev_row == row - 1 (toujours, car backtracking ligne/ligne)
        return abs(col - prev_col) > 1
    
    def solve(self, size: int, zones: List[List[int]]) -> Tuple[List[List[List[int]]], int]:
        """
        Résout le problème des Queens avec contraintes de zones par backtracking.
        
        Args:
            size: Taille de la grille (size x size)
            zones: Grille des zones (matrice size x size)
        
        Returns:
            Tuple (solutions, iterations) où:
            - solutions: Liste de toutes les solutions trouvées
            - iterations: Nombre total d'itérations effectuées
        """
        self.iterations = 0
        solutions = []
        
        def backtrack(
            row: int,
            used_cols: Set[int],
            used_zones: Set[int],
            positions: List[List[int]]
        ) -> None:
            """Fonction récursive de backtracking"""
            self.iterations += 1
            
            if self.iterations > self.max_iterations:
                logger.warning(f"⚠️  Limite d'itérations atteinte: {self.max_iterations}")
                return
            
            # Condition de terminaison: toutes les lignes ont une reine
            if row == size:
                solutions.append(positions[:])  # Ajouter une copie de la solution
                return
            
            # Essayer chaque colonne pour cette ligne
            for col in range(size):
                zone = zones[row][col]
                
                # Vérifier les contraintes
                if col in used_cols:
                    continue
                if zone in used_zones:
                    continue
                if not self.is_safe(row, col, positions):
                    continue
                
                # Placement de la reine
                used_cols.add(col)
                used_zones.add(zone)
                positions.append([row, col])
                
                # Récursion sur la ligne suivante
                backtrack(row + 1, used_cols, used_zones, positions)
                
                # Backtrack
                positions.pop()
                used_zones.remove(zone)
                used_cols.remove(col)
        
        # Initialisation et lancement de la résolution
        positions: List[List[int]] = []
        used_cols: Set[int] = set()
        used_zones: Set[int] = set()
        
        logger.info(f"🚀 Début de la résolution pour grille {size}x{size}")
        backtrack(0, used_cols, used_zones, positions)
        logger.info(f"🎯 {len(solutions)} solutions trouvées après {self.iterations} itérations")
        
        return solutions, self.iterations
