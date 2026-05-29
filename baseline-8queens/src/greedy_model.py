"""
Modèle baseline heuristique pour le problème des N-Reines
Utilise un algorithme glouton + placement itératif
"""
from typing import List
import random


class QueensGreedyBaseline:
    """
    Baseline simple et rapide pour résoudre les N-Reines.
    Approche: placement glouton + perturbations aléatoires.
    """
    
    def __init__(self, seed: int = 42):
        random.seed(seed)

    def solve_exhaustive(self, n: int, zones: list, max_iterations: int = 10**18) -> tuple:
        """
        Backtracking naïf exhaustif : compte TOUTES les solutions sans les stocker en RAM.
        Seule la première solution est gardée pour l'affichage.
        Zone constraint : une seule reine par zone (couleur).
        """
        placement = [-1] * n
        used_cols = [False] * n
        used_zones = set()
        iteration_count = [0]
        solution_count = [0]
        first_solution = [None]

        def backtrack(row: int):
            iteration_count[0] += 1
            if iteration_count[0] > max_iterations:
                return
            if row == n:
                solution_count[0] += 1
                if first_solution[0] is None:
                    first_solution[0] = [[i, placement[i]] for i in range(n)]
                return
            for col in range(n):
                if used_cols[col]:
                    continue
                # Contrainte de zone
                zone = zones[row][col] if zones and row < len(zones) and col < len(zones[row]) else -1
                if zone != -1 and zone in used_zones:
                    continue
                # Contrainte d'adjacence : uniquement avec la ligne précédente (optimisation O(1))
                if placement[row - 1] != -1 and abs(placement[row - 1] - col) <= 1:
                    continue
                # Placer la reine
                placement[row] = col
                used_cols[col] = True
                zone_added = zone != -1
                if zone_added:
                    used_zones.add(zone)
                backtrack(row + 1)
                # Retirer la reine
                placement[row] = -1
                used_cols[col] = False
                if zone_added:
                    used_zones.discard(zone)

        backtrack(0)
        sol = first_solution[0] if first_solution[0] is not None else []
        return sol, solution_count[0]
    
    def count_conflicts(self, placement: List[int]) -> int:
        """Compte le nombre de conflits (attaques) dans un placement."""
        n = len(placement)
        conflicts = 0
        for i in range(n):
            for j in range(i + 1, n):
                # Même colonne
                if placement[i] == placement[j]:
                    conflicts += 1
                # Diagonales
                elif abs(placement[i] - placement[j]) == abs(i - j):
                    conflicts += 1
        return conflicts
    
    def greedy_place(self, n: int) -> List[int]:
        """
        Placement glouton : pour chaque ligne, placer la reine
        dans la colonne avec le minimum de conflits futurs.
        """
        placement = [-1] * n
        
        for row in range(n):
            best_col = 0
            best_conflicts = float('inf')
            
            for col in range(n):
                # Vérifier si la colonne est disponible
                if any(placement[r] == col for r in range(row)):
                    continue
                
                # Compter les conflits potentiels
                temp_placement = placement.copy()
                temp_placement[row] = col
                conflicts = 0
                
                # Conflits avec les reines placées
                for prev_row in range(row):
                    if abs(col - placement[prev_row]) == abs(row - prev_row):
                        conflicts += 1
                
                if conflicts < best_conflicts:
                    best_conflicts = conflicts
                    best_col = col
            
            placement[row] = best_col
        
        return placement
    
    def local_search_improve(self, placement: List[int], max_iters: int = 500) -> List[int]:
        """
        Amélioration par recherche locale (permutations aléatoires et réarrangements).
        """
        n = len(placement)
        best_placement = placement.copy()
        best_conflicts = self.count_conflicts(best_placement)
        stall_count = 0
        
        for iteration in range(max_iters):
            if best_conflicts == 0:
                break
            
            # Stratégie 1 : Permutation simple (70%)
            if random.random() < 0.7:
                i, j = random.sample(range(n), 2)
                temp_placement = best_placement.copy()
                temp_placement[i], temp_placement[j] = temp_placement[j], temp_placement[i]
            else:
                # Stratégie 2 : Réassigner une ligne complètement (30%)
                row = random.randint(0, n - 1)
                temp_placement = best_placement.copy()
                # Essayer toutes les colonnes et prendre la meilleure
                best_col_for_row = 0
                best_score = float('inf')
                for col in range(n):
                    temp_placement[row] = col
                    score = self.count_conflicts(temp_placement)
                    if score < best_score:
                        best_score = score
                        best_col_for_row = col
                temp_placement[row] = best_col_for_row
            
            conflicts = self.count_conflicts(temp_placement)
            if conflicts < best_conflicts:
                best_conflicts = conflicts
                best_placement = temp_placement.copy()
                stall_count = 0
            else:
                stall_count += 1
                # Accepter occasionnellement de mauvaises solutions (simulated annealing)
                if random.random() < 0.05 * (1 - iteration / max_iters):
                    best_placement = temp_placement.copy()
                    best_conflicts = conflicts
                    stall_count = 0
        
        return best_placement
    
    def solve(self, n: int, num_attempts: int = 10) -> tuple:
        """
        Résout le problème des N-Reines via glouton + recherche locale multi-tentatives.
        
        Args:
            n: Taille de la grille (n x n)
            num_attempts: Nombre de tentatives avec différentes graines aléatoires
        
        Returns:
            (solution, conflicts) où solution est [[row, col], ...] et conflicts le nombre de conflits
        """
        best_placement = None
        best_conflicts = float('inf')
        
        for attempt in range(num_attempts):
            placement = self.greedy_place(n)
            placement = self.local_search_improve(placement, max_iters=500)
            
            conflicts = self.count_conflicts(placement)
            if conflicts < best_conflicts:
                best_conflicts = conflicts
                best_placement = placement.copy()
            
            if best_conflicts == 0:
                break
        
        solution = [[i, best_placement[i]] for i in range(n)]
        
        return solution, best_conflicts
